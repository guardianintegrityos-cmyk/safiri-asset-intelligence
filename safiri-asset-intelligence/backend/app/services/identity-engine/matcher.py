"""
Identity Matcher - Detailed matching algorithms for IRE
"""

from typing import Dict, List
from rapidfuzz import fuzz  # type: ignore
import re

class IdentityMatcher:
    def __init__(self):
        self.name_weights = {
            'exact': 1.0,
            'token_sort': 0.9,
            'partial': 0.7,
            'token_set': 0.6
        }

    def match_names(self, name1: str, name2: str) -> Dict[str, float]:
        """Comprehensive name matching with multiple algorithms"""
        if not name1 or not name2:
            return {'score': 0.0, 'method': 'empty'}

        # Normalize names
        name1_norm = self._normalize_name(name1)
        name2_norm = self._normalize_name(name2)

        # Exact match
        if name1_norm == name2_norm:
            return {'score': 1.0, 'method': 'exact'}

        # Token sort ratio (handles name reordering)
        token_sort = fuzz.token_sort_ratio(name1_norm, name2_norm) / 100.0

        # Partial ratio (handles abbreviations)
        partial = fuzz.partial_ratio(name1_norm, name2_norm) / 100.0

        # Token set ratio (handles extra/missing words)
        token_set = fuzz.token_set_ratio(name1_norm, name2_norm) / 100.0

        # Weighted combination
        score = (
            self.name_weights['token_sort'] * token_sort +
            self.name_weights['partial'] * partial +
            self.name_weights['token_set'] * token_set
        ) / sum(self.name_weights.values())

        # Determine best method
        if token_sort > 0.9:
            method = 'token_sort'
        elif partial > 0.8:
            method = 'partial'
        elif token_set > 0.7:
            method = 'token_set'
        else:
            method = 'low_confidence'

        return {'score': score, 'method': method}

    def _normalize_name(self, name: str) -> str:
        """Normalize name for better matching"""
        if not name:
            return ""

        # Convert to lowercase
        name = name.lower()

        # Remove common titles
        name = re.sub(r'\b(mr|mrs|ms|dr|prof|rev)\.?\s+', '', name)

        # Remove punctuation and extra spaces
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name).strip()

        # Handle common abbreviations
        name = re.sub(r'\bjr\b', 'junior', name)
        name = re.sub(r'\bsr\b', 'senior', name)

        return name

    def match_addresses(self, addr1: str, addr2: str) -> Dict[str, float]:
        """Address matching with postal box handling"""
        if not addr1 or not addr2:
            return {'score': 0.0, 'method': 'empty'}

        # Normalize addresses
        addr1_norm = self._normalize_address(addr1)
        addr2_norm = self._normalize_address(addr2)

        # Exact match
        if addr1_norm == addr2_norm:
            return {'score': 1.0, 'method': 'exact'}

        # Extract postal box numbers
        box1 = self._extract_postal_box(addr1)
        box2 = self._extract_postal_box(addr2)

        if box1 and box2 and box1 == box2:
            return {'score': 0.95, 'method': 'postal_box_match'}

        # Fuzzy matching
        ratio = fuzz.token_sort_ratio(addr1_norm, addr2_norm) / 100.0
        partial = fuzz.partial_ratio(addr1_norm, addr2_norm) / 100.0

        score = max(ratio, partial)

        if score > 0.8:
            method = 'high_similarity'
        elif score > 0.6:
            method = 'medium_similarity'
        else:
            method = 'low_similarity'

        return {'score': score, 'method': method}

    def _normalize_address(self, address: str) -> str:
        """Normalize address for comparison"""
        if not address:
            return ""

        # Convert to lowercase
        address = address.lower()

        # Standardize postal box formats
        address = re.sub(r'p\.?\s*o\.?\s*box', 'po box', address)
        address = re.sub(r'p\.?o\.?\s*b\.?', 'po box', address)

        # Remove punctuation and extra spaces
        address = re.sub(r'[^\w\s]', ' ', address)
        address = re.sub(r'\s+', ' ', address).strip()

        return address

    def _extract_postal_box(self, address: str) -> str:
        """Extract postal box number"""
        if not address:
            return None

        # Match patterns like "PO Box 123", "P.O Box 456", etc.
        match = re.search(r'po\s+box\s+(\d+)', address.lower())
        if match:
            return match.group(1)
        return None

    def match_identifiers(self, id1: str, id2: str) -> Dict[str, float]:
        """Identifier matching (IDs, phone numbers, etc.)"""
        if not id1 or not id2:
            return {'score': 0.0, 'method': 'empty'}

        # Exact match
        if id1 == id2:
            return {'score': 1.0, 'method': 'exact'}

        # For phone numbers, normalize and compare
        if self._is_phone_number(id1) and self._is_phone_number(id2):
            norm1 = self._normalize_phone(id1)
            norm2 = self._normalize_phone(id2)
            if norm1 == norm2:
                return {'score': 1.0, 'method': 'phone_exact'}
            elif norm1 and norm2 and norm1[-8:] == norm2[-8:]:  # Last 8 digits match
                return {'score': 0.9, 'method': 'phone_partial'}

        # For IDs, check if they're numeric and similar length
        if id1.isdigit() and id2.isdigit():
            if len(id1) == len(id2) and len(id1) > 5:
                # Check digit similarity
                matches = sum(1 for a, b in zip(id1, id2) if a == b)
                similarity = matches / len(id1)
                if similarity > 0.9:
                    return {'score': similarity, 'method': 'id_high_similarity'}

        return {'score': 0.0, 'method': 'no_match'}

    def _is_phone_number(self, text: str) -> bool:
        """Check if text looks like a phone number"""
        if not text:
            return False

        # Remove spaces, dashes, parentheses
        clean = re.sub(r'[^\d]', '', text)

        # Check length (African phone numbers typically 9-13 digits)
        return 9 <= len(clean) <= 13

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for comparison"""
        if not phone:
            return ""

        # Remove all non-digits
        clean = re.sub(r'[^\d]', '', phone)

        # Handle country codes
        if len(clean) > 10 and clean.startswith('254'):  # Kenya
            clean = clean[3:]  # Remove country code
        elif len(clean) > 10 and clean.startswith('256'):  # Uganda
            clean = clean[3:]
        elif len(clean) > 10 and clean.startswith('255'):  # Tanzania
            clean = clean[3:]
        elif len(clean) > 10 and clean.startswith('233'):  # Ghana
            clean = clean[3:]
        elif len(clean) > 10 and clean.startswith('27'):   # South Africa
            clean = clean[3:]
        elif len(clean) > 10 and clean.startswith('234'):  # Nigeria
            clean = clean[3:]

        return clean

    def calculate_overall_similarity(self, matches: Dict[str, Dict]) -> float:
        """Calculate overall similarity from individual match scores"""
        weights = {
            'name': 0.4,
            'address': 0.3,
            'id': 0.3
        }

        score = 0.0
        total_weight = 0.0

        for field, match_result in matches.items():
            if field in weights and match_result['score'] > 0:
                score += weights[field] * match_result['score']
                total_weight += weights[field]

        return score / total_weight if total_weight > 0 else 0.0

# Global instance
identity_matcher = IdentityMatcher()