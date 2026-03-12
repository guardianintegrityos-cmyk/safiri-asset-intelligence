# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

try:
    from fastapi import FastAPI, Depends, Request, HTTPException, status
    from fastapi.middleware.cors import CORSMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    # Fallback for when FastAPI is not available
    FASTAPI_AVAILABLE = False

    class FastAPI:
        def __init__(self, title=""):
            self.title = title
            self.routes = []

        def get(self, path):
            def decorator(func):
                self.routes.append(('GET', path, func))
                return func
            return decorator

        def include_router(self, router):
            pass

    class Depends:
        def __init__(self, dependency):
            self.dependency = dependency

from sqlalchemy.orm import Session
from app.database import get_db
try:
    from app.matching_engine.matching_engine import search_ownership_probability, detect_fraud
except ImportError:
    # Fallback stubs for matching engine
    def search_ownership_probability(*args, **kwargs):
        return {}
    def detect_fraud(*args, **kwargs):
        return {"fraud_score": 0.0}

# Optional imports - gracefully skip if not available
try:
    from app.services.federation_service import federation_service
except (ImportError, ModuleNotFoundError):
    federation_service = None

try:
    from app.services.identity_engine.api import identity_resolution_router
except (ImportError, ModuleNotFoundError):
    identity_resolution_router = None

# ============================================
# SECURITY IMPORTS
# ============================================
from app.config import security_config
from app.security import (
    jwt_manager,
    api_key_manager,
    authentication_service,
    rate_limiter,
    request_validator,
    api_security_validator,
    cors_validator,
    data_masker,
    audit_logger,
    fraud_detection_engine,
    identity_verification_service,
    guardian_integrity_service
)

app = FastAPI(
    title="Safiri Continental Asset Intelligence Network",
    description="Financial-grade security architecture for asset intelligence"
)

# ============================================
# SECURITY MIDDLEWARE SETUP
# ============================================

# 1. CORS Configuration
if security_config.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=security_config.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        max_age=3600
    )

# 2. Security Headers Middleware
from app.security import SecurityHeadersMiddleware
app.add_middleware(SecurityHeadersMiddleware)

# 3. Rate limiting
search_limiter = rate_limiter.get_search_limiter()
claim_limiter = rate_limiter.get_claim_limiter()
upload_limiter = rate_limiter.get_upload_limiter()

# ============================================
# INCLUDE ROUTERS
# ============================================

if FASTAPI_AVAILABLE and identity_resolution_router:
    app.include_router(identity_resolution_router)

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/auth/login")
async def login(username: str, password: str, request: Request, db: Session = Depends(get_db)):
    """
    User login endpoint
    Returns JWT access token and refresh token
    """
    ip_address = request.client.host if request.client else "unknown"
    
    # Log authentication attempt
    success, tokens, error = authentication_service.authenticate_user(
        username, password, ip_address, db
    )
    
    audit_logger.log_authentication_attempt(
        username=username,
        ip_address=ip_address,
        user_agent=request.headers.get("user-agent", "unknown"),
        success=success,
        error=error,
        db=db
    )
    
    if not success:
        raise HTTPException(status_code=401, detail=error)
    
    access_token, refresh_token = tokens
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@app.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token
    """
    is_valid, payload = jwt_manager.verify_token(refresh_token)
    
    if not is_valid or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Generate new access token
    user_id = payload["user_id"]
    # In production, look up user from database to get username and role
    new_token = jwt_manager.generate_token(user_id, payload.get("username", "user"))
    
    return {"access_token": new_token, "token_type": "bearer"}


# ============================================
# SECURED ASSET SEARCH ENDPOINTS
# ============================================

async def get_current_user(request: Request):
    """
    Dependency: Verify JWT token in Authorization header
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    is_valid, error = api_security_validator.validate_bearer_token(auth_header)
    if not is_valid:
        raise HTTPException(status_code=401, detail=error)
    
    token = auth_header.replace("Bearer ", "")
    is_valid, payload = jwt_manager.verify_token(token)
    
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload


@app.get("/search")
@search_limiter.limit("10/hour")
async def search_assets(
    query: str,
    country: str = None,
    request: Request = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Federated search across African countries
    Secure endpoint with rate limiting and audit logging
    """
    ip_address = request.client.host if request.client else "unknown"
    device_fp = f"{request.headers.get('user-agent', 'unknown')}:{ip_address}"
    
    # Fraud detection
    is_verified, message, analysis = fraud_detection_engine.verify_before_claim(
        user_id=user.get("user_id"),
        identity_id=0,  # Will be set once identity found
        ip_address=ip_address,
        device_fingerprint=device_fp,
        db=db
    )
    
    fraud_score = analysis.get("fraud_score", 0.0) if analysis else 0.0
    
    # Perform search
    if country and country.lower() in federation_service.country_nodes:
        result = federation_service.query_country_node(country.lower(), query)
        found = result is not None
    else:
        result = search_ownership_probability(query, db)
        found = result is not None
    
    # Mask sensitive data in response
    if found and result:
        masked_result = {
            "identity_id": result.get("identity_id"),
            "name": data_masker.mask_full_name(result.get("full_name")),
            "national_id": data_masker.mask_national_id(result.get("national_id")),
            "match_score": result.get("match_score"),
            "integrity_score": result.get("integrity_score")
        }
    else:
        masked_result = {"status": "not_found"}
    
    # Audit log
    audit_logger.log_identity_query(
        user_id=user.get("user_id"),
        query=query,
        identity_id=result.get("identity_id") if found else 0,
        ip_address=ip_address,
        user_agent=request.headers.get("user-agent", "unknown"),
        device_fingerprint=device_fp,
        found=found,
        fraud_score=fraud_score,
        db=db
    )
    
    return masked_result


@app.get("/local-search")
async def local_search(
    query: str,
    request: Request = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Local country search with security
    """
    ip_address = request.client.host if request.client else "unknown"
    
    result = search_ownership_probability(query, db)
    
    # Mask response
    if result:
        return {
            "found": True,
            "identity_id": result.get("identity_id"),
            "name": data_masker.mask_full_name(result.get("full_name")),
            "match_score": result.get("match_score")
        }
    
    return {"found": False}


@app.get("/fraud-check/{identity_id}")
async def check_fraud(
    identity_id: int,
    request: Request = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check fraud risk for identity
    Admin endpoint
    """
    from app.models import IdentityCore
    
    identity = db.query(IdentityCore).filter(IdentityCore.identity_id == identity_id).first()
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    
    is_fraud = detect_fraud(identity, db)
    
    audit_logger.log_action(
        action="fraud_check",
        action_type="security_audit",
        user_id=user.get("user_id"),
        resource_type="identity",
        resource_id=identity_id,
        ip_address=request.client.host if request.client else "unknown",
        query_data={"identity_id": identity_id},
        db=db
    )
    
    return {
        "identity_id": identity_id,
        "fraud_risk": is_fraud,
        "verification_required": not is_fraud is False
    }


# ============================================
# IDENTITY VERIFICATION ENDPOINTS
# ============================================

@app.post("/verify/start")
async def start_verification(
    request: Request = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate identity verification (Stage 1: Email + Phone OTP)
    """
    user_id = user.get("user_id")
    
    verification = identity_verification_service.start_verification(user_id, db)
    
    audit_logger.log_action(
        action="verify_start",
        action_type="identity_verification",
        user_id=user_id,
        resource_type="identity_verification",
        resource_id=verification.verification_id,
        ip_address=request.client.host if request.client else "unknown",
        db=db
    )
    
    return {"verification_id": verification.verification_id, "stage": 1}


@app.post("/verify/email-otp")
async def send_email_otp(
    verification_id: int,
    email: str,
    request: Request = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send email OTP
    """
    success, message = identity_verification_service.send_email_verification(
        email, verification_id, db
    )
    
    return {
        "success": success,
        "message": message,
        "email_masked": data_masker.mask_email(email)
    }


@app.post("/verify/phone-otp")
async def send_phone_otp(
    verification_id: int,
    phone: str,
    request: Request = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send phone OTP via SMS
    """
    success, message = identity_verification_service.send_phone_verification(
        phone, verification_id, db
    )
    
    return {
        "success": success,
        "message": message,
        "phone_masked": data_masker.mask_phone(phone)
    }


# ============================================
# GUARDIAN INTEGRITY ENDPOINTS
# ============================================

@app.get("/integrity/{identity_id}")
async def get_integrity_score(
    identity_id: int,
    request: Request = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Guardian Integrity score and claim classification
    """
    from app.models import GuardianIntegrity
    
    integrity = db.query(GuardianIntegrity).filter(
        GuardianIntegrity.identity_id == identity_id
    ).first()
    
    if not integrity:
        raise HTTPException(status_code=404, detail="Integrity assessment not found")
    
    return guardian_integrity_service.generate_integrity_report(integrity)


# ============================================
# HEALTH & STATUS ENDPOINTS
# ============================================

@app.get("/network-stats")
async def get_network_stats():
    """
    Get statistics from the continental network
    """
    return federation_service.get_country_statistics()


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": str(__import__('datetime').datetime.utcnow()),
        "security_enabled": True
    }


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Welcome to Safiri Asset Intelligence API",
        "version": "2.0.0",
        "security": "Financial-grade security (Guardian Academy)"
    }

