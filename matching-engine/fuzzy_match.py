from rapidfuzz import fuzz

def fuzzy_name_match(name1: str, name2: str) -> float:
    """
    Returns a similarity score between 0-100
    """
    return fuzz.token_sort_ratio(name1.lower(), name2.lower())
