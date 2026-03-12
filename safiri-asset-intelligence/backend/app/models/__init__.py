try:
    from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Text, JSON  # type: ignore
    from sqlalchemy.ext.declarative import declarative_base  # type: ignore
    from sqlalchemy.orm import relationship  # type: ignore
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

    # Fallback classes for when SQLAlchemy is not available
    class Column:
        def __init__(self, *args, **kwargs):
            pass

    Integer = String = DateTime = ForeignKey = Float = Boolean = Text = JSON = Column

    class declarative_base:
        def __init__(self):
            pass

        def __call__(self):
            return type('Base', (), {})

    class relationship:
        def __init__(self, *args, **kwargs):
            pass

from datetime import datetime

if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
else:
    Base = declarative_base()

class IdentityCore(Base):
    __tablename__ = 'identity_core'
    identity_id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    national_id = Column(String, unique=True)
    postal_address = Column(String)
    phone = Column(String)
    email = Column(String)
    date_of_birth = Column(DateTime)
    assets = relationship("Asset", back_populates="identity")
    aliases = relationship("IdentityAlias", back_populates="identity")
    links = relationship("IdentityLinks", back_populates="identity")
    cluster_memberships = relationship("ClusterMembers", back_populates="identity")

class Asset(Base):
    __tablename__ = 'assets'
    asset_id = Column(Integer, primary_key=True)
    identity_id = Column(Integer, ForeignKey('identity_core.identity_id'))
    asset_type = Column(String, nullable=False)  # cash, shares, safe_deposit
    institution = Column(String, nullable=False)
    account_number = Column(String)
    amount = Column(Float)
    status = Column(String)
    identity = relationship("IdentityCore", back_populates="assets")

class IdentityAlias(Base):
    __tablename__ = 'identity_alias'
    alias_id = Column(Integer, primary_key=True)
    identity_id = Column(Integer, ForeignKey('identity_core.identity_id'))
    name_variations = Column(String)
    previous_addresses = Column(String)
    alternative_ids = Column(String)
    identity = relationship("IdentityCore", back_populates="aliases")

class IdentityLinks(Base):
    __tablename__ = 'identity_links'
    link_id = Column(Integer, primary_key=True)
    identity_id = Column(Integer, ForeignKey('identity_core.identity_id'))
    linked_identifier = Column(String, nullable=False)
    identifier_type = Column(String, nullable=False)  # e.g., phone, email, account
    confidence_score = Column(Float, default=1.0)
    identity = relationship("IdentityCore", back_populates="links")

# Identity Resolution Engine (IRE) Models
class IdentityClusters(Base):
    __tablename__ = 'identity_clusters'
    cluster_id = Column(Integer, primary_key=True)
    representative_name = Column(String, nullable=False)
    representative_address = Column(Text)
    cluster_size = Column(Integer, nullable=False, default=1)
    confidence_score = Column(Float, nullable=False, default=0.0)
    country = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    validated = Column(Boolean, default=False)
    members = relationship("ClusterMembers", back_populates="cluster")
    resolution_logs = relationship("IdentityResolutionLog", back_populates="cluster")

class ClusterMembers(Base):
    __tablename__ = 'cluster_members'
    member_id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, ForeignKey('identity_clusters.cluster_id'), nullable=False)
    identity_id = Column(Integer, ForeignKey('identity_core.identity_id'))
    source_table = Column(String, nullable=False)  # identity_core, identity_alias, etc.
    source_record_id = Column(Integer, nullable=False)
    similarity_score = Column(Float, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    cluster = relationship("IdentityClusters", back_populates="members")
    identity = relationship("IdentityCore", back_populates="cluster_memberships")

class IdentityResolutionLog(Base):
    __tablename__ = 'identity_resolution_log'
    log_id = Column(Integer, primary_key=True)
    query_hash = Column(String, nullable=False)
    query_params = Column(JSON)
    resolved_cluster_id = Column(Integer, ForeignKey('identity_clusters.cluster_id'))
    confidence_score = Column(Float)
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    cluster = relationship("IdentityClusters", back_populates="resolution_logs")


# ============================================
# SECURITY & AUTHENTICATION MODELS
# ============================================

class User(Base):
    """
    User authentication and profile management
    Financial-grade security for all user accounts
    """
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)  # bcrypt hashed
    
    # Profile information
    full_name = Column(String)
    role = Column(String, default="user")  # user, admin, institution, guardian
    
    # Account status
    is_active = Column(Boolean, default=False)  # requires email verification
    is_verified = Column(Boolean, default=False)  # multi-factor verification
    verification_level = Column(Integer, default=0)  # 0=none, 1=basic, 2=identity, 3=full
    
    # Two-factor authentication
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String)  # encrypted TOTP secret
    
    # Account security
    failed_login_attempts = Column(Integer, default=0)
    last_login_at = Column(DateTime)
    locked_until = Column(DateTime)  # temporarily locked after too many failed attempts
    
    # Terms and consent
    terms_accepted = Column(Boolean, default=False)
    privacy_policy_accepted = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_password_change = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user")
    identity_verifications = relationship("IdentityVerification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    fraud_reports = relationship("FraudReport", back_populates="user")


class APIKey(Base):
    """
    API keys for service-to-service authentication
    Each service must authenticate independently
    """
    __tablename__ = 'api_keys'
    
    key_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    key_name = Column(String, nullable=False)
    key_hash = Column(String, unique=True, nullable=False)  # hashed API key
    
    # Permissions and scope
    scopes = Column(JSON, default={})  # e.g., ["read", "write", "admin"]
    
    # Rate limiting
    requests_today = Column(Integer, default=0)
    requests_limit = Column(Integer, default=1000)  # per day
    
    # Security
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    ip_whitelist = Column(JSON, default=[])  # restrict to specific IPs
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # optional expiration
    revoked_at = Column(DateTime)
    
    user = relationship("User", back_populates="api_keys")


class IdentityVerification(Base):
    """
    Multi-stage identity verification pipeline
    Stage 1: Email + Phone OTP + CAPTCHA
    Stage 2: ID Document + Selfie + Face Match
    Stage 3: Proof of Ownership + Bank Statement
    """
    __tablename__ = 'identity_verifications'
    
    verification_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    identity_id = Column(Integer, ForeignKey('identity_core.identity_id'))
    
    # Verification stages
    stage = Column(Integer, default=1)  # 1, 2, or 3
    status = Column(String, default="pending")  # pending, in_progress, verified, rejected, expired
    
    # Stage 1 - Basic verification
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime)
    phone_verified = Column(Boolean, default=False)
    phone_verified_at = Column(DateTime)
    captcha_passed = Column(Boolean, default=False)
    
    # Stage 2 - Identity verification
    document_uploaded = Column(Boolean, default=False)
    document_verified = Column(Boolean, default=False)
    document_url = Column(String)
    document_hash = Column(String)  # hash for forgery detection
    
    selfie_uploaded = Column(Boolean, default=False)
    selfie_verified = Column(Boolean, default=False)
    selfie_url = Column(String)
    face_match_confidence = Column(Float)  # 0.0-1.0
    
    # Stage 3 - Ownership verification
    proof_of_ownership_uploaded = Column(Boolean, default=False)
    proof_of_ownership_verified = Column(Boolean, default=False)
    
    # Overall confidence
    confidence_score = Column(Float, default=0.0)  # 0.0-1.0
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    verified_at = Column(DateTime)
    rejected_reason = Column(String)
    
    user = relationship("User", back_populates="identity_verifications")


class AuditLog(Base):
    """
    Complete audit trail for compliance and investigation
    Records every action in the system for forensic analysis
    """
    __tablename__ = 'audit_logs'
    
    log_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    
    # Action details
    action = Column(String, nullable=False)  # search, claim, upload, admin_action, etc.
    action_type = Column(String)  # identity_query, asset_claim, document_upload, etc.
    result = Column(String)  # success, failure, blocked
    
    # Request details
    resource_type = Column(String)  # identity, asset, document, user, etc.
    resource_id = Column(Integer)
    query_data = Column(JSON)  # searched query parameters
    
    # Network information (for fraud detection)
    ip_address = Column(String, index=True)
    user_agent = Column(String)
    device_fingerprint = Column(String)
    
    # Geographic information
    country = Column(String)
    city = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Request/response
    status_code = Column(Integer)
    error_message = Column(String)
    response_time_ms = Column(Integer)
    
    # Security flags
    flagged_as_suspicious = Column(Boolean, default=False)
    fraud_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="audit_logs")


class FraudDetectionEvent(Base):
    """
    Tracks suspicious behavior patterns for fraud detection
    Accumulates evidence for blocking malicious users
    """
    __tablename__ = 'fraud_detection_events'
    
    event_id = Column(Integer, primary_key=True)
    
    # Classification
    event_type = Column(String, nullable=False)  # rate_limit, repeated_query, ip_mass_search, etc.
    severity = Column(String)  # low, medium, high, critical
    
    # Subject
    ip_address = Column(String, index=True)
    device_fingerprint = Column(String)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
    
    # Evidence
    search_count = Column(Integer)  # how many searches of same ID
    claim_count = Column(Integer)  # how many claims from same IP
    unique_ids_queried = Column(Integer)
    
    # Context
    query_details = Column(JSON)  # what they were searching for
    
    # Action
    action_taken = Column(String)  # none, warned, rate_limited, blocked, manual_review
    blocked_until = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User")


class FraudReport(Base):
    """
    Reports of fraudulent activity for investigation
    Supports Guardian Integrity Oversight Layer
    """
    __tablename__ = 'fraud_reports'
    
    report_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    
    # Report details
    report_type = Column(String)  # identity_spoofing, document_forgery, false_claim, etc.
    description = Column(Text)
    evidence = Column(JSON)  # attachments, links, etc.
    
    # Status
    status = Column(String, default="open")  # open, investigating, resolved, dismissed
    assigned_to = Column(Integer)  # admin user_id
    
    # Outcome
    findings = Column(Text)
    action_taken = Column(String)  # warning, suspension, permanent_ban, no_action
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    user = relationship("User", back_populates="fraud_reports")


class GuardianIntegrity(Base):
    """
    Guardian Integrity Oversight Layer
    Tracks claim integrity scores and institutional verification
    """
    __tablename__ = 'guardian_integrity'
    
    integrity_id = Column(Integer, primary_key=True)
    identity_id = Column(Integer, ForeignKey('identity_core.identity_id'))
    
    # Integrity metrics
    overall_score = Column(Float, default=0.0)  # 0.0-1.0 (1.0 = most trustworthy)
    
    # Component scores
    identity_confidence = Column(Float, default=0.0)  # how verified the identity is
    document_authenticity = Column(Float, default=0.0)  # document validation score
    behavior_risk = Column(Float, default=0.0)  # behavioral red flags (lower = higher risk)
    
    # Claim classification
    claim_level = Column(Integer, default=1)  # 1=auto-approve, 2=review, 3=institutional
    
    # Institutional oversight
    institution_reviewed = Column(Boolean, default=False)
    institution_reviewer_id = Column(Integer)
    institution_review_notes = Column(Text)
    
    # Appeal process
    appeal_filed = Column(Boolean, default=False)
    appeal_status = Column(String)  # pending, approved, rejected
    appeal_notes = Column(Text)
    
    # Timeline
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_reviewed_at = Column(DateTime)


# ============================================
# EXPORTS - All models publicly available
# ============================================

__all__ = [
    "Base",
    "IdentityCore",
    "Asset",
    "IdentityAlias",
    "IdentityLinks",
    "IdentityClusters",
    "ClusterMembers",
    "IdentityResolutionLog",
    "User",
    "APIKey",
    "IdentityVerification",
    "AuditLog",
    "FraudDetectionEvent",
    "FraudReport",
    "GuardianIntegrity",
]
