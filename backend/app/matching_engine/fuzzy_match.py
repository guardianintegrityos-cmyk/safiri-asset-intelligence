from rapidfuzz import fuzz

def fuzzy_name_match(name1: str, name2: str) -> int:
    """
    Returns a confidence score 0-100 for name similarity
    """
    return fuzz.ratio(name1.lower(), name2.lower())
