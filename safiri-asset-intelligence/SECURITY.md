# Safiri Asset Intelligence - Production Security Architecture
## Guardian Academy Financial-Grade Security Framework

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Zero-Trust Model](#zero-trust-model)
3. [Security Layers](#security-layers)
4. [Implementation Guide](#implementation-guide)
5. [API Documentation](#api-documentation)
6. [Deployment Checklist](#deployment-checklist)

---

## Architecture Overview

Safiri's security architecture treats **identity, assets, and integrity** as the core of a financial-grade system. Every component assumes attackers will attempt to:

- **Scrape data** via mass queries
- **Spoof identities** with fake documents
- **Manipulate results** through API abuse
- **Create fraudulent claims** against real assets
- **Launch DDoS attacks** against infrastructure

### Security Stack

```
┌─────────────────────────────────────────────────────────┐
│  Browser / Mobile Client                               │
├─────────────────────────────────────────────────────────┤
│  HTTPS (TLS 1.3+) + Security Headers                   │
├─────────────────────────────────────────────────────────┤
│  Cloudflare WAF (DDoS protection + Bot filtering)      │
├─────────────────────────────────────────────────────────┤
│  API Gateway (Rate Limiting + Request Validation)      │
├─────────────────────────────────────────────────────────┤
│  Authentication Layer (JWT + API Keys + OAuth)         │
├─────────────────────────────────────────────────────────┤
│  Fraud Detection Engine (Behavior Analysis)            │
├─────────────────────────────────────────────────────────┤
│  Identity Verification Pipeline (3-stage process)      │
├─────────────────────────────────────────────────────────┤
│  Guardian Integrity Oversight (Claim Classification)   │
├─────────────────────────────────────────────────────────┤
│  Data Masking Layer (PII Protection in Responses)      │
├─────────────────────────────────────────────────────────┤
│  Secure Data Layer (Encrypted PostgreSQL + Neo4j)      │
├─────────────────────────────────────────────────────────┤
│  Audit Logging (Complete Transaction Trail)           │
└─────────────────────────────────────────────────────────┘
```

---

## Zero-Trust Model

**Principle**: No request is trusted by default. Every access must pass through multiple verification gates.

### Trust Verification Sequence

```python
1. Request arrives
   ↓
2. Request validation (check for SQL injection, XSS, size limits)
   ↓
3. Rate limit check (Is this IP/user making too many requests?)
   ↓
4. Authentication (Valid JWT or API key?)
   ↓
5. Fraud detection (Behavioral analysis - is this request suspicious?)
   ↓
6. Device fingerprinting (Is this a known device or bot?)
   ↓
7. Authorization (Does this user have permission?)
   ↓
8. Data masking (Check if user should see full or masked data)
   ↓
9. Audit logging (Record action for investigation)
   ↓
10. Execute request
```

---

## Security Layers

### 1. Network Security

**Cloudflare WAF**
- DDoS protection
- Bot detection and blocking
- Rate limiting at edge
- IP reputation filtering

**Configuration**:
```yaml
cloudflare:
  waf_rules:
    - block_tor_exit_nodes: true
    - block_known_bots: true
    - rate_limit: 100_requests_per_10_seconds
```

### 2. Request Validation

**Detects**:
- SQL injection attempts
- Cross-site scripting (XSS)
- Path traversal attacks
- Header bombs
- Oversized payloads

**Implementation**:
```python
# From app/security/rate_limiting.py
request_validator.validate_request(request)

# Returns: (is_valid, error_message)
# If invalid, request is rejected immediately
```

### 3. Authentication

#### JWT Tokens (User Authentication)
```
POST /auth/login
{
  "username": "user@example.com",
  "password": "secure_password_12chars_min"
}

Returns:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Token Usage**:
```
GET /search?query=james%20mwangi
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

#### API Keys (Service Authentication)
```python
# Example: Generate API key for Matching Engine
raw_key, api_key_obj = api_key_manager.generate_api_key(
    user_id=123,
    key_name="matching_engine_service",
    scopes=["read", "write"]
)

# Returns:
# raw_key = "safiri_xk8z9m4p..."  (show to user once)
# api_key_obj = APIKey(...)        (stored in database)
```

**Service Usage**:
```bash
curl -H "X-API-Key: safiri_xk8z9m4p..." \
  https://api.safiri.org/search?query=john
```

### 4. Rate Limiting (Anti-Scraping)

**Limits**:
```python
# From app/config.py
RATE_LIMIT_SEARCHES_PER_HOUR = 10
RATE_LIMIT_SEARCHES_PER_DAY = 50
RATE_LIMIT_IDENTITY_QUERIES_PER_HOUR = 5
RATE_LIMIT_CLAIMS_PER_HOUR = 3
```

**In Action**:
```
User makes 11 searches in 1 hour
↓
Rate limiter blocks request
↓
Returns 429 Too Many Requests
↓
User must wait until hourly window resets
```

### 5. Fraud Detection Engine

**Detects**:
1. **Search Rate Violations** - More than X searches per hour
2. **Repeated Identity Queries** - Same ID searched 3+ times by same IP
3. **Mass ID Enumeration** - Searching 50+ different IDs (scraping)
4. **Device Anomalies** - More than 5 claims from same device
5. **Behavior Anomalies** - Unusual search patterns

**Example**:
```python
# Analyze suspicious behavior
analysis = fraud_detection_engine.analyze_behavior(
    ip_address="203.0.113.45",
    device_fingerprint="abc123...",
    identity_id=9001,
    db=db
)

# Returns:
{
    "fraud_score": 0.85,  # 0.0-1.0
    "is_suspicious": true,
    "flags": [
        "Search Rate Limit: 25 searches in 1 hour",
        "Repeated Identity Queries: 5 queries for same ID"
    ],
    "checks": {
        "Search Rate Limit": {"is_clean": false, "score": 0.8},
        "Device Fingerprint": {"is_clean": true, "score": 0.0}
        ...
    }
}

# If fraud_score > threshold:
# → Block user temporarily or require additional verification
```

### 6. Identity Verification Pipeline

**3-Stage Process**:

#### Stage 1: Basic Verification
```
1. Email verification (OTP)
2. Phone OTP (SMS via Twilio)
3. CAPTCHA completion
```

**Implementation**:
```python
# Start verification
verification = identity_verification_service.start_verification(user_id, db)

# Send email OTP
success, message = identity_verification_service.send_email_verification(
    email="user@example.com",
    verification_id=verification.id,
    db=db
)

# Verify OTP
is_valid, msg = identity_verification_service.verify_email_otp(
    verification_id=verification.id,
    email="user@example.com",
    otp_code="123456",
    db=db
)
```

#### Stage 2: Identity Verification
```
1. Upload identity document (ID card, passport)
2. Capture selfie
3. AI face matching
4. Document forgery detection
```

#### Stage 3: Ownership Verification
```
1. Upload proof of ownership (bank statement, asset certificate)
2. Institutional verification (if needed)
3. Guardian Integrity review
```

### 7. Data Masking (PII Protection)

**API Response Before Masking**:
```json
{
  "full_name": "James Mwangi",
  "national_id": "12345678",
  "phone": "+254712345678",
  "email": "james@example.com",
  "asset_amount": 50000
}
```

**API Response After Masking** (default user view):
```json
{
  "full_name": "J**** M*****",
  "national_id": "****5678",
  "phone": "+2547****5678",
  "email": "***@example.com",
  "asset_range": "40k - 60k"
}
```

**Policy**:
```python
# From app/config.py
MASK_SENSITIVE_DATA = True
MASK_FULL_NAME_MODE = "partial"    # "partial" or "full"
MASK_ID_NUMBER_MODE = "last_4"     # "last_4" or "last_2"
MASK_PHONE_MODE = "last_4"
MASK_EMAIL_MODE = "domain_only"
```

**Usage in Code**:
```python
from app.security import data_masker, MaskedIdentity

# Mask identity data
masked = MaskedIdentity(identity_data)
response = masked.to_dict(include_sensitive=False)  # User view
response_admin = masked.to_dict(include_sensitive=True)  # Admin view
```

### 8. Guardian Integrity Oversight

**Claim Classification**:

```
┌─────────────────────────────────────────────┐
│ Claim Integrity Score Calculation           │
├─────────────────────────────────────────────┤
│ Identity Confidence:    40%                 │
│ Document Authenticity:  35%                 │
│ Behavior Risk Score:    25%                 │
├─────────────────────────────────────────────┤
│ Total Score: 0.0 (reject) to 1.0 (approve) │
└─────────────────────────────────────────────┘

Score 0.80-1.0 → Level 1: Auto-Approve (1 hour)
Score 0.60-0.80 → Level 2: AI + Human Review (24 hours)
Score 0.00-0.60 → Level 3: Institutional Verification (72 hours)
```

**Implementation**:
```python
from app.services.guardian_integrity_service import guardian_integrity_service

# Assess claim
integrity = guardian_integrity_service.assess_claim_integrity(
    identity_id=123,
    verification=verification_obj,
    fraud_score=0.15,
    asset_value=50000,
    db=db
)

# Generate report
report = guardian_integrity_service.generate_integrity_report(integrity)

print(f"Integrity Score: {integrity.overall_score}")
print(f"Claim Level: {integrity.claim_level}")
print(f"Processing Time: {report['claim_classification']['typical_processing_time']} hours")
```

### 9. Encryption & Hashing

**Encryption** (sensitive data at rest):
```python
from app.security import encryption_manager

# Encrypt national ID
encrypted_id = encryption_manager.encrypt("12345678")
# Stored in DB: "gAAAAABl..."

# Decrypt when needed
decrypted_id = encryption_manager.decrypt(encrypted_id)
# Returns: "12345678"
```

**Hashing** (one-way, for deduplication):
```python
from app.security import hash_manager

# Hash for fraud detection (cannot be reversed)
id_hash = hash_manager.hash_pii("12345678")
# "a7f3c2e9... (SHA-256 hex string)"

# Password hashing
pwd_hash = hash_manager.hash_password("password123")
# Stored: "$2b$12$..." (bcrypt)

# Verify password
is_correct = hash_manager.verify_password("password123", pwd_hash)
# Returns: True
```

### 10. Audit Logging

**Complete transaction trail** for forensic analysis and compliance.

**Logged Events**:
- Identity searches
- Asset claims
- Document uploads
- Authentication attempts (success + failures)
- Admin actions
- Suspicious activities

**Implementation**:
```python
from app.services.audit_logging_service import audit_logger

# Log identity query
audit_logger.log_identity_query(
    user_id=456,
    query="james mwangi",
    identity_id=123,
    ip_address="203.0.113.45",
    user_agent="Mozilla/5.0...",
    device_fingerprint="abc123...",
    found=True,
    fraud_score=0.2,
    db=db
)

# Log asset claim
audit_logger.log_asset_claim(
    user_id=456,
    identity_id=123,
    asset_id=789,
    ip_address="203.0.113.45",
    user_agent="Mozilla/5.0...",
    device_fingerprint="abc123...",
    status="pending",
    fraud_score=0.15,
    db=db
)

# Retrieve audit trail for investigation
logs = audit_logger.get_audit_trail(
    resource_type="asset",
    resource_id=789,
    days=30,
    db=db
)

# Analyze suspicious IP activity
analysis = audit_logger.analyze_suspicious_activity(
    ip_address="203.0.113.45",
    days=7,
    db=db
)
```

---

## Implementation Guide

### 1. Setup Environment

```bash
# Copy example configuration
cp backend/.env.example backend/.env

# Edit .env with your values
nano backend/.env

# Generate secrets
python -m secrets.token_urlsafe(32)     # SECRET_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # ENCRYPTION_KEY
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Create Database Tables

```bash
# Using alembic migrations
alembic upgrade head

# Or run SQL directly
psql safiri_db < migrations/001_create_tables.sql
psql safiri_db < migrations/002_add_identity_resolution.sql
```

### 4. Start API Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --ssl-certfile=cert.pem --ssl-keyfile=key.pem
```

### 5. Example: Login & Search

```bash
# 1. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com", "password":"password123"}'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}

# 2. Search with JWT token
curl -X GET "http://localhost:8000/search?query=james%20mwangi" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# Response (masked data)
{
  "identity_id": 123,
  "name": "J**** M*****",
  "national_id": "****5678",
  "match_score": 0.92,
  "integrity_score": 0.78
}

# 3. Start verification
curl -X POST http://localhost:8000/verify/start \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json"

# Response
{
  "verification_id": 456,
  "stage": 1
}
```

---

## API Documentation

### Authentication Endpoints

#### `POST /auth/login`
**Login with username and password**

```
Request:
{
  "username": "user@example.com",
  "password": "password123"
}

Response (200 OK):
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}

Errors:
- 401: Invalid credentials
- 429: Too many login attempts
- 423: Account locked
```

#### `POST /auth/refresh`
**Refresh access token**

```
Request:
{
  "refresh_token": "eyJ..."
}

Response (200 OK):
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Identity Verification

#### `POST /verify/start`
**Initiate identity verification (Stage 1)**

```
Headers:
Authorization: Bearer <access_token>

Response (200 OK):
{
  "verification_id": 123,
  "stage": 1
}
```

#### `POST /verify/email-otp`
**Send email verification OTP**

```
Headers:
Authorization: Bearer <access_token>

Request:
{
  "verification_id": 123,
  "email": "user@example.com"
}

Response (200 OK):
{
  "success": true,
  "message": "OTP sent to email",
  "email_masked": "***@example.com"
}
```

#### `POST /verify/phone-otp`
**Send phone OTP via SMS**

```
Headers:
Authorization: Bearer <access_token>

Request:
{
  "verification_id": 123,
  "phone": "+254712345678"
}

Response (200 OK):
{
  "success": true,
  "message": "OTP sent to phone",
  "phone_masked": "+2547****5678"
}
```

### Asset Search

#### `GET /search`
**Search for asset and identity**

```
Headers:
Authorization: Bearer <access_token>

Query Params:
- query (string): Name, ID, email, or phone to search
- country (string, optional): Country code (KE, NG, TZ, UG)

Response (200 OK):
{
  "identity_id": 123,
  "name": "J**** M*****",
  "national_id": "****5678",
  "match_score": 0.92,
  "integrity_score": 0.78
}

Errors:
- 401: Unauthorized (no/invalid token)
- 429: Rate limit exceeded
- 403: Fraudulent activity detected
```

### Guardian Integrity

#### `GET /integrity/{identity_id}`
**Get integrity score and claim classification**

```
Headers:
Authorization: Bearer <access_token>

Response (200 OK):
{
  "integrity_id": 456,
  "identity_id": 123,
  "overall_integrity_score": 0.78,
  "component_scores": {
    "identity_confidence": 0.85,
    "document_authenticity": 0.92,
    "behavior_risk": 0.60
  },
  "claim_classification": {
    "level": 1,
    "name": "Automatic Approval",
    "description": "Low-risk, high-integrity claims auto-approved within 1 hour",
    "typical_processing_time": 1,
    "success_probability": 0.95
  },
  "institutional_verification": {
    "required": false,
    "completed": false
  }
}
```

---

## Deployment Checklist

### Pre-Production

- [ ] All environment variables set in `.env`
- [ ] Database encrypted and backed up
- [ ] SSL/TLS certificates generated and installed
- [ ] Cloudflare WAF configured
- [ ] Rate limits configured for expected load
- [ ] Twilio credentials configured for SMS OTP
- [ ] Email service configured for verification
- [ ] Audit log retention policy set (90 days minimum)
- [ ] Admin accounts created and 2FA enabled
- [ ] API keys generated for internal services

### Security Hardening

- [ ] HTTPS enforced (HTTP → HTTPS redirect)
- [ ] HSTS headers enabled
- [ ] Security headers configured
- [ ] CORS whitelist configured (not wildcard)
- [ ] Database connection SSL mode: "require"
- [ ] Database user permissions minimal (least privilege)
- [ ] API secrets not logged
- [ ] Failed login attempts trigger account lock
- [ ] Password requirements enforced
- [ ] Backup encryption enabled

### Monitoring & Logging

- [ ] Audit logging enabled
- [ ] Failed authentication attempts monitored
- [ ] Fraud detection alerts configured
- [ ] Rate limit violations logged
- [ ] Performance metrics collected
- [ ] Error rates monitored
- [ ] Database connections monitored
- [ ] Suspicious IP activity tracked

### Maintenance

- [ ] Regular security patches applied
- [ ] Database backups automated (daily)
- [ ] Audit logs archived (monthly)
- [ ] API keys rotated (quarterly)
- [ ] SSL certificates renewed (90 days before expiry)
- [ ] Security audit conducted (annually)
- [ ] Penetration testing scheduled

---

## Support & Contact

For security issues, contact: security@guardian-academy.org

For implementation support, refer to:
- [API Documentation](./API.md)
- [Database Schema](../db/migrations/README.md)
- [Deployment Guide](./DEPLOYMENT.md)

---

**Last Updated**: March 2026
**Version**: 2.0.0
**Status**: Production-Ready
