# Placeholder for users routes
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_users():
    # TODO: Fetch users from DB
    return {"users": []}
