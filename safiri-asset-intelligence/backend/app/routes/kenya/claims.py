from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ClaimRequest(BaseModel):
    asset_id: int
    owner_id: int

@router.post("/submit")
def submit_claim_kenya(request: ClaimRequest):
    # Connect to Kenya-specific DB
    # Placeholder: insert into Kenya assets table
    return {"status": "submitted", "country": "Kenya", "claim": request.dict()}
