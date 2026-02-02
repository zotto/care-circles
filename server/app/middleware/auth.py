"""
Authentication Middleware

JWT token validation and user extraction for protected routes.
"""

import logging
import time
from typing import Optional
from functools import lru_cache
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives import serialization
import httpx
import base64

from app.config.settings import settings
from app.config.constants import AuthConstants

logger = logging.getLogger(__name__)

# HTTP Bearer security scheme
security = HTTPBearer()

# Cache for JWKS (JSON Web Key Set)
_jwks_cache: Optional[dict] = None
_jwks_cache_time: Optional[float] = None
JWKS_CACHE_TTL = 3600  # Cache JWKS for 1 hour


@lru_cache(maxsize=1)
def get_jwks_url() -> str:
    """Get the JWKS URL from Supabase settings"""
    base_url = settings.SUPABASE_URL.rstrip('/')
    return f"{base_url}/auth/v1/.well-known/jwks.json"


async def fetch_jwks() -> dict:
    """
    Fetch JWKS (JSON Web Key Set) from Supabase
    
    Returns:
        dict: JWKS containing public keys for token verification
        
    Raises:
        HTTPException: If JWKS cannot be fetched
    """
    global _jwks_cache, _jwks_cache_time

    # Return cached JWKS if still valid
    if _jwks_cache and _jwks_cache_time:
        if time.time() - _jwks_cache_time < JWKS_CACHE_TTL:
            return _jwks_cache
    
    try:
        jwks_url = get_jwks_url()
        logger.info(f"Fetching JWKS from: {jwks_url}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            jwks = response.json()
            
            # Cache the JWKS
            _jwks_cache = jwks
            _jwks_cache_time = time.time()
            
            logger.info(f"Successfully fetched JWKS with {len(jwks.get('keys', []))} keys")
            return jwks
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify authentication token: JWKS unavailable",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_public_key_from_jwks(jwks: dict, kid: str) -> Optional[dict]:
    """
    Get the public key from JWKS for a given key ID
    
    Args:
        jwks: JSON Web Key Set
        kid: Key ID from JWT header
        
    Returns:
        dict: Public key information (JWK) or None if not found
    """
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    return None


def jwk_to_public_key(jwk: dict):
    """
    Convert JWK (JSON Web Key) to a cryptography public key object
    
    Args:
        jwk: JSON Web Key dictionary
        
    Returns:
        Public key object (EC or RSA) that can be used for JWT verification
    """
    kty = jwk.get("kty")  # Key type: EC or RSA
    
    if kty == "EC":
        # Elliptic Curve key (ES256)
        curve_map = {
            "P-256": ec.SECP256R1(),
            "P-384": ec.SECP384R1(),
            "P-521": ec.SECP521R1(),
        }
        curve_name = jwk.get("crv", "P-256")
        curve = curve_map.get(curve_name)
        
        if not curve:
            raise ValueError(f"Unsupported EC curve: {curve_name}")
        
        # JWK x and y are base64url-encoded strings
        # Use urlsafe_b64decode which handles base64url properly
        x_str = jwk["x"]
        y_str = jwk["y"]
        
        # Add padding if needed
        def add_padding(s):
            return s + '=' * (4 - len(s) % 4) if len(s) % 4 else s
        
        x_bytes = base64.urlsafe_b64decode(add_padding(x_str))
        y_bytes = base64.urlsafe_b64decode(add_padding(y_str))
        
        # Convert bytes to integers (big-endian)
        x_int = int.from_bytes(x_bytes, "big")
        y_int = int.from_bytes(y_bytes, "big")
        
        public_numbers = ec.EllipticCurvePublicNumbers(
            x_int,
            y_int,
            curve
        )
        return public_numbers.public_key()
        
    elif kty == "RSA":
        # RSA key (RS256)
        # JWK n and e are base64url-encoded strings
        def add_padding(s):
            return s + '=' * (4 - len(s) % 4) if len(s) % 4 else s
        
        n_str = jwk["n"]
        e_str = jwk["e"]
        
        n_bytes = base64.urlsafe_b64decode(add_padding(n_str))
        e_bytes = base64.urlsafe_b64decode(add_padding(e_str))
        
        # Convert bytes to integers (big-endian)
        n_int = int.from_bytes(n_bytes, "big")
        e_int = int.from_bytes(e_bytes, "big")
        
        public_numbers = rsa.RSAPublicNumbers(
            e_int,
            n_int
        )
        return public_numbers.public_key()
    
    else:
        raise ValueError(f"Unsupported key type: {kty}")


class AuthUser:
    """Authenticated user context"""
    
    def __init__(self, user_id: str, email: str, token: str):
        self.user_id = user_id
        self.email = email
        self.token = token
    
    def __repr__(self):
        return f"AuthUser(user_id={self.user_id}, email={self.email})"


async def verify_jwt_token(token: str) -> dict:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT access token
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # First, decode the header to see what algorithm is being used
        unverified_header = jwt.get_unverified_header(token)
        algorithm = unverified_header.get("alg", "HS256")
        kid = unverified_header.get("kid")  # Key ID for ES256/RS256
        
        logger.info(f"JWT token algorithm: {algorithm}, kid: {kid}")
        
        # Handle different algorithms
        if algorithm == "HS256":
            # HS256 uses symmetric key (JWT secret)
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": False  # Supabase uses different audiences
                }
            )
            return payload
            
        elif algorithm in ["ES256", "RS256"]:
            # ES256/RS256 use asymmetric keys (public key from JWKS)
            if not kid:
                logger.error(f"Missing 'kid' in token header for {algorithm} algorithm")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing key identifier",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Fetch JWKS and get the public key
            jwks = await fetch_jwks()
            jwk = get_public_key_from_jwks(jwks, kid)
            
            if not jwk:
                logger.error(f"Key ID '{kid}' not found in JWKS")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: key not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Convert JWK to cryptography public key object
            try:
                public_key = jwk_to_public_key(jwk)
                
                # Serialize the public key to PEM format for python-jose
                pem_key = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                logger.debug(f"Successfully converted JWK to PEM format for algorithm {algorithm}")
                
                # Decode the token with the public key
                payload = jwt.decode(
                    token,
                    pem_key,
                    algorithms=[algorithm],
                    options={
                        "verify_signature": True,
                        "verify_exp": True,
                        "verify_aud": False
                    }
                )
                logger.info(f"Successfully verified JWT token with {algorithm}")
                return payload
            except JWTError as jwt_err:
                logger.error(f"JWT verification failed with {algorithm}: {str(jwt_err)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: signature verification failed",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except Exception as key_error:
                logger.error(f"Failed to process public key: {str(key_error)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: key processing failed",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
        else:
            logger.error(f"Unsupported JWT algorithm: {algorithm}. Supported: HS256, RS256, ES256")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unsupported token algorithm: {algorithm}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    except JWTError as e:
        error_msg = str(e)
        logger.warning(f"JWT verification failed: {error_msg}")
        
        # Log the token header for debugging
        try:
            header = jwt.get_unverified_header(token)
            logger.error(f"JWT token header: {header}")
        except Exception as header_error:
            logger.error(f"Could not decode token header: {header_error}")
        
        # Provide more specific error messages
        if "alg" in error_msg.lower() or "algorithm" in error_msg.lower():
            logger.error(f"JWT algorithm mismatch. Error: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token: algorithm mismatch",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif "exp" in error_msg.lower() or "expired" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        # Catch any other exceptions (like HTTPException from algorithm check)
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Unexpected error verifying JWT: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def extract_user_from_token(payload: dict) -> AuthUser:
    """
    Extract user information from decoded token payload
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        AuthUser: Authenticated user context
        
    Raises:
        HTTPException: If required fields are missing
    """
    user_id = payload.get("sub")
    email = payload.get("email")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
        )
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing email",
        )
    
    return AuthUser(
        user_id=user_id,
        email=email,
        token=payload.get("token", "")
    )


# In-memory cache: user_id -> timestamp of last "ensure user exists".
# Skip GET+PATCH to Supabase when we've done it recently (per process, safe TTL).
_user_ensure_cache: dict[str, float] = {}
USER_ENSURE_CACHE_TTL = 300  # seconds; ensure user at most once per 5 min per process


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthUser:
    """
    FastAPI dependency to get current authenticated user
    
    Ensures the user exists in the database by creating/updating their record.
    This is cached per user for a short TTL to avoid GET+PATCH on every request.
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: AuthUser = Depends(get_current_user)):
            return {"user_id": user.user_id}
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        AuthUser: Authenticated user context
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = await verify_jwt_token(token)
    user = extract_user_from_token(payload)
    
    # Ensure user exists in database (upsert), but skip if we did it recently
    now = time.time()
    if user.user_id in _user_ensure_cache and (now - _user_ensure_cache[user.user_id]) < USER_ENSURE_CACHE_TTL:
        logger.debug(f"Using cached user-ensure for {user.user_id}")
    else:
        try:
            from app.db import get_service_client
            from app.db.repositories.user_repository import UserRepository

            db = get_service_client()
            user_repo = UserRepository(db)

            full_name = payload.get("user_metadata", {}).get("full_name")
            if not full_name:
                full_name = user.email.split("@")[0]

            user_repo.create_or_update(
                user_id=user.user_id,
                email=user.email,
                full_name=full_name
            )
            _user_ensure_cache[user.user_id] = now
            logger.debug(f"Ensured user record exists for {user.user_id}")
        except Exception as e:
            logger.error(f"Failed to ensure user exists in database: {str(e)}", exc_info=True)
            # Don't fail authentication; user is still authenticated

    logger.debug(f"Authenticated user: {user}")
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[AuthUser]:
    """
    FastAPI dependency to get current user if authenticated (optional)
    
    Use this for routes that can work with or without authentication.
    
    Args:
        credentials: HTTP Authorization credentials (optional)
        
    Returns:
        Optional[AuthUser]: Authenticated user context or None
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = await verify_jwt_token(token)
        user = extract_user_from_token(payload)
        return user
    except HTTPException:
        # If token is invalid, treat as unauthenticated
        return None
