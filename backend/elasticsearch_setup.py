import elasticsearch

ES_INDEX = "claims"

INDEX_BODY = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "asset_type": {"type": "keyword"},
            "asset_id": {"type": "keyword"},
            "claimant_name": {"type": "text"},
            "created_at": {"type": "date"},
            "owner_id": {"type": "integer"},
            "institution_id": {"type": "integer"},
            "institution_country": {"type": "keyword"}
        }
    }
}

def setup_index(es_url="http://localhost:9200"):
    es = elasticsearch.Elasticsearch(es_url)
    if not es.indices.exists(index=ES_INDEX):
        es.indices.create(index=ES_INDEX, body=INDEX_BODY)
        print(f"Created index: {ES_INDEX}")
    else:
        print(f"Index {ES_INDEX} already exists.")

if __name__ == "__main__":
    setup_index()
