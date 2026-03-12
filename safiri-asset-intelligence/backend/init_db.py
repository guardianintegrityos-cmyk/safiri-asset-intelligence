#!/usr/bin/env python3
"""Initialize database and create test user for SECURITY_QUICKSTART.md"""

import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Initializing Safiri Security Database...\n")

try:
    # Import database components
    from app.config import security_config
    from app.models import Base, User
    from app.security.encryption import hash_manager
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Get database URL from config
    database_url = security_config.DATABASE_URL
    print(f"Database URL: {database_url}")
    
    # Create engine
    engine = create_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
    )
    
    # Create all tables
    print("\nCreating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            print(f"\nTest user 'testuser' already exists (ID: {existing_user.user_id})")
            print(f"  Email: {existing_user.email}")
            print(f"  Created: {existing_user.created_at}")
        else:
            # Create test user
            print("\nCreating test user...")
            password = "TestPassword123!"
            password_hash = hash_manager.hash_password(password)
            
            test_user = User(
                username="testuser",
                email="testuser@safiri.local",
                password_hash=password_hash,
                full_name="Test User",
                role="user",
                is_active=True,
                is_verified=True,
                verification_level=3,
                two_factor_enabled=False,
                terms_accepted=True,
                privacy_policy_accepted=True,
                created_at=datetime.utcnow(),
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            print(f"✅ Test user created successfully!")
            print(f"  User ID: {test_user.user_id}")
            print(f"  Username: {test_user.username}")
            print(f"  Email: {test_user.email}")
            print(f"  Password: {password}")
            print(f"  Role: {test_user.role}")
    
    finally:
        db.close()
    
    print("\n" + "="*50)
    print("DATABASE INITIALIZATION COMPLETE")
    print("="*50)
    print("\nTest User Credentials:")
    print("  Username: testuser")
    print("  Password: TestPassword123!")
    print("  Email: testuser@safiri.local")
    print("\nUse these credentials to test /auth/login endpoint")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
