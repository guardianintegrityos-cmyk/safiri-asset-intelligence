try:
    from rapidfuzz import fuzz  # type: ignore
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

    class fuzz:
        @staticmethod
        def ratio(s1, s2):
            # Simple fallback similarity calculation
            if not s1 or not s2:
                return 0
            s1, s2 = s1.lower(), s2.lower()
            if s1 == s2:
                return 100
            # Simple character overlap ratio
            set1, set2 = set(s1), set(s2)
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            return int((intersection / union) * 100) if union > 0 else 0

def fuzzy_name_match(name1: str, name2: str) -> int:
    """
    Returns a confidence score 0-100 for name similarity
    """
    return fuzz.ratio(name1.lower(), name2.lower())
