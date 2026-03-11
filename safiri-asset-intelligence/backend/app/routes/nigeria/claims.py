from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ClaimRequest(BaseModel):
    asset_id: int
    owner_id: int

@router.post("/submit")
def submit_claim_nigeria(request: ClaimRequest):
    # Connect to Nigeria-specific DB
    # Placeholder: insert into Nigeria assets table
    return {"status": "submitted", "country": "Nigeria", "claim": request.dict()}
