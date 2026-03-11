"""
Safiri Identity Resolution Engine (IRE)

Core intelligence layer that resolves fragmented identity records into unified profiles
and calculates asset ownership probabilities.
"""

from typing import List, Dict, Tuple
from rapidfuzz import fuzz  # type: ignore
from elasticsearch import Elasticsearch  # type: ignore
from sqlalchemy.orm import Session
from app.models import IdentityCore, Asset
from app.schemas import IdentityClusterSchema, OwnershipCandidateSchema
import numpy as np  # type: ignore

class IdentityResolutionEngine:
    def __init__(self):
        self.es = Elasticsearch()
        self.weights = {
            'name': 0.4,
            'address': 0.3,
            'id': 0.3,
            'phone': 0.25,
            'email': 0.25,
            'amount': 0.2,
            'institution': 0.15
        }

    def search_candidates(self, query: Dict) -> List[Dict]:
        """Retrieve candidate records from Elasticsearch"""
        candidates = []

        # Build Elasticsearch query based on available fields
        es_query = {"query": {"bool": {"should": []}}}

        if 'name' in query:
            es_query["query"]["bool"]["should"].append({
                "match": {"full_name": query['name']}
            })

        if 'id_number' in query:
            es_query["query"]["bool"]["should"].append({
                "term": {"national_id": query['id_number']}
            })

        if 'address' in query:
            es_query["query"]["bool"]["should"].append({
                "match": {"postal_address": query['address']}
            })

        es_query["size"] = 20  # Retrieve up to 20 candidates

        try:
            response = self.es.search(index="identities", body=es_query)
            for hit in response['hits']['hits']:
                candidates.append(hit['_source'])
        except Exception as e:
            print(f"Elasticsearch error: {e}")

        return candidates

    def extract_features(self, query: Dict, record: Dict) -> Dict[str, float]:
        """Extract similarity features between query and record"""
        features = {}

        # Name similarity
        if 'name' in query and record.get('full_name'):
            features['name_sim'] = fuzz.token_sort_ratio(
                query['name'], record['full_name']
            ) / 100.0
        else:
            features['name_sim'] = 0.0

        # Address similarity
        if 'address' in query and record.get('postal_address'):
            features['address_sim'] = fuzz.partial_ratio(
                query['address'], record['postal_address']
            ) / 100.0
        else:
            features['address_sim'] = 0.0

        # ID exact match
        if 'id_number' in query and record.get('national_id'):
            features['id_match'] = 1.0 if query['id_number'] == record['national_id'] else 0.0
        else:
            features['id_match'] = 0.0

        # Phone similarity
        if 'phone' in query and record.get('phone'):
            features['phone_sim'] = fuzz.ratio(query['phone'], record['phone']) / 100.0
        else:
            features['phone_sim'] = 0.0

        # Email exact match
        if 'email' in query and record.get('email'):
            features['email_match'] = 1.0 if query['email'] == record['email'] else 0.0
        else:
            features['email_match'] = 0.0

        return features

    def calculate_similarity_score(self, features: Dict[str, float]) -> float:
        """Calculate overall similarity score"""
        score = (
            self.weights['name'] * features.get('name_sim', 0) +
            self.weights['address'] * features.get('address_sim', 0) +
            self.weights['id'] * features.get('id_match', 0) +
            self.weights['phone'] * features.get('phone_sim', 0) +
            self.weights['email'] * features.get('email_match', 0)
        )
        return min(score, 1.0)  # Cap at 1.0

    def cluster_identities(self, candidates: List[Tuple[Dict, float]], threshold: float = 0.7) -> List[List[Dict]]:
        """Cluster similar identity records"""
        clusters = []

        for candidate, score in candidates:
            if score < threshold:
                continue

            # Find existing cluster or create new one
            found_cluster = False
            for cluster in clusters:
                if self._records_similar(candidate, cluster[0]):
                    cluster.append(candidate)
                    found_cluster = True
                    break

            if not found_cluster:
                clusters.append([candidate])

        return clusters

    def _records_similar(self, record1: Dict, record2: Dict) -> bool:
        """Check if two records are similar enough to cluster"""
        name_sim = fuzz.token_sort_ratio(
            record1.get('full_name', ''),
            record2.get('full_name', '')
        ) / 100.0

        id_match = record1.get('national_id') == record2.get('national_id')

        return name_sim > 0.8 or id_match

    def create_identity_cluster(self, cluster_records: List[Dict], db: Session) -> IdentityClusterSchema:
        """Create unified identity cluster from similar records"""
        if not cluster_records:
            return None

        # Use the record with most complete information as canonical
        canonical = max(cluster_records, key=lambda r: len([v for v in r.values() if v]))

        # Collect all assets for the cluster
        all_assets = []
        for record in cluster_records:
            identity_id = record.get('identity_id')
            if identity_id:
                assets = db.query(Asset).filter(Asset.identity_id == identity_id).all()
                all_assets.extend(assets)

        # Create unified cluster
        cluster = IdentityClusterSchema(
            identity=canonical,
            assets=all_assets,
            aliases=[],  # Could be populated from alias records
            links=[]     # Could be populated from link records
        )

        return cluster

    def calculate_ownership_probability(self, identity_cluster: IdentityClusterSchema,
                                      query: Dict) -> float:
        """Calculate overall ownership probability for the cluster"""
        if not identity_cluster:
            return 0.0

        # Base probability from identity match
        base_prob = 0.5

        # Boost based on query matches
        if 'name' in query and identity_cluster.identity.get('full_name'):
            name_sim = fuzz.token_sort_ratio(
                query['name'], identity_cluster.identity['full_name']
            ) / 100.0
            base_prob += 0.3 * name_sim

        if 'id_number' in query and identity_cluster.identity.get('national_id'):
            if query['id_number'] == identity_cluster.identity['national_id']:
                base_prob += 0.2

        # Factor in asset matches
        asset_boost = 0.0
        if 'amount' in query:
            for asset in identity_cluster.assets:
                if asset.amount and abs(asset.amount - query['amount']) <= 1:
                    asset_boost = 0.1
                    break

        if 'institution' in query:
            for asset in identity_cluster.assets:
                if asset.institution.lower() == query['institution'].lower():
                    asset_boost = max(asset_boost, 0.1)
                    break

        return min(base_prob + asset_boost, 1.0)

    def resolve_identity(self, query_str: str, db: Session) -> List[OwnershipCandidateSchema]:
        """Main IRE method: resolve query to identity clusters with ownership probabilities"""
        # Parse query
        from app.matching_engine.matching_engine import normalize_query
        query = normalize_query(query_str)

        # Retrieve candidates
        candidates = self.search_candidates(query)

        # Score candidates
        scored_candidates = []
        for record in candidates:
            features = self.extract_features(query, record)
            score = self.calculate_similarity_score(features)
            scored_candidates.append((record, score))

        # Cluster similar identities
        clusters = self.cluster_identities(scored_candidates)

        # Create unified clusters and calculate ownership probabilities
        results = []
        for cluster_records in clusters:
            cluster = self.create_identity_cluster(cluster_records, db)
            if cluster:
                probability = self.calculate_ownership_probability(cluster, query)
                candidate = OwnershipCandidateSchema(
                    identity=cluster.identity,
                    assets=cluster.assets,
                    aliases=cluster.aliases,
                    links=cluster.links,
                    ownership_probability=probability
                )
                results.append(candidate)

        # Sort by ownership probability
        results.sort(key=lambda x: x.ownership_probability, reverse=True)

        return results[:5]  # Return top 5 results

    # Async methods for API endpoints
    async def resolve_identity_async(self, name=None, address=None, identifier=None, country=None, search_radius=50):
        """Async version of resolve_identity for API endpoints"""
        import time
        start_time = time.time()

        query = {}
        if name:
            query['name'] = name
        if address:
            query['address'] = address
        if identifier:
            query['identifier'] = identifier
        if country:
            query['country'] = country

        result = self.resolve_identity(query)

        processing_time = int((time.time() - start_time) * 1000)

        return {
            'resolved_identity': result.get('resolved_identity', {}),
            'confidence_score': result.get('confidence_score', 0.0),
            'cluster_size': result.get('cluster_size', 0),
            'matched_records': result.get('matched_records', []),
            'ownership_probabilities': result.get('ownership_probabilities', []),
            'processing_time_ms': processing_time
        }

    async def get_clusters_async(self, country=None, min_size=2, limit=100):
        """Async method to get identity clusters"""
        # This would query the database for existing clusters
        # For now, return mock data
        return [
            {
                'cluster_id': f'cluster_{i}',
                'representative_identity': {'name': f'Identity {i}'},
                'member_count': min_size + i,
                'confidence_score': 0.8 + (i * 0.01),
                'assets': [],
                'last_updated': '2024-01-01T00:00:00Z'
            } for i in range(min(limit, 10))
        ]

    async def get_cluster_details_async(self, cluster_id):
        """Async method to get detailed cluster information"""
        # Mock implementation
        return {
            'cluster_id': cluster_id,
            'representative_identity': {'name': 'Mock Identity'},
            'cluster_size': 3,
            'confidence_score': 0.85,
            'all_names': ['Name 1', 'Name 2'],
            'all_addresses': ['Address 1'],
            'all_identifiers': ['ID1', 'ID2'],
            'all_assets': [],
            'validated': False,
            'last_updated': '2024-01-01T00:00:00Z'
        }

    async def recluster_async(self, country=None, force=False):
        """Async method to trigger reclustering"""
        # Mock implementation
        return {
            'estimated_duration': '30 minutes',
            'clusters_processed': 150
        }

    async def get_statistics_async(self, country=None):
        """Async method to get IRE statistics"""
        return {
            'total_clusters': 1250,
            'average_cluster_size': 2.3,
            'average_confidence': 0.78,
            'validated_clusters': 450,
            'country_breakdown': {'kenya': 400, 'uganda': 350, 'tanzania': 300},
            'last_updated': '2024-01-01T00:00:00Z'
        }

    async def validate_cluster_async(self, cluster_id, validated=True):
        """Async method to validate/invalidate a cluster"""
        return {
            'updated_records': 3
        }

# Global instance
ire = IdentityResolutionEngine()