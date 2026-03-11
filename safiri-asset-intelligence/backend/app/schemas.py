try:
    from pydantic import BaseModel  # type: ignore
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

    class BaseModel:
        class Config:
            pass

from datetime import datetime
from typing import List, Optional, Dict, Any

class IdentityCoreSchema(BaseModel):
    identity_id: int
    full_name: str
    national_id: Optional[str]
    postal_address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    date_of_birth: Optional[datetime]

    class Config:
        orm_mode = True

class AssetSchema(BaseModel):
    asset_id: int
    asset_type: str
    institution: str
    account_number: Optional[str]
    amount: Optional[float]
    status: Optional[str]

    class Config:
        orm_mode = True

class IdentityAliasSchema(BaseModel):
    alias_id: int
    name_variations: Optional[str]
    previous_addresses: Optional[str]
    alternative_ids: Optional[str]

    class Config:
        orm_mode = True

class IdentityLinksSchema(BaseModel):
    link_id: int
    linked_identifier: str
    identifier_type: str
    confidence_score: float

    class Config:
        orm_mode = True

class OwnershipCandidateSchema(BaseModel):
    identity: IdentityCoreSchema
    assets: List[AssetSchema]
    aliases: List[IdentityAliasSchema]
    links: List[IdentityLinksSchema]
    ownership_probability: float

class SearchResultSchema(BaseModel):
    query: str
    results: List[OwnershipCandidateSchema]

# Identity Resolution Engine (IRE) Schemas
class IdentityClusterSchema(BaseModel):
    cluster_id: int
    representative_name: str
    representative_address: Optional[str]
    cluster_size: int
    confidence_score: float
    country: Optional[str]
    created_at: datetime
    updated_at: datetime
    validated: bool

    class Config:
        orm_mode = True

class ClusterMemberSchema(BaseModel):
    member_id: int
    identity_id: Optional[int]
    source_table: str
    source_record_id: int
    similarity_score: float
    added_at: datetime

    class Config:
        orm_mode = True

class IdentityResolutionLogSchema(BaseModel):
    log_id: int
    query_hash: str
    query_params: Optional[Dict[str, Any]]
    resolved_cluster_id: Optional[int]
    confidence_score: Optional[float]
    processing_time_ms: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True

class ResolvedIdentitySchema(BaseModel):
    cluster_id: int
    representative_identity: Dict[str, Any]
    cluster_size: int
    confidence_score: float
    all_names: List[str]
    all_addresses: List[str]
    all_identifiers: List[str]
    all_assets: List[Dict[str, Any]]
    validated: bool
    last_updated: datetime

class IdentityQuerySchema(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    identifier: Optional[str] = None
    country: Optional[str] = None
    search_radius: Optional[int] = 50

class ResolutionResultSchema(BaseModel):
    resolved_identity: ResolvedIdentitySchema
    confidence_score: float
    cluster_size: int
    matched_records: List[Dict[str, Any]]
    ownership_probabilities: List[Dict[str, Any]]
    processing_time_ms: float

class ClusterStatisticsSchema(BaseModel):
    total_clusters: int
    average_cluster_size: float
    average_confidence: float
    validated_clusters: int
    country_breakdown: Dict[str, int]
    last_updated: datetime