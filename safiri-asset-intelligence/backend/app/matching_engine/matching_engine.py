from sqlalchemy.orm import Session
from app.models import IdentityCore, Asset, IdentityAlias, IdentityLinks
from app.schemas import OwnershipCandidateSchema, SearchResultSchema

try:
    from elasticsearch import Elasticsearch  # type: ignore
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False

    class Elasticsearch:
        def __init__(self, hosts=None):
            pass

        def search(self, **kwargs):
            return {"hits": {"hits": []}}

from .fuzzy_match import fuzzy_name_match
from typing import List, Optional

# Initialize Elasticsearch with configuration
try:
    if ELASTICSEARCH_AVAILABLE:
        try:
            es = Elasticsearch(hosts=["localhost:9200"])
        except Exception:
            # If local Elasticsearch is not available, use mock
            class MockElasticsearch:
                def search(self, **kwargs):
                    return {"hits": {"hits": []}}
            es = MockElasticsearch()
    else:
        es = Elasticsearch()
except Exception:
    # Fallback to mock Elasticsearch
    class MockElasticsearch:
        def search(self, **kwargs):
            return {"hits": {"hits": []}}
    es = MockElasticsearch()

WEIGHTS = {
    'id_number': 0.9,
    'account': 0.85,
    'name': 0.7,
    'address': 0.6,
    'phone': 0.65,
    'email': 0.65,
    'amount': 0.5,
    'institution': 0.4
}

def normalize_query(query_str: str) -> dict:
    """Smart query parser that detects input types"""
    query = {}
    parts = query_str.split()

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # National ID: 8 digits
        if part.isdigit() and len(part) == 8:
            query['id_number'] = part
        # Account number: >10 digits
        elif part.isdigit() and len(part) > 10:
            query['account'] = part
        # Amount: number with possible commas/decimals
        elif part.replace(',', '').replace('.', '').isdigit():
            query['amount'] = float(part.replace(',', ''))
        # Email: contains @
        elif '@' in part:
            query['email'] = part
        # Phone: starts with + or country code
        elif part.startswith('+') or (part.startswith('0') and len(part) >= 10):
            query['phone'] = part
        # Address: contains common address keywords
        elif any(keyword in part.lower() for keyword in ['p.o', 'box', 'street', 'avenue', 'road']):
            query['address'] = part
        # Name: default to name
        else:
            query['name'] = part if 'name' not in query else query['name'] + ' ' + part

    return query

def retrieve_candidates(query: dict, db: Session) -> List[IdentityCore]:
    """Use Elasticsearch to find candidate identities"""
    candidates = []
    if 'name' in query:
        es_query = {
            "query": {
                "match": {
                    "full_name": query['name']
                }
            },
            "size": 10
        }
        res = es.search(index="identities", body=es_query)
        for hit in res['hits']['hits']:
            identity_id = hit['_source']['identity_id']
            identity = db.query(IdentityCore).filter(IdentityCore.identity_id == identity_id).first()
            if identity:
                candidates.append(identity)
    else:
        # If no name, get all identities (for amount/account matches)
        candidates = db.query(IdentityCore).all()
    return candidates

from app.matching_engine.ai_service import ai_service

def calculate_ownership_score(candidate: IdentityCore, query: dict, db: Session) -> float:
    """Calculate ownership probability score using AI model"""
    name_sim = 0.0
    address_sim = 0.0
    amount_match = 0.0
    institution_match = 0.0
    id_match = 0.0
    account_match = 0.0

    # Calculate similarities
    if 'name' in query:
        name_sim = fuzzy_name_match(query['name'], candidate.full_name) / 100.0

    if 'address' in query and candidate.postal_address:
        address_sim = fuzzy_name_match(query['address'], candidate.postal_address) / 100.0

    if 'amount' in query:
        assets = db.query(Asset).filter(Asset.identity_id == candidate.identity_id).all()
        for asset in assets:
            if asset.amount and abs(asset.amount - query['amount']) <= 1:
                amount_match = 1.0
                break

    if 'institution' in query:
        assets = db.query(Asset).filter(Asset.identity_id == candidate.identity_id).all()
        for asset in assets:
            if asset.institution.lower() == query['institution'].lower():
                institution_match = 1.0
                break

    if 'id_number' in query and candidate.national_id == query['id_number']:
        id_match = 1.0

    if 'account' in query:
        assets = db.query(Asset).filter(Asset.identity_id == candidate.identity_id).all()
        for asset in assets:
            if asset.account_number == query['account']:
                account_match = 1.0
                break

    # Use AI model for prediction
    features = [name_sim, address_sim, amount_match, institution_match, id_match, account_match]
    probability = ai_service.predict_probability(features)

    return min(probability, 1.0)

def build_ownership_candidate(identity: IdentityCore, probability: float, db: Session) -> OwnershipCandidateSchema:
    assets = db.query(Asset).filter(Asset.identity_id == identity.identity_id).all()
    aliases = db.query(IdentityAlias).filter(IdentityAlias.identity_id == identity.identity_id).all()
    links = db.query(IdentityLinks).filter(IdentityLinks.identity_id == identity.identity_id).all()
    return OwnershipCandidateSchema(
        identity=identity,
        assets=assets,
        aliases=aliases,
        links=links,
        ownership_probability=probability
    )

def detect_fraud(identity: IdentityCore, db: Session) -> bool:
    """Simple fraud detection: too many assets"""
    asset_count = db.query(Asset).filter(Asset.identity_id == identity.identity_id).count()
    return asset_count > 10  # Arbitrary threshold

def search_ownership_probability(query_str: str, db: Session) -> SearchResultSchema:
    query = normalize_query(query_str)
    candidates = retrieve_candidates(query, db)

    scored_candidates = []
    for candidate in candidates:
        score = calculate_ownership_score(candidate, query, db)
        if score > 0.1:  # Threshold for inclusion
            candidate_schema = build_ownership_candidate(candidate, score, db)
            scored_candidates.append(candidate_schema)

    # Sort by probability descending
    scored_candidates.sort(key=lambda x: x.ownership_probability, reverse=True)

    return SearchResultSchema(query=query_str, results=scored_candidates[:5])  # Top 5
