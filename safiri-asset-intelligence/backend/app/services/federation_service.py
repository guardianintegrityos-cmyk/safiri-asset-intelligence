import urllib.request
import urllib.parse
import json
import os
from typing import List, Dict
from app.schemas import OwnershipCandidateSchema, SearchResultSchema
from app.services.governance_service import governance_service

class FederationService:
    def __init__(self):
        # Country node endpoints - in production, this would be configurable
        self.country_nodes = {
            'kenya': os.getenv('KENYA_NODE_URL', 'http://kenya-node:8000'),
            'nigeria': os.getenv('NIGERIA_NODE_URL', 'http://nigeria-node:8000'),
            'uganda': os.getenv('UGANDA_NODE_URL', 'http://uganda-node:8000'),
            'tanzania': os.getenv('TANZANIA_NODE_URL', 'http://tanzania-node:8000'),
            'ghana': os.getenv('GHANA_NODE_URL', 'http://ghana-node:8000'),
            'south_africa': os.getenv('SOUTH_AFRICA_NODE_URL', 'http://south-africa-node:8000'),
        }
        self.node_tokens = {}  # Cache authentication tokens

    def _get_node_token(self, country: str) -> str:
        """Get or generate authentication token for country node"""
        if country not in self.node_tokens:
            self.node_tokens[country] = governance_service.generate_node_token(country)
        return self.node_tokens[country]

    def query_country_node(self, country: str, query: str) -> Dict:
        """Query a specific country node securely"""
        try:
            url = f"{self.country_nodes[country]}/search"
            token = self._get_node_token(country)

            # Check rate limiting
            if not governance_service.check_rate_limit(country):
                return {"error": "Rate limit exceeded"}

            # Audit the query
            governance_service.audit_log(
                'federation_query',
                'safiri_hub',
                {'country': country, 'query': query}
            )

            # Make authenticated request
            headers = {'Authorization': f'Bearer {token}'}
            req = urllib.request.Request(url + '?' + urllib.parse.urlencode({'query': query}))
            for key, value in headers.items():
                req.add_header(key, value)

            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    return json.loads(response.read().decode('utf-8'))
            except urllib.error.HTTPError as e:
                return {"error": f"Node {country} returned {e.code}"}
            except urllib.error.URLError as e:
                return {"error": f"Failed to query {country}: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error querying {country}: {str(e)}"}

    def federated_search(self, query: str) -> SearchResultSchema:
        """Perform federated search across all country nodes"""
        all_results = []

        # Query all country nodes in parallel (simplified sequential for now)
        for country in self.country_nodes.keys():
            country_result = self.query_country_node(country, query)
            if 'results' in country_result:
                # Add country information to each result
                for result in country_result['results']:
                    result['country'] = country
                    all_results.append(result)

        # Sort by ownership probability across all countries
        all_results.sort(key=lambda x: x.get('ownership_probability', 0), reverse=True)

        # Return top results
        return SearchResultSchema(
            query=query,
            results=all_results[:10]  # Top 10 across continent
        )

    def get_country_statistics(self) -> Dict:
        """Get statistics from all country nodes"""
        stats = {}
        for country, url in self.country_nodes.items():
            try:
                token = self._get_node_token(country)
                headers = {'Authorization': f'Bearer {token}'}
                req = urllib.request.Request(f"{url}/stats")
                for key, value in headers.items():
                    req.add_header(key, value)

                try:
                    with urllib.request.urlopen(req) as response:
                        stats[country] = json.loads(response.read().decode('utf-8'))
                except urllib.error.HTTPError as e:
                    stats[country] = {"error": f"HTTP {e.code}"}
                except urllib.error.URLError as e:
                    stats[country] = {"error": str(e)}
            except:
                stats[country] = {"error": "unavailable"}
        return stats

    def secure_cross_border_merge(self, identity_data: Dict) -> Dict:
        """Perform secure cross-border identity merging"""
        if not governance_service.validate_governance_approval('cross_border_merge'):
            return {"error": "Governance approval required"}

        # Encrypt data for processing
        encrypted_data = governance_service.encrypt_query(identity_data)

        # In production, this would involve multi-party computation
        # For now, return placeholder
        return {"status": "merge_initiated", "encrypted_data": encrypted_data}

federation_service = FederationService()