#!/usr/bin/env python3
"""Test that models can be imported successfully"""

try:
    from app.models import User, APIKey, IdentityVerification, AuditLog
    print("✅ All models imported successfully!")
    print(f"User model table: {User.__tablename__}")
    print(f"APIKey model table: {APIKey.__tablename__}")
    print(f"IdentityVerification model table: {IdentityVerification.__tablename__}")
    print(f"AuditLog model table: {AuditLog.__tablename__}")
    print("\nAll security models are properly exported!")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
