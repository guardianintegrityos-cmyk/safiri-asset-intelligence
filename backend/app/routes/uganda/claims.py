from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ClaimRequest(BaseModel):
    asset_id: int
    owner_id: int

@router.post("/submit")
def submit_claim_uganda(request: ClaimRequest):
    # Connect to Uganda-specific DB
    # Placeholder: insert into Uganda assets table
    return {"status": "submitted", "country": "Uganda", "claim": request.dict()}
