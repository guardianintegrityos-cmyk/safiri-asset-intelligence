try:
    from fastapi import FastAPI, Depends  # type: ignore
    FASTAPI_AVAILABLE = True
except ImportError:
    # Fallback for when FastAPI is not available
    FASTAPI_AVAILABLE = False

    class FastAPI:
        def __init__(self, title=""):
            self.title = title
            self.routes = []

        def get(self, path):
            def decorator(func):
                self.routes.append(('GET', path, func))
                return func
            return decorator

        def include_router(self, router):
            pass

    class Depends:
        def __init__(self, dependency):
            self.dependency = dependency

from sqlalchemy.orm import Session
from app.database import get_db
from app.matching_engine.matching_engine import search_ownership_probability, detect_fraud
from app.services.federation_service import federation_service
from app.services.identity_engine.api import router as identity_resolution_router

app = FastAPI(title="Safiri Continental Asset Intelligence Network")

# Include routers
if FASTAPI_AVAILABLE:
    app.include_router(identity_resolution_router)

@app.get("/search")
def search_assets(query: str, country: str = None, db: Session = Depends(get_db)):
    """Federated search across African countries"""
    if country and country.lower() in federation_service.country_nodes:
        # Query specific country
        result = federation_service.query_country_node(country.lower(), query)
        return result
    else:
        # Continental search
        result = federation_service.federated_search(query)
        return result

@app.get("/local-search")
def local_search(query: str, db: Session = Depends(get_db)):
    """Local country search (fallback)"""
    result = search_ownership_probability(query, db)
    return result

@app.get("/fraud-check/{identity_id}")
def check_fraud(identity_id: int, db: Session = Depends(get_db)):
    from app.models import IdentityCore
    identity = db.query(IdentityCore).filter(IdentityCore.identity_id == identity_id).first()
    if not identity:
        return {"error": "Identity not found"}
    is_fraud = detect_fraud(identity, db)
    return {"identity_id": identity_id, "fraud_risk": is_fraud}

@app.get("/network-stats")
def get_network_stats():
    """Get statistics from the continental network"""
    return federation_service.get_country_statistics()

@app.get("/")
def root():
    return {"message": "Welcome to Safiri Asset Intelligence API"}