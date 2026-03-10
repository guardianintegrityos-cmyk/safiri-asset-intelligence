from fastapi import Request, HTTPException

API_KEYS = {"BANK123": 1000, "INSURER456": 500}  # Example: keys with daily quota
USAGE_TRACKER = {}

async def api_key_auth(request: Request):
    key = request.headers.get("x-api-key")
    if not key or key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Simple rate limiting
    count = USAGE_TRACKER.get(key, 0)
    if count >= API_KEYS[key]:
        raise HTTPException(status_code=429, detail="Quota exceeded")
    USAGE_TRACKER[key] = count + 1
