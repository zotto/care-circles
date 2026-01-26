"""
Application settings and configuration

Uses Pydantic Settings for environment variable management and validation.
Settings can be configured via environment variables or .env file.
"""

from typing import List, Union, Annotated
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, BeforeValidator
import json


def _parse_cors_origins(v: Union[str, List[str]]) -> List[str]:
    """Parse CORS_ORIGINS from comma-separated string or JSON array"""
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        # Try JSON first
        try:
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        # Fall back to comma-separated string
        if v.strip():
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return []
    return v if isinstance(v, list) else []


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file
    """
    
    # API Configuration
    API_TITLE: str = "Care Circles API"
    API_VERSION: str = "0.1.0"
    API_DESCRIPTION: str = "AI-assisted caregiving coordination system"
    API_PORT: int = 8000
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key for LLM")
    OPENAI_MODEL: str = Field(default="gpt-4", description="OpenAI model to use")
    
    # CORS Configuration
    CORS_ORIGINS: Annotated[List[str], BeforeValidator(_parse_cors_origins)] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins (comma-separated string or JSON array)"
    )
    
    # Supabase Configuration
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_ANON_KEY: str = Field(..., description="Supabase anon key")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., description="Supabase service role key (for server-side operations)")
    SUPABASE_JWT_SECRET: str = Field(..., description="Supabase JWT secret for token verification")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


# Global settings instance
settings = Settings()
