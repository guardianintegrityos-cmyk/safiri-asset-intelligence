"""
Encryption and Hashing Utilities for Safiri Asset Intelligence
Handles sensitive data encryption, decryption, and secure hashing
"""

import hashlib
import os
from cryptography.fernet import Fernet
import base64
from app.config import security_config


class EncryptionManager:
    """
    Manages encryption and decryption of sensitive data
    Uses Fernet (symmetric encryption with AES-128)
    """
    
    def __init__(self):
        """Initialize encryption with environment-based key"""
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if not encryption_key:
            # Generate a new key if not provided
            encryption_key = Fernet.generate_key().decode()
            print("⚠️  WARNING: No ENCRYPTION_KEY set. Generated temporary key.")
            print("Set ENCRYPTION_KEY in .env for production")
        
        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string
        
        Args:
            plaintext: String to encrypt (e.g., national ID, phone number)
            
        Returns:
            Encrypted string (base64 encoded)
        """
        if not plaintext:
            return None
        
        try:
            encrypted = self.cipher.encrypt(plaintext.encode())
            return encrypted.decode()
        except Exception as e:
            print(f"Encryption error: {e}")
            raise
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt encrypted string
        
        Args:
            encrypted_text: Encrypted string to decrypt
            
        Returns:
            Decrypted plaintext string
        """
        if not encrypted_text:
            return None
        
        try:
            decrypted = self.cipher.decrypt(encrypted_text.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            raise


class HashManager:
    """
    Manages one-way hashing for PII
    Used for deduplication and fraud detection without storing actual values
    """
    
    @staticmethod
    def hash_pii(data: str, salt: str = "safiri") -> str:
        """
        Create secure hash of personally identifiable information
        One-way function (cannot be reversed)
        
        Args:
            data: PII to hash (name, ID, phone, email)
            salt: Salt for additional security
            
        Returns:
            Hex-encoded hash string
        """
        if not data:
            return None
        
        # Normalize data
        normalized = str(data).strip().lower()
        
        # Create hash with salt
        combined = f"{salt}{normalized}"
        hash_obj = hashlib.sha256(combined.encode())
        return hash_obj.hexdigest()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt for authentication
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password (bcrypt)
        """
        try:
            import bcrypt
            salt = bcrypt.gensalt(rounds=security_config.BCRYPT_ROUNDS)
            hashed = bcrypt.hashpw(password.encode(), salt)
            return hashed.decode()
        except ImportError:
            print("bcrypt not installed. Using SHA256 fallback (NOT RECOMMENDED for production)")
            return HashManager.hash_pii(password)
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password to verify
            hashed: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except ImportError:
            # Fallback comparison
            return HashManager.hash_pii(password) == hashed


# Global encryption instances
encryption_manager = EncryptionManager()
hash_manager = HashManager()


def encrypt_national_id(national_id: str) -> str:
    """Encrypt national ID number"""
    if not security_config.ENCRYPT_NATIONAL_IDS:
        return national_id
    return encryption_manager.encrypt(national_id)


def decrypt_national_id(encrypted_id: str) -> str:
    """Decrypt national ID number"""
    if not security_config.ENCRYPT_NATIONAL_IDS:
        return encrypted_id
    return encryption_manager.decrypt(encrypted_id)


def encrypt_phone(phone: str) -> str:
    """Encrypt phone number"""
    if not security_config.ENCRYPT_PHONE_NUMBERS:
        return phone
    return encryption_manager.encrypt(phone)


def decrypt_phone(encrypted_phone: str) -> str:
    """Decrypt phone number"""
    if not security_config.ENCRYPT_PHONE_NUMBERS:
        return encrypted_phone
    return encryption_manager.decrypt(encrypted_phone)
