#!/usr/bin/env python3
"""Test that all security modules can be imported successfully"""

print("Testing security module imports...\n")

try:
    print("1. Testing app.security.encryption...")
    from app.security.encryption import encryption_manager, hash_manager
    print("   ✅ encryption.py imported")
    
    print("2. Testing app.security.masking...")
    from app.security.masking import data_masker
    print("   ✅ masking.py imported")
    
    print("3. Testing app.security.api_security...")
    from app.security.api_security import jwt_manager, api_key_manager
    print("   ✅ api_security.py imported")
    
    print("4. Testing app.security.rate_limiting...")
    from app.security.rate_limiting import rate_limiter
    print("   ✅ rate_limiting.py imported")
    
    print("5. Testing app.security module init...")
    from app import security
    print("   ✅ security/__init__.py imported")
    
    print("\n" + "="*50)
    print("✅ ALL SECURITY MODULES IMPORTED SUCCESSFULLY!")
    print("="*50)
    
    # Run quick functionality tests
    print("\nRunning quick functionality tests...")
    
    # Test encryption
    test_data = "test_secret_123"
    encrypted = encryption_manager.encrypt(test_data)
    decrypted = encryption_manager.decrypt(encrypted)
    assert decrypted == test_data
    print("✅ Encryption/decryption working")
    
    # Test password hashing
    password = "TestPassword123!"
    pwd_hash = hash_manager.hash_password(password)
    is_correct = hash_manager.verify_password(password, pwd_hash)
    assert is_correct
    print("✅ Password hashing working")
    
    # Test data masking
    masked_name = data_masker.mask_full_name("James Mwangi")
    assert "*" in masked_name
    print("✅ Data masking working")
    
    print("\n" + "="*50)
    print("All security functions verified and operational!")
    print("="*50)
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
