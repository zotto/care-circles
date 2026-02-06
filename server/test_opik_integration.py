"""
Test Opik integration

Simple script to verify that Opik is properly configured and traces are being sent.
"""

import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 80)
print("Testing Opik Integration")
print("=" * 80)

# Test 1: Check if Opik is installed
print("\n1. Checking if Opik is installed...")
try:
    import opik
    print("   ✅ Opik is installed")
    print(f"   Version: {opik.__version__ if hasattr(opik, '__version__') else 'unknown'}")
except ImportError as e:
    print(f"   ❌ Opik is NOT installed: {e}")
    print("   Run: pip install opik>=0.2.0")
    exit(1)

# Test 2: Check configuration
print("\n2. Checking Opik configuration...")
try:
    from app.config.settings import settings
    
    if settings.OPIK_API_KEY:
        print(f"   ✅ OPIK_API_KEY is set (length: {len(settings.OPIK_API_KEY)})")
    else:
        print("   ❌ OPIK_API_KEY is not set")
        print("   Add to .env: OPIK_API_KEY=your_key")
    
    print(f"   Workspace: {settings.OPIK_WORKSPACE}")
    print(f"   Project: {settings.OPIK_PROJECT_NAME}")
    
except Exception as e:
    print(f"   ❌ Configuration error: {e}")
    exit(1)

# Test 3: Initialize Opik client
print("\n3. Initializing Opik client...")
try:
    from app.observability.opik_client import opik_client
    
    if opik_client.is_enabled():
        print("   ✅ Opik client is enabled and ready")
    else:
        print("   ❌ Opik client is disabled")
        print("   Check your API key and configuration")
        exit(1)
        
except Exception as e:
    print(f"   ❌ Client initialization error: {e}")
    exit(1)

# Test 4: Send a test trace
print("\n4. Sending test trace to Opik...")
try:
    from app.observability.opik_tracker import log_to_opik
    
    log_to_opik(
        name="TEST_opik_integration",
        input_data={
            "test": "This is a test trace",
            "timestamp": datetime.utcnow().isoformat()
        },
        output_data={
            "status": "success",
            "message": "Opik integration is working!"
        },
        metadata={
            "test_type": "integration_test",
            "success": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    print("   ✅ Test trace sent successfully")
    print("   Check your Opik dashboard at: https://www.comet.com/opik")
    print(f"   Project: {settings.OPIK_PROJECT_NAME}")
    
except Exception as e:
    print(f"   ❌ Failed to send test trace: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 5: Verify tracker module
print("\n5. Verifying tracker module...")
try:
    from app.observability.opik_tracker import configure_opik, track_agent
    print("   ✅ Tracker module loaded successfully")
except Exception as e:
    print(f"   ❌ Tracker module error: {e}")
    exit(1)

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED!")
print("=" * 80)
print("\nNext steps:")
print("1. Check your Opik dashboard: https://www.comet.com/opik")
print("2. Look for the 'TEST_opik_integration' trace")
print("3. Run the demo: python demo_observability.py")
print("4. View agent traces in your dashboard")
print()
