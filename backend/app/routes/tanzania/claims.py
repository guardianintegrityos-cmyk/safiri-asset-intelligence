from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ClaimRequest(BaseModel):
    asset_id: int
    owner_id: int

@router.post("/submit")
def submit_claim_tanzania(request: ClaimRequest):
    # Connect to Tanzania-specific DB
    # Placeholder: insert into Tanzania assets table
    return {"status": "submitted", "country": "Tanzania", "claim": request.dict()}
