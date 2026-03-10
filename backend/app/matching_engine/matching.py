# matching.py
from rapidfuzz import fuzz
from elasticsearch import Elasticsearch

def match_records(data):
    es = Elasticsearch()
    matches = []
    for record in data['records']:
        # Example: exact ID match
        if record['id'] == data['query']['id']:
            matches.append({'score': 100, 'record': record})
        else:
            # Fuzzy name match
            score = fuzz.token_sort_ratio(record['name'], data['query']['name'])
            if score >= 85:
                matches.append({'score': 85, 'record': record})
            elif score >= 60:
                matches.append({'score': 60, 'record': record})
    return matches
