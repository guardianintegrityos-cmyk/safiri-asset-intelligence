"""
Security-First Configuration for Safiri Asset Intelligence
Guardian Academy - Financial-Grade Security Architecture
"""

import os
from datetime import timedelta
from pydantic_settings import BaseSettings


class SecurityConfig(BaseSettings):
    """
    Production-level security configuration aligned with financial-grade standards
    Assumes zero-trust model: no request is trusted by default
    """
    
    # ============================================
    # CORE SECURITY SETTINGS
    # ============================================
    
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRATION_DAYS: int = 7
    
    # API Key Security
    API_KEY_PREFIX: str = "safiri_"
    API_KEY_LENGTH: int = 32
    API_KEYS_ENABLED: bool = True
    
    # Password Hashing
    PASSWORD_MIN_LENGTH: int = 12
    BCRYPT_ROUNDS: int = 12
    
    # ============================================
    # RATE LIMITING & ANTI-SCRAPING
    # ============================================
    
    # Global rate limits
    RATE_LIMIT_SEARCHES_PER_HOUR: int = 10
    RATE_LIMIT_SEARCHES_PER_DAY: int = 50
    RATE_LIMIT_IDENTITY_QUERIES_PER_HOUR: int = 5
    RATE_LIMIT_CLAIMS_PER_HOUR: int = 3
    
    # Temporary blocking
    TEMP_BLOCK_DURATION_MINUTES: int = 60
    TEMP_BLOCK_THRESHOLD: int = 3  # consecutive violations
    
    # ============================================
    # FRAUD DETECTION THRESHOLDS
    # ============================================
    
    FRAUD_SEARCH_LIMIT_PER_HOUR: int = 20
    FRAUD_CLAIMS_FROM_SAME_IP: int = 3
    FRAUD_DEVICE_FINGERPRINT_THRESHOLD: float = 0.9
    FRAUD_BEHAVIOR_ANOMALY_THRESHOLD: float = 0.75
    
    # Identity verification confidence thresholds
    IDENTITY_VERIFICATION_THRESHOLD_LOW: float = 0.6
    IDENTITY_VERIFICATION_THRESHOLD_MEDIUM: float = 0.8
    IDENTITY_VERIFICATION_THRESHOLD_HIGH: float = 0.95
    
    # ============================================
    # DATA MASKING & PRIVACY
    # ============================================
    
    # Enable data masking in API responses
    MASK_SENSITIVE_DATA: bool = True
    
    # Masking strategy
    MASK_FULL_NAME_MODE: str = "partial"  # "partial" or "full"
    MASK_ID_NUMBER_MODE: str = "last_4"  # "last_4" or "last_2"
    MASK_PHONE_MODE: str = "last_4"
    MASK_EMAIL_MODE: str = "domain_only"
    
    # ============================================
    # ENCRYPTION & HASHING
    # ============================================
    
    # Encryption for sensitive fields in database
    ENCRYPT_NATIONAL_IDS: bool = True
    ENCRYPT_PHONE_NUMBERS: bool = True
    ENCRYPT_DOCUMENTS: bool = True
    ENCRYPTION_ALGORITHM: str = "fernet"  # symmetric encryption
    
    # Hash algorithm for PII (one-way, for deduplication)
    HASH_ALGORITHM: str = "sha256"
    
    # ============================================
    # AUDIT LOGGING
    # ============================================
    
    AUDIT_LOG_ENABLED: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 90
    
    # Events to audit
    AUDIT_IDENTITY_QUERIES: bool = True
    AUDIT_ASSET_CLAIMS: bool = True
    AUDIT_DOCUMENT_UPLOADS: bool = True
    AUDIT_ADMIN_ACTIONS: bool = True
    AUDIT_FAILED_AUTHENTICATIONS: bool = True
    
    # ============================================
    # IDENTITY VERIFICATION PIPELINE
    # ============================================
    
    # Verification stages (multiple factors required)
    REQUIRE_EMAIL_VERIFICATION: bool = True
    REQUIRE_PHONE_OTP: bool = True
    REQUIRE_IDENTITY_DOCUMENT: bool = True
    REQUIRE_SELFIE_CAPTURE: bool = True
    REQUIRE_PROOF_OF_OWNERSHIP: bool = True
    
    # OTP Configuration
    OTP_LENGTH: int = 6
    OTP_EXPIRATION_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 3
    
    # ============================================
    # DOCUMENT VALIDATION
    # ============================================
    
    VALIDATE_DOCUMENT_METADATA: bool = True
    DETECT_DOCUMENT_FORGERY: bool = True
    MAX_DOCUMENT_SIZE_MB: int = 10
    ALLOWED_DOCUMENT_FORMATS: list = ["pdf", "jpg", "jpeg", "png"]
    
    # ============================================
    # GUARDIAN INTEGRITY OVERSIGHT
    # ============================================
    
    # Integrity scoring
    INTEGRITY_SCORE_MIN: float = 0.0
    INTEGRITY_SCORE_MAX: float = 1.0
    
    # Classification levels
    CLAIM_LEVEL_1_THRESHOLD: float = 0.8  # auto-approve
    CLAIM_LEVEL_2_THRESHOLD: float = 0.6  # AI + human review
    CLAIM_LEVEL_3_THRESHOLD: float = 0.0  # institutional verification
    
    # Institutional oversight
    INSTITUTIONAL_VERIFICATION_REQUIRED: bool = True
    APPEAL_PROCESS_ENABLED: bool = True
    
    # ============================================
    # INFRASTRUCTURE & DEPLOYMENT
    # ============================================
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        os.getenv("FRONTEND_URL", "https://safiri.guardian-academy.org")
    ]
    
    # HTTPS enforcement
    ENFORCE_HTTPS: bool = True
    HSTS_MAX_AGE: int = 31536000  # 1 year
    
    # Security headers
    ENABLE_SECURITY_HEADERS: bool = True
    X_CONTENT_TYPE_OPTIONS: str = "nosniff"
    X_FRAME_OPTIONS: str = "DENY"
    X_XSS_PROTECTION: str = "1; mode=block"
    
    # ============================================
    # DATABASE SECURITY
    # ============================================
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost/safiri_db"
    )
    DATABASE_SSL_MODE: str = os.getenv("DATABASE_SSL_MODE", "require")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_POOL_RECYCLE: int = 3600  # 1 hour
    
    # Neo4j
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    
    # ============================================
    # LOGGING & MONITORING
    # ============================================
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "json"  # structured logging
    
    # ============================================
    # THIRD-PARTY INTEGRATIONS
    # ============================================
    
    # Cloudflare WAF
    CLOUDFLARE_ENABLED: bool = True
    CLOUDFLARE_API_KEY: str = os.getenv("CLOUDFLARE_API_KEY", "")
    CLOUDFLARE_ZONE_ID: str = os.getenv("CLOUDFLARE_ZONE_ID", "")
    
    # Twilio for OTP
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Email Service Configuration (optional)
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "noreply@safiri.org")
    
    # Environment Type
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Frontend URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Allow extra fields (ignore them)


# Global security configuration instance
security_config = SecurityConfig()

