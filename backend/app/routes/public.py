from fastapi import APIRouter
from matching_engine.fuzzy_match import fuzzy_name_match

router = APIRouter()

ASSETS = [
    {"owner_name": "John Kamau", "asset_type": "Bank Account", "id_number": "12345"},
    {"owner_name": "Mary Wanjiku", "asset_type": "Insurance Payout", "id_number": "67890"},
]

@router.get("/search")
def search_assets(name: str):
    matches = []
    for row in ASSETS:
        score = fuzzy_name_match(name, row["owner_name"])
        matches.append({"owner_name": row["owner_name"], "asset_type": row["asset_type"], "confidence": score})
    matches = sorted(matches, key=lambda x: x["confidence"], reverse=True)
    return {"query": name, "matches": matches}
