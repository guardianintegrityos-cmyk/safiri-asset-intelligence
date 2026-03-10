# Placeholder for Pydantic schemas
# Example: ClaimSchema, OwnerSchema, InstitutionSchema

from pydantic import BaseModel
from datetime import datetime

class ClaimSchema(BaseModel):
    id: int
    claimant_name: str
    asset_type: str
    created_at: datetime

    class Config:
        orm_mode = True

# Add OwnerSchema, InstitutionSchema as needed