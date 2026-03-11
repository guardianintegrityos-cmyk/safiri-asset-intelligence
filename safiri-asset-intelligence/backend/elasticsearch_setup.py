import elasticsearch

ES_INDEX = "identities"

INDEX_BODY = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "identity_id": {"type": "integer"},
            "full_name": {"type": "text", "analyzer": "standard"},
            "national_id": {"type": "keyword"},
            "postal_address": {"type": "text"},
            "phone": {"type": "keyword"},
            "email": {"type": "keyword"},
            "date_of_birth": {"type": "date"}
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
