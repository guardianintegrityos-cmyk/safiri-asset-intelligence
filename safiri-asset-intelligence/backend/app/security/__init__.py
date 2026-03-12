"""
Safiri Asset Intelligence - Security Module
Production-level financial-grade security architecture
Guardian Academy Security Framework
"""

# Core encryption and hashing
from app.security.encryption import (
    encryption_manager,
    hash_manager,
    encrypt_national_id,
    decrypt_national_id,
    encrypt_phone,
    decrypt_phone
)

# Data masking
from app.security.masking import (
    data_masker,
    DataMasker,
    MaskedIdentity,
    MaskedAsset
)

# API Security
from app.security.api_security import (
    jwt_manager,
    api_key_manager,
    authentication_service,
    JWTManager,
    APIKeyManager,
    AuthenticationService
)

# Rate limiting and request validation
from app.security.rate_limiting import (
    rate_limiter,
    request_validator,
    api_security_validator,
    cors_validator,
    RateLimiter,
    SecurityHeadersMiddleware,
    RequestValidationMiddleware
)

# Services
from app.services.identity_verification_service import (
    identity_verification_service,
    IdentityVerificationService,
    OTPService
)

from app.services.fraud_detection_service import (
    fraud_detection_engine,
    FraudDetectionEngine,
    DeviceFingerprinter
)

from app.services.audit_logging_service import (
    audit_logger,
    AuditLogger
)

from app.services.guardian_integrity_service import (
    guardian_integrity_service,
    GuardianIntegrityService,
    IntegrityScorer,
    ClaimClassifier
)

__all__ = [
    # Encryption
    "encryption_manager",
    "hash_manager",
    "encrypt_national_id",
    "decrypt_national_id",
    "encrypt_phone",
    "decrypt_phone",
    
    # Masking
    "data_masker",
    "DataMasker",
    "MaskedIdentity",
    "MaskedAsset",
    
    # API Security
    "jwt_manager",
    "api_key_manager",
    "authentication_service",
    "JWTManager",
    "APIKeyManager",
    "AuthenticationService",
    
    # Rate limiting
    "rate_limiter",
    "request_validator",
    "api_security_validator",
    "cors_validator",
    "RateLimiter",
    "SecurityHeadersMiddleware",
    "RequestValidationMiddleware",
    
    # Services
    "identity_verification_service",
    "IdentityVerificationService",
    "OTPService",
    "fraud_detection_engine",
    "FraudDetectionEngine",
    "DeviceFingerprinter",
    "audit_logger",
    "AuditLogger",
    "guardian_integrity_service",
    "GuardianIntegrityService",
    "IntegrityScorer",
    "ClaimClassifier"
]
