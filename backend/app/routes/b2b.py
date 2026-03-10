from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict

router = APIRouter()

# Sample token-based auth for institutions
def verify_api_key(api_key: str):
    if api_key != "SAFE_API_KEY_SAMPLE":
        raise HTTPException(status_code=403, detail="Unauthorized")

@router.get("/matches", dependencies=[Depends(verify_api_key)])
def get_matches(query: str):
    """
    Returns potential matches for dormant assets based on search query.
    """
    # TODO: Integrate with matching engine
    results = [
        {"owner_name": "John Kamau", "asset_type": "Bank Account", "confidence": 95},
        {"owner_name": "Mary Wanjiku", "asset_type": "Insurance Payout", "confidence": 88},
    ]
    return {"query": query, "matches": results}
