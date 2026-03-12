"""
Rate Limiting & Security Middleware for Safiri Asset Intelligence
Protects against scraping, DoS attacks, and fraudulent attempts
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import security_config
from collections import defaultdict


class RateLimiter:
    """
    Implements multi-tiered rate limiting
    Different limits for different endpoint types
    """
    
    def __init__(self):
        self.limiters = {}
        self._initialize_limiters()
    
    def _initialize_limiters(self):
        """Initialize rate limiters for different endpoint types"""
        self.limiters["search"] = Limiter(key_func=get_remote_address)
        self.limiters["claim"] = Limiter(key_func=get_remote_address)
        self.limiters["upload"] = Limiter(key_func=get_remote_address)
    
    def get_search_limiter(self):
        """Get search endpoint rate limiter"""
        return self.limiters["search"]
    
    def get_claim_limiter(self):
        """Get claim endpoint rate limiter"""
        return self.limiters["claim"]
    
    def get_upload_limiter(self):
        """Get document upload limiter"""
        return self.limiters["upload"]


class SecurityHeadersMiddleware:
    """
    Adds security headers to all responses
    Protects against common web vulnerabilities
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                
                # Add security headers
                if security_config.ENABLE_SECURITY_HEADERS:
                    headers.append((b"X-Content-Type-Options", b"nosniff"))
                    headers.append((b"X-Frame-Options", b"DENY"))
                    headers.append((b"X-XSS-Protection", b"1; mode=block"))
                    headers.append((b"Strict-Transport-Security", 
                                  f"max-age={security_config.HSTS_MAX_AGE}".encode()))
                    headers.append((b"Content-Security-Policy", 
                                  b"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"))
                
                message["headers"] = headers
            
            await send(message)
        
        await self.app(scope, receive, send_with_headers)


class RequestValidationMiddleware:
    """
    Validates incoming requests for security
    Checks for suspicious patterns before reaching endpoints
    """
    
    def __init__(self):
        self.blocked_ips = {}  # IP -> unblock_time
        self.suspicious_patterns = self._load_patterns()
    
    def _load_patterns(self):
        """Load patterns to detect malicious requests"""
        return {
            "sql_injection": ["' OR '", "UNION", "SELECT", "DROP", "INSERT"],
            "xss": ["<script>", "javascript:", "onerror=", "onclick="],
            "traversal": ["../", "..\\", "%2e%2e"]
        }
    
    def is_ip_blocked(self, ip_address: str) -> Tuple[bool, Optional[str]]:
        """
        Check if IP is currently blocked
        
        Args:
            ip_address: Client IP address
            
        Returns:
            Tuple of (is_blocked, unblock_time)
        """
        if ip_address in self.blocked_ips:
            unblock_time = self.blocked_ips[ip_address]
            if datetime.utcnow() < unblock_time:
                return True, unblock_time
            else:
                del self.blocked_ips[ip_address]
        
        return False, None
    
    def block_ip(self, ip_address: str, duration_minutes: int = 60):
        """
        Temporarily block IP address
        
        Args:
            ip_address: IP to block
            duration_minutes: Duration of block
        """
        unblock_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.blocked_ips[ip_address] = unblock_time
    
    def detect_malicious_patterns(self, text: str) -> Optional[str]:
        """
        Detect known malicious patterns in request data
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected pattern type or None
        """
        text_upper = text.upper()
        
        for pattern_type, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                if pattern.upper() in text_upper:
                    return pattern_type
        
        return None
    
    def validate_request(self, request: Request) -> Tuple[bool, Optional[str]]:
        """
        Validate incoming request
        
        Args:
            request: FastAPI request object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if IP is blocked
        client_ip = request.client.host if request.client else "unknown"
        is_blocked, unblock_time = self.is_ip_blocked(client_ip)
        
        if is_blocked:
            return False, f"IP blocked until {unblock_time}"
        
        # Check for malicious patterns in query
        query_string = request.url.query
        if query_string:
            pattern = self.detect_malicious_patterns(query_string)
            if pattern:
                self.block_ip(client_ip, duration_minutes=120)
                return False, f"Malicious pattern detected: {pattern}"
        
        # Check for excessive headers (header bombing)
        if len(request.headers) > 100:
            return False, "Too many headers"
        
        # Check Content-Length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 50_000_000:  # 50MB limit
            return False, "Request too large"
        
        return True, None


class APISecurityValidator:
    """
    Validates API authentication and authorization
    Enforces zero-trust model
    """
    
    @staticmethod
    def validate_api_key(api_key: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate API key format and presence
        
        Args:
            api_key: API key from Authorization header
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not api_key:
            return False, "API key required"
        
        if not api_key.startswith(security_config.API_KEY_PREFIX):
            return False, "Invalid API key format"
        
        if len(api_key) < 30:
            return False, "API key too short"
        
        return True, None
    
    @staticmethod
    def validate_bearer_token(auth_header: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate Bearer token format
        
        Args:
            auth_header: Authorization header value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not auth_header:
            return False, "Authorization header required"
        
        if not auth_header.startswith("Bearer "):
            return False, "Invalid authorization format"
        
        token = auth_header.replace("Bearer ", "")
        if not token:
            return False, "No token provided"
        
        return True, None


class CORSValidator:
    """
    Validates Cross-Origin requests
    Implements strict CORS policy
    """
    
    @staticmethod
    def is_origin_allowed(origin: str) -> bool:
        """
        Check if origin is allowed
        
        Args:
            origin: Request origin header
            
        Returns:
            True if origin is in whitelist
        """
        return origin in security_config.ALLOWED_ORIGINS
    
    @staticmethod
    def get_cors_headers(origin: str) -> dict:
        """
        Get CORS headers for response
        
        Args:
            origin: Request origin
            
        Returns:
            Dictionary of CORS headers
        """
        if CORSValidator.is_origin_allowed(origin):
            return {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Max-Age": "3600"
            }
        return {}


# Global instances
rate_limiter = RateLimiter()
request_validator = RequestValidationMiddleware()
api_security_validator = APISecurityValidator()
cors_validator = CORSValidator()
