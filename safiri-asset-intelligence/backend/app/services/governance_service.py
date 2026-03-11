"""
Safiri Continental Asset Intelligence Network - Governance & Security Module

This module implements the governance framework and security protocols for CAIN,
ensuring sovereign data protection, audit trails, and academic oversight.
"""

import hashlib

try:
    import jwt  # type: ignore
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

    class jwt:
        @staticmethod
        def encode(payload, key, algorithm='HS256'):
            # Simple fallback - not secure for production
            return f"mock_token_{hash(str(payload))}"

        @staticmethod
        def decode(token, key, algorithms=None):
            # Simple fallback
            return {"mock": "payload"}

import datetime
from typing import Dict, List
from cryptography.fernet import Fernet  # type: ignore
import os

class GovernanceService:
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET', 'safiri-secret-key')
        self.encryption_key = Fernet.generate_key()  # In production, load from secure storage
        self.cipher = Fernet(self.encryption_key)

    def authenticate_node(self, node_id: str, token: str) -> bool:
        """Authenticate a country node for federation access"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload.get('node_id') == node_id and payload.get('role') == 'country_node'
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    def generate_node_token(self, node_id: str) -> str:
        """Generate authentication token for a country node"""
        payload = {
            'node_id': node_id,
            'role': 'country_node',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def encrypt_query(self, query_data: Dict) -> str:
        """Encrypt query data for zero-knowledge processing"""
        data_str = str(query_data)
        return self.cipher.encrypt(data_str.encode()).decode()

    def decrypt_response(self, encrypted_data: str) -> Dict:
        """Decrypt response data"""
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return eval(decrypted.decode())  # In production, use safer deserialization

    def audit_log(self, action: str, user: str, details: Dict):
        """Log all federation activities for transparency"""
        timestamp = datetime.datetime.utcnow().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'action': action,
            'user': user,
            'details': details,
            'hash': hashlib.sha256(f"{timestamp}{action}{user}".encode()).hexdigest()
        }
        # In production, store in secure audit database
        print(f"AUDIT: {log_entry}")
        return log_entry

    def check_rate_limit(self, node_id: str) -> bool:
        """Implement rate limiting for queries"""
        # Simple in-memory rate limiting - in production use Redis
        current_time = datetime.datetime.utcnow()
        # Implementation would track queries per node per time window
        return True  # Allow for now

    def validate_governance_approval(self, operation: str) -> bool:
        """Check if operation has required governance approvals"""
        # In production, check against governance database
        critical_operations = ['bulk_data_export', 'cross_border_merge']
        return operation not in critical_operations or self._check_approvals(operation)

    def _check_approvals(self, operation: str) -> bool:
        """Check academic and institutional approvals"""
        # Placeholder for governance workflow
        return True

class AcademicOversight:
    """Guardian Academy oversight integration"""

    def __init__(self):
        self.approved_institutions = [
            'University of Nairobi',
            'Makerere University',
            'University of Cape Town',
            'African Leadership University'
        ]

    def validate_researcher(self, researcher_id: str, institution: str) -> bool:
        """Validate researcher credentials for data access"""
        return institution in self.approved_institutions

    def approve_research_query(self, query: Dict, researcher: Dict) -> bool:
        """Approve research queries under academic oversight"""
        # Check if query is for legitimate research
        research_keywords = ['academic', 'research', 'transparency', 'policy']
        query_str = str(query).lower()
        has_research_purpose = any(keyword in query_str for keyword in research_keywords)

        return has_research_purpose and self.validate_researcher(
            researcher.get('id'), researcher.get('institution')
        )

# Global instances
governance_service = GovernanceService()
academic_oversight = AcademicOversight()