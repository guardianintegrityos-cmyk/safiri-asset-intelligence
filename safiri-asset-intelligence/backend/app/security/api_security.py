"""
API Security Layer - JWT & API Key Management
Handles authentication, authorization, and service-to-service security
Zero-trust model: every request must authenticate
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
from sqlalchemy.orm import Session
from app.models import User, APIKey
from app.config import security_config
from app.security.encryption import hash_manager


class JWTManager:
    """
    JWT token generation and verification
    Used for user authentication and session management
    """
    
    @staticmethod
    def generate_token(
        user_id: int,
        username: str,
        role: str = "user",
        expires_in_minutes: Optional[int] = None
    ) -> str:
        """
        Generate JWT token for authenticated user
        
        Args:
            user_id: User ID
            username: Username
            role: User role (user, admin, institution, guardian)
            expires_in_minutes: Token expiration (default: config value)
            
        Returns:
            JWT token string
        """
        import jwt
        from datetime import datetime, timedelta
        
        expires_in = expires_in_minutes or security_config.JWT_EXPIRATION_MINUTES
        
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=expires_in)
        }
        
        token = jwt.encode(
            payload,
            security_config.SECRET_KEY,
            algorithm=security_config.JWT_ALGORITHM
        )
        
        return token
    
    @staticmethod
    def verify_token(token: str) -> Tuple[bool, Optional[Dict]]:
        """
        Verify JWT token validity
        
        Args:
            token: JWT token to verify
            
        Returns:
            Tuple of (is_valid, decoded_payload)
        """
        import jwt
        
        try:
            payload = jwt.decode(
                token,
                security_config.SECRET_KEY,
                algorithms=[security_config.JWT_ALGORITHM]
            )
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, None
        except jwt.InvalidTokenError:
            return False, None
    
    @staticmethod
    def generate_refresh_token(user_id: int) -> str:
        """
        Generate long-lived refresh token
        
        Args:
            user_id: User ID
            
        Returns:
            Refresh token string
        """
        import jwt
        
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=security_config.REFRESH_TOKEN_EXPIRATION_DAYS)
        }
        
        token = jwt.encode(
            payload,
            security_config.SECRET_KEY,
            algorithm=security_config.JWT_ALGORITHM
        )
        
        return token


class APIKeyManager:
    """
    API key generation, validation, and revocation
    Used for service-to-service authentication
    Each service gets unique key with specific scopes
    """
    
    @staticmethod
    def generate_api_key(
        user_id: int,
        key_name: str,
        scopes: list = None,
        db: Session = None
    ) -> Tuple[str, APIKey]:
        """
        Generate new API key
        
        Args:
            user_id: User ID (typically a service account)
            key_name: Friendly name for the key
            scopes: Allowed scopes (default: read)
            db: Database session
            
        Returns:
            Tuple of (raw_key, APIKey_object)
        """
        if not scopes:
            scopes = ["read"]
        
        # Generate random key
        raw_key = f"{security_config.API_KEY_PREFIX}{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        # Create database record
        api_key = APIKey(
            user_id=user_id,
            key_name=key_name,
            key_hash=key_hash,
            scopes=scopes,
            is_active=True
        )
        
        if db:
            db.add(api_key)
            db.commit()
        
        return raw_key, api_key
    
    @staticmethod
    def validate_api_key(
        raw_key: str,
        db: Session = None
    ) -> Tuple[bool, Optional[APIKey], str]:
        """
        Validate API key
        
        Args:
            raw_key: API key to validate
            db: Database session
            
        Returns:
            Tuple of (is_valid, APIKey_object, message)
        """
        if not db:
            return False, None, "Database session required"
        
        # Hash the provided key
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        # Look up in database
        api_key = db.query(APIKey).filter(
            APIKey.key_hash == key_hash
        ).first()
        
        if not api_key:
            return False, None, "Invalid API key"
        
        # Check if active
        if not api_key.is_active:
            return False, None, "API key is revoked"
        
        # Check expiration
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return False, None, "API key expired"
        
        # Check rate limit
        today = datetime.utcnow().date()
        if api_key.requests_today >= api_key.requests_limit:
            return False, None, "Rate limit exceeded for today"
        
        # Check IP whitelist
        if api_key.ip_whitelist:
            # IP whitelist check would be done by caller
            pass
        
        # Update last used
        api_key.last_used_at = datetime.utcnow()
        api_key.requests_today += 1
        db.commit()
        
        return True, api_key, "Valid"
    
    @staticmethod
    def revoke_api_key(key_id: int, db: Session = None) -> bool:
        """
        Revoke API key (permanent)
        
        Args:
            key_id: API key ID
            db: Database session
            
        Returns:
            Success flag
        """
        if not db:
            return False
        
        api_key = db.query(APIKey).filter(APIKey.key_id == key_id).first()
        
        if api_key:
            api_key.is_active = False
            api_key.revoked_at = datetime.utcnow()
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def rotate_api_key(
        key_id: int,
        db: Session = None
    ) -> Tuple[Optional[str], Optional[APIKey]]:
        """
        Rotate (replace) API key with new one
        
        Args:
            key_id: API key ID to rotate
            db: Database session
            
        Returns:
            Tuple of (new_raw_key, new_APIKey_object)
        """
        if not db:
            return None, None
        
        # Get original key
        old_key = db.query(APIKey).filter(APIKey.key_id == key_id).first()
        
        if not old_key:
            return None, None
        
        # Revoke old key
        APIKeyManager.revoke_api_key(key_id, db)
        
        # Generate new key
        new_raw_key, new_key = APIKeyManager.generate_api_key(
            user_id=old_key.user_id,
            key_name=f"{old_key.key_name} (rotated)",
            scopes=old_key.scopes,
            db=db
        )
        
        return new_raw_key, new_key


class AuthenticationService:
    """
    Manages user authentication and password security
    """
    
    @staticmethod
    def authenticate_user(
        username: str,
        password: str,
        ip_address: str,
        db: Session = None
    ) -> Tuple[bool, Optional[Tuple[str, str]], Optional[str]]:
        """
        Authenticate user with username and password
        
        Args:
            username: Username or email
            password: Password (plaintext - will be hashed and compared)
            ip_address: Client IP address
            db: Database session
            
        Returns:
            Tuple of (success, (access_token, refresh_token), error_message)
        """
        if not db:
            return False, None, "Database session required"
        
        # Find user
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            return False, None, "Invalid username or password"
        
        # Check if user is locked (too many failed attempts)
        if user.locked_until and user.locked_until > datetime.utcnow():
            return False, None, f"Account temporarily locked until {user.locked_until}"
        
        # Verify password
        password_valid = hash_manager.verify_password(password, user.password_hash)
        
        if not password_valid:
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(hours=1)
            
            db.commit()
            return False, None, "Invalid username or password"
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        # Generate tokens
        access_token = JWTManager.generate_token(user.user_id, user.username, user.role)
        refresh_token = JWTManager.generate_refresh_token(user.user_id)
        
        return True, (access_token, refresh_token), None
    
    @staticmethod
    def change_password(
        user_id: int,
        old_password: str,
        new_password: str,
        db: Session = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Change user password
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            db: Database session
            
        Returns:
            Tuple of (success, error_message)
        """
        if not db:
            return False, "Database session required"
        
        # Validate password length
        if len(new_password) < security_config.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {security_config.PASSWORD_MIN_LENGTH} characters"
        
        # Get user
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            return False, "User not found"
        
        # Verify old password
        if not hash_manager.verify_password(old_password, user.password_hash):
            return False, "Current password is incorrect"
        
        # Set new password
        user.password_hash = hash_manager.hash_password(new_password)
        user.last_password_change = datetime.utcnow()
        db.commit()
        
        return True, None


# Global instances
jwt_manager = JWTManager()
api_key_manager = APIKeyManager()
authentication_service = AuthenticationService()
