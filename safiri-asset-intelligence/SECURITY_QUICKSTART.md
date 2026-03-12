# Security Implementation Quick-Start Guide
## Safiri Asset Intelligence - Guardian Academy

---

## Installation & Setup (5 minutes)

### 1. Install Dependencies

```bash
cd safiri-asset-intelligence/backend

# Install security packages
pip install -r requirements.txt

# Verify key packages installed
python -c "
import jwt
import bcrypt
from cryptography.fernet import Fernet
from slowapi import Limiter
print('✓ All security packages installed successfully')
"
```

### 2. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env

# Required values to set:
# SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
# ENCRYPTION_KEY=<generate-with-Fernet.generate_key()>
# DATABASE_URL=postgresql://...
# TWILIO_ACCOUNT_SID=<your-sid>
# TWILIO_AUTH_TOKEN=<your-token>
```

### 3. Initialize Database

```bash
# Create encryption tables
python -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('✓ Database tables created')
"

# Or use migrations
alembic upgrade head
```

---

## Quick Testing (10 minutes)

### 1. Start Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Test Authentication

```bash
# Create a test user
python -c "
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.security import hash_manager

db = SessionLocal()

user = User(
    username='test@example.com',
    email='test@example.com',
    password_hash=hash_manager.hash_password('Password123!'),
    full_name='Test User',
    is_active=True,
    is_verified=True,
    verification_level=3
)

db.add(user)
db.commit()
print(f'✓ Test user created: {user.user_id}')
"

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "Password123!"
  }'

# Copy the access_token from response
export TOKEN="eyJhbGc..."
```

### 3. Test Secured Endpoint

```bash
# Search with authentication
curl -X GET "http://localhost:8000/search?query=test" \
  -H "Authorization: Bearer $TOKEN"

# Expected response (masked):
# {
#   "identity_id": 123,
#   "name": "T*** U***",
#   "national_id": "****5678",
#   "match_score": 0.92
# }
```

### 4. Test Identity Verification

```bash
# Start verification
curl -X POST http://localhost:8000/verify/start \
  -H "Authorization: Bearer $TOKEN"

# Response:
# {
#   "verification_id": 123,
#   "stage": 1
# }

# Send email OTP
curl -X POST http://localhost:8000/verify/email-otp \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "verification_id": 123,
    "email": "test@example.com"
  }'

# Check console for OTP code (development mode)
```

### 5. Test Fraud Detection

```bash
# Make multiple searches to trigger rate limit
for i in {1..11}; do
  curl -X GET "http://localhost:8000/search?query=test&iteration=$i" \
    -H "Authorization: Bearer $TOKEN" &
  sleep 0.1
done

# 11th request should get 429 Too Many Requests
```

---

## Implementation Checklist

### Phase 1: Core Security (Week 1)

- [ ] JWT authentication configured
- [ ] API key management working
- [ ] Unit tests passing for encryption
- [ ] Rate limiting operational
- [ ] Environment variables set

### Phase 2: Fraud Detection (Week 2)

- [ ] Fraud detection engine integrated into search endpoint
- [ ] Device fingerprinting working
- [ ] Audit logging functional
- [ ] Suspicious activity alerts configured

### Phase 3: Identity Verification (Week 3)

- [ ] 3-stage verification pipeline complete
- [ ] Email OTP service working
- [ ] SMS OTP service (Twilio) configured
- [ ] Face detection/matching implemented
- [ ] Document validation working

### Phase 4: Guardian Integrity (Week 4)

- [ ] Integrity scoring working
- [ ] Claim classification functioning
- [ ] Institutional review workflow operational
- [ ] Appeal process implemented

### Phase 5: Deployment (Week 5)

- [ ] HTTPS/SSL configured
- [ ] Cloudflare WAF integrated
- [ ] Database backed up
- [ ] Monitoring & alerting set up
- [ ] Security audit completed

---

## Code Examples

### Authentication (Protecting Endpoints)

```python
# In your routes
from fastapi import Depends, HTTPException
from app.security import jwt_manager

async def get_current_user(request):
    """Dependency that validates JWT token"""
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth.replace("Bearer ", "")
    is_valid, payload = jwt_manager.verify_token(token)
    
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return payload

@app.get("/protected-endpoint")
async def protected_route(user = Depends(get_current_user)):
    return {"user_id": user["user_id"], "message": "Access granted"}
```

### Data Masking (Protecting Responses)

```python
# When returning identity data
from app.security import MaskedIdentity

identity_data = {
    "identity_id": 123,
    "full_name": "James Mwangi",
    "national_id": "12345678",
    "phone": "+254712345678",
    "email": "james@example.com"
}

# For regular users (masked)
masked = MaskedIdentity(identity_data)
response = masked.to_dict(include_sensitive=False)
# Returns: {"name": "J**** M*****", "national_id": "****5678", ...}

# For admins (full data)
response_admin = masked.to_dict(include_sensitive=True)
# Returns: Full unmasked data
```

### Fraud Detection (Protecting from Attacks)

```python
# Integrate into search endpoint
from app.security import fraud_detection_engine

# Check for fraud
is_verified, message, analysis = fraud_detection_engine.verify_before_claim(
    user_id=user_id,
    identity_id=identity_id,
    ip_address=request.client.host,
    device_fingerprint=get_device_fingerprint(request),
    db=db
)

if not is_verified:
    # Block or require additional verification
    audit_logger.log_suspicious_activity(...)
    raise HTTPException(status_code=403, detail="Additional verification required")

# Proceed with claim
```

### Audit Logging (Recording All Actions)

```python
# Log every important action
from app.services.audit_logging_service import audit_logger

audit_logger.log_identity_query(
    user_id=user_id,
    query="james mwangi",
    identity_id=123,
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent"),
    device_fingerprint=fingerprint,
    found=True,
    fraud_score=0.15,
    db=db
)

# Later, retrieve audit trail for investigation
logs = audit_logger.get_audit_trail(
    resource_type="identity",
    resource_id=123,
    days=30,
    db=db
)
```

### Guardian Integrity (Assessing Claims)

```python
# When user makes a claim
from app.services.guardian_integrity_service import guardian_integrity_service

# Generate integrity assessment
integrity = guardian_integrity_service.assess_claim_integrity(
    identity_id=123,
    verification=verification_obj,
    fraud_score=0.2,
    asset_value=50000,
    db=db
)

print(f"Integrity Score: {integrity.overall_score}")
print(f"Claim Level: {integrity.claim_level}")

# Level 1 → Auto-approve in 1 hour
# Level 2 → Human review in 24 hours
# Level 3 → Institutional verification in 72 hours
```

---

## Troubleshooting

### Issue: "JWT decode error"
```
Solution: Make sure SECRET_KEY is set in .env and consistent
python -c "import os; print(os.getenv('SECRET_KEY'))"
```

### Issue: "Rate limit exceeded" immediately
```
Solution: Check rate limit config in app/config.py
Default: 10 searches/hour - adjust if needed
```

### Issue: "OTP not working"
```
Solution: Check Twilio credentials in .env
Development mode prints OTP to console
```

### Issue: "Database connection refused"
```
Solution: Verify DATABASE_URL in .env
psql $DATABASE_URL -c "SELECT 1" to test connection
```

---

## Next Steps

1. **Read [SECURITY.md](./SECURITY.md)** - Comprehensive architecture documentation
2. **Review [requirements.txt](./backend/requirements.txt)** - All dependencies
3. **Test all endpoints** - Use provided curl examples
4. **Set up monitoring** - Configure alerts for suspicious activity
5. **Schedule security audit** - Annual penetration testing
6. **Train team** - Ensure all developers understand security layers

---

## Key Files & Locations

```
safiri-asset-intelligence/backend/
├── app/
│   ├── security/
│   │   ├── __init__.py          # Security module exports
│   │   ├── encryption.py         # Encryption & hashing
│   │   ├── masking.py            # Data masking utilities
│   │   ├── api_security.py       # JWT & API key management
│   │   └── rate_limiting.py      # Rate limiting & request validation
│   ├── services/
│   │   ├── identity_verification_service.py    # 3-stage verification
│   │   ├── fraud_detection_service.py          # Fraud detection engine
│   │   ├── audit_logging_service.py            # Comprehensive audit trail
│   │   └── guardian_integrity_service.py       # Integrity oversight
│   ├── models.py                 # Security-related database models
│   ├── config.py                 # Security configuration (CRITICAL)
│   ├── main.py                   # Main API with security integrated
│   └── database.py               # Database connection
├── .env.example                  # Environment template (COPY & EDIT)
└── requirements.txt              # All dependencies including security
```

---

## Support

- **Documentation**: See SECURITY.md
- **Issues**: Contact security@guardian-academy.org
- **Updates**: Check README.md for latest version

---

**Version**: 2.0.0  
**Last Updated**: March 2026  
**Status**: Production-Ready
