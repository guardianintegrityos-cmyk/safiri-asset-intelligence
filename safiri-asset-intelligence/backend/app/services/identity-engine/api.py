"""
Identity Resolution Engine API - REST endpoints for IRE functionality
"""

try:
    from fastapi import APIRouter, HTTPException, Query  # type: ignore
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    class APIRouter:
        def __init__(self, prefix="", tags=None):
            self.prefix = prefix
            self.tags = tags or []
            self.routes = []

        def post(self, path):
            def decorator(func):
                self.routes.append(('POST', path, func))
                return func
            return decorator

        def get(self, path):
            def decorator(func):
                self.routes.append(('GET', path, func))
                return func
            return decorator

    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            self.status_code = status_code
            self.detail = detail

    class Query:
        def __init__(self, default=None, description=""):
            self.default = default
            self.description = description

from typing import List, Dict, Optional
from pydantic import BaseModel

from .engine import identity_resolution_engine
from ..governance_service import governance_service

router = APIRouter(prefix="/identity-resolution", tags=["Identity Resolution"])

class IdentityQuery(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    identifier: Optional[str] = None
    country: Optional[str] = None
    search_radius: Optional[int] = 50  # km for location-based search

class ResolutionResult(BaseModel):
    resolved_identity: Dict
    confidence_score: float
    cluster_size: int
    matched_records: List[Dict]
    ownership_probabilities: List[Dict]
    processing_time_ms: float

class ClusterResult(BaseModel):
    cluster_id: str
    representative_identity: Dict
    member_count: int
    confidence_score: float
    assets: List[Dict]
    last_updated: str

@router.post("/resolve", response_model=ResolutionResult)
async def resolve_identity(query: IdentityQuery):
    """
    Resolve a fragmented identity into a unified profile
    """
    try:
        # Governance check
        governance_service.log_request("identity_resolution", {
            "query": query.dict(),
            "endpoint": "resolve"
        })

        # Perform identity resolution
        result = await identity_resolution_engine.resolve_identity_async(
            name=query.name,
            address=query.address,
            identifier=query.identifier,
            country=query.country,
            search_radius=query.search_radius
        )

        return ResolutionResult(**result)

    except Exception as e:
        governance_service.log_error("identity_resolution_error", str(e))
        raise HTTPException(status_code=500, detail=f"Identity resolution failed: {str(e)}")

@router.get("/clusters", response_model=List[ClusterResult])
async def get_identity_clusters(
    country: Optional[str] = Query(None, description="Filter by country"),
    min_size: Optional[int] = Query(2, description="Minimum cluster size"),
    limit: Optional[int] = Query(100, description="Maximum number of clusters to return")
):
    """
    Get all identity clusters
    """
    try:
        governance_service.log_request("get_clusters", {
            "country": country,
            "min_size": min_size,
            "limit": limit
        })

        clusters = await identity_resolution_engine.get_clusters_async(
            country=country,
            min_size=min_size,
            limit=limit
        )

        return [ClusterResult(**cluster) for cluster in clusters]

    except Exception as e:
        governance_service.log_error("get_clusters_error", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve clusters: {str(e)}")

@router.get("/cluster/{cluster_id}", response_model=ClusterResult)
async def get_cluster_details(cluster_id: str):
    """
    Get detailed information about a specific identity cluster
    """
    try:
        governance_service.log_request("get_cluster_details", {"cluster_id": cluster_id})

        cluster = await identity_resolution_engine.get_cluster_details_async(cluster_id)

        if not cluster:
            raise HTTPException(status_code=404, detail="Cluster not found")

        return ClusterResult(**cluster)

    except HTTPException:
        raise
    except Exception as e:
        governance_service.log_error("get_cluster_details_error", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve cluster details: {str(e)}")

@router.post("/recluster")
async def trigger_reclustering(
    country: Optional[str] = Query(None, description="Country to recluster"),
    force: bool = Query(False, description="Force full reclustering")
):
    """
    Trigger reclustering of identities (admin operation)
    """
    try:
        # Check governance permissions (admin only)
        governance_service.log_request("recluster", {
            "country": country,
            "force": force
        })

        # This would typically require admin authentication
        result = await identity_resolution_engine.recluster_async(
            country=country,
            force=force
        )

        return {
            "message": "Reclustering initiated",
            "estimated_duration": result.get("estimated_duration", "Unknown"),
            "clusters_processed": result.get("clusters_processed", 0)
        }

    except Exception as e:
        governance_service.log_error("recluster_error", str(e))
        raise HTTPException(status_code=500, detail=f"Reclustering failed: {str(e)}")

@router.get("/statistics")
async def get_resolution_statistics(
    country: Optional[str] = Query(None, description="Filter by country")
):
    """
    Get statistics about identity resolution performance
    """
    try:
        governance_service.log_request("get_statistics", {"country": country})

        stats = await identity_resolution_engine.get_statistics_async(country=country)

        return stats

    except Exception as e:
        governance_service.log_error("get_statistics_error", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")

@router.post("/validate/{cluster_id}")
async def validate_cluster(cluster_id: str, validated: bool = Query(True)):
    """
    Mark a cluster as validated or invalid
    """
    try:
        governance_service.log_request("validate_cluster", {
            "cluster_id": cluster_id,
            "validated": validated
        })

        result = await identity_resolution_engine.validate_cluster_async(
            cluster_id=cluster_id,
            validated=validated
        )

        return {
            "message": f"Cluster {cluster_id} {'validated' if validated else 'marked as invalid'}",
            "updated_records": result.get("updated_records", 0)
        }

    except Exception as e:
        governance_service.log_error("validate_cluster_error", str(e))
        raise HTTPException(status_code=500, detail=f"Cluster validation failed: {str(e)}")

# Include router in main app
identity_resolution_router = router