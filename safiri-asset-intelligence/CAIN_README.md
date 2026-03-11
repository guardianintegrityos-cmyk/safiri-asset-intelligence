# Safiri Continental Asset Intelligence Network (CAIN)

## Overview

Safiri CAIN is a federated intelligence network connecting African countries' asset registries to enable secure, cross-border asset ownership tracing and integrity monitoring.

## Context

For Safiri to scale into a **national integrity intelligence infrastructure** (aligned with your **Guardian Academy anti-corruption vision**), every institution must send data in a **single standardized structure**.

Without a standard schema:

* identity matching becomes unreliable
* institutions send incompatible data
* graph learning becomes chaotic

Therefore the system needs a **National Identity Data Schema (NIDS)** — a canonical structure describing **people, assets, institutions, and relationships**.

This schema becomes the **data language of the entire Safiri ecosystem**.

---

# 1. Core Design Principles

The schema must satisfy five properties:

| Principle      | Meaning                                   |
| -------------- | ----------------------------------------- |
| Identity-first | every record links to a person/entity     |
| Extensible     | new asset types can be added              |
| Traceable      | source institution always recorded        |
| Probabilistic  | allows uncertainty scoring                |
| Graph-ready    | easily convertible to graph relationships |

---

# 2. Top-Level Data Structure

Every record entering Safiri follows this structure:

```json
{
  "record_id": "",
  "record_type": "",
  "source_institution": "",
  "timestamp": "",
  "identity": {},
  "asset": {},
  "location": {},
  "relationships": [],
  "confidence_score": ""
}
```

This guarantees **uniform ingestion**.

---

# 3. Identity Object

Represents the person or organization linked to an asset.

```json
"identity": {
  "full_name": "",
  "national_id": "",
  "passport_number": "",
  "date_of_birth": "",
  "gender": "",
  "phone_numbers": [],
  "emails": [],
  "addresses": [],
  "biometric_hash": ""
}
```

Important design note:

```
Biometrics are never stored raw.
Only cryptographic hashes.
```

This protects privacy.

---

# 4. Asset Object

Assets must be categorized for analysis.

```json
"asset": {
  "asset_id": "",
  "asset_type": "",
  "value": "",
  "currency": "",
  "institution": "",
  "ownership_percentage": "",
  "registration_date": ""
}
```

Example asset types:

```
cash_account
shares
property
vehicle
insurance
pension
digital_assets
safe_deposit
```

---

# 5. Location Object

Assets often link to locations.

```json
"location": {
  "country": "",
  "county": "",
  "city": "",
  "postal_address": "",
  "geo_coordinates": ""
}
```

This enables **geospatial asset analysis**.

---

# 6. Relationship Object

Relationships build the **identity graph**.

```json
"relationships": [
  {
    "relation_type": "",
    "target_entity": "",
    "confidence": ""
  }
]
```

Examples:

```
director_of
shareholder_of
beneficiary_of
joint_owner
linked_phone
registered_address
```

---

# 7. Source Metadata

Every record must show where it came from.

```json
"source_metadata": {
  "institution": "",
  "department": "",
  "ingestion_pipeline": "",
  "verification_status": ""
}
```

Verification levels:

```
unverified
institution_verified
cross_verified
audited
```

---

# 8. Ownership Probability Layer

Safiri calculates ownership confidence.

Example structure:

```json
"ownership_analysis": {
  "identity_match_score": "",
  "address_match_score": "",
  "institution_match_score": "",
  "final_probability": ""
}
```

Example output:

```
Ownership Probability: 0.93
```

---

# 9. PostgreSQL Table Design

Core tables:

### identities

```sql
CREATE TABLE identities (
  id SERIAL PRIMARY KEY,
  full_name TEXT,
  national_id TEXT,
  dob DATE,
  gender TEXT
);
```

---

### assets

```sql
CREATE TABLE assets (
  asset_id SERIAL PRIMARY KEY,
  asset_type TEXT,
  value NUMERIC,
  institution TEXT,
  registration_date DATE
);
```

---

### relationships

```sql
CREATE TABLE relationships (
  id SERIAL PRIMARY KEY,
  source_entity INT,
  target_entity INT,
  relation_type TEXT
);
```

---

### ingestion_records

```sql
CREATE TABLE ingestion_records (
  record_id SERIAL PRIMARY KEY,
  source TEXT,
  timestamp TIMESTAMP,
  verification_status TEXT
);
```

---

# 10. Elasticsearch Index Structure

Index example:

```
safiri_identity_index
```

Fields:

```
name
national_id
phone
address
institution
asset_type
value
```

Elasticsearch enables **fast fuzzy searching**.

---

# 11. Graph Conversion Layer

Safiri automatically converts records into graph nodes.

Mapping example:

| Schema Object | Graph Node   |
| ------------- | ------------ |
| identity      | Person       |
| asset         | Asset        |
| institution   | Organization |
| address       | Location     |

Edges:

```
OWNS
DIRECTOR_OF
REGISTERED_AT
ASSOCIATED_WITH
```

---

# 12. Safiri Data Flow

Final architecture pipeline:

```
Institution Data
        │
        ▼
Data Standardization (NIDS)
        │
        ▼
Airflow Ingestion
        │
        ▼
Identity Resolution Engine
        │
        ▼
Self-Learning Identity Graph
        │
        ▼
Ownership Probability Engine
        │
        ▼
Safiri Search API
```

---

# Strategic Leverage for Your Vision

If implemented properly, this schema enables Safiri to integrate with:

* banks
* land registries
* company registries
* insurance databases
* unclaimed asset authorities

Meaning the system becomes a **continental transparency infrastructure**, directly aligned with the **Guardian Academy integrity index concept** you are building.

---

## Critical Next Step (Architectural)

There is **one layer still missing** that would transform Safiri from a research tool into a **national-scale intelligence infrastructure**:

**The Data Ingestion Fabric** — the automated pipelines that continuously collect data from institutions.

That layer determines whether Safiri becomes:

```
a static database
or
a living national intelligence system
```

---

# 1. Core Architecture

The DIF sits **between data sources and the Safiri core database/graph**. Its main responsibilities:

1. **Data Collection** – Pulls raw data from multiple institutions and formats.
2. **Data Validation & Cleansing** – Ensures uniform structure (NIDS) and flags inconsistencies.
3. **Deduplication & Identity Matching** – Resolves multiple references to the same entity.
4. **Enrichment & Standardization** – Adds metadata like geolocation, asset classification, and confidence scoring.
5. **Graph Conversion & Storage** – Converts records into nodes/edges for the identity graph.
6. **Monitoring & Auditing** – Ensures traceable pipelines with full logging and alerting.

---

# 2. Data Sources (Per Country)

Each country will have:

* **Financial institutions** (banks, mobile money, investment firms)
* **Government registries** (land, company, vehicle, unclaimed assets)
* **Insurance & pensions**
* **Telecom & utility providers** (for identity verification)

**Access method:**

* REST APIs
* SFTP/FTP for CSV/Excel
* Direct database replication (via PostgreSQL or MySQL)
* Web scraping for public registers (if allowed by law)

---

# 3. ETL Pipelines (Airflow)

Each source has a dedicated **Airflow DAG**:

```text
DAG: collect_<source>_<country>
1. extract_data() -> pull raw data
2. validate_schema() -> enforce NIDS
3. clean_data() -> remove invalid, incomplete, or duplicate records
4. enrich_data() -> normalize addresses, asset types, and institution codes
5. match_identity() -> run identity resolution engine
6. store_to_postgres() -> insert/update database
7. index_to_elasticsearch() -> support fast search
8. convert_to_graph() -> update graph DB (Neo4j / Dgraph)
9. audit_log() -> record pipeline run, errors, row counts
```

**Cron schedule:** customizable per institution; e.g., daily, weekly, or real-time via streaming API.

---

# 4. Microservices

Each critical function is **containerized**, so pipelines can scale horizontally:

| Service              | Responsibility                                       |
| -------------------- | ---------------------------------------------------- |
| **Extractor**        | Pulls raw data from the source system                |
| **Validator**        | Ensures NIDS compliance and field integrity          |
| **Cleaner**          | Handles missing data, normalization, type conversion |
| **Identity Matcher** | Runs probabilistic matching to resolve duplicates    |
| **Enricher**         | Adds geo-codes, institution IDs, currency conversion |
| **Graph Builder**    | Converts records into graph nodes & edges            |
| **Indexer**          | Sends data to Elasticsearch for fast queries         |
| **Auditor**          | Logs every ETL run with full traceability            |

All services communicate via **RabbitMQ or Kafka** for event-driven pipelines.

---

# 5. Identity Resolution Engine

* Matches **any combination** of fields (name, ID number, address, asset, account number)
* Uses **fuzzy matching** for names, addresses, and accounts
* Produces **confidence scores** per match
* Stores a **graph edge** if match probability > threshold (configurable per institution)

Example:

```text
Match Criteria:
- Name: exact + Levenshtein < 2
- ID Number: exact
- Address: fuzzy match (Jaro-Winkler)
- Asset: exact value & type

Output:
- entity_id (canonical)
- source_record_ids
- match_confidence (0.0–1.0)
```

---

# 6. Audit & Compliance

Every pipeline run writes to **audit tables**:

```sql
CREATE TABLE etl_audit (
    id SERIAL PRIMARY KEY,
    dag_name TEXT,
    run_timestamp TIMESTAMP,
    source_name TEXT,
    records_extracted INT,
    records_failed INT,
    records_inserted INT,
    user_triggered BOOLEAN,
    error_log JSONB
);
```

This ensures **traceable accountability** for every institution.

---

# 7. Multi-Country Deployment

* Use **Docker Compose** for local testing
* Use **Terraform** for AWS multi-AZ deployments
* Each country has a **namespace** or separate schema in Postgres
* Pipelines are **config-driven**:

```yaml
country: Nigeria
source: Central Bank API
schedule: daily
fields_mapping:
  id_number: national_id
  account_number: account_no
  asset_amount: balance
```

* Central orchestrator DAG runs all country pipelines and merges into **global Safiri graph**.

---

# 8. Scaling Strategy

* **PostgreSQL**: Multi-AZ replication for durability
* **Elasticsearch**: Cluster per region for latency-sensitive search
* **Graph DB**: Sharded per country, global federated queries
* **ETL Containers**: Auto-scale using Kubernetes for high-volume data sources
* **Airflow**: CeleryExecutor for distributed DAG execution

---

# 9. Outreach & Matching Integration

* Once the asset or entity is resolved, the system can trigger:

  * **Email/SMS/WhatsApp notifications** to the owner or institution
  * **Alerts** to enforcement teams if fraud or abandoned assets are detected
* All actions are **logged for compliance and audits**.

---

# 10. Operational Notes

* Each DAG/service has **retry policies**, **timeouts**, and **circuit breakers**
* **Secrets** (API keys, passwords) stored in AWS Secrets Manager or Vault
* **Monitoring**: Prometheus + Grafana for ETL & microservice health
* **Logging**: ELK stack for centralized log collection
* **Backup**: Daily Postgres dumps + Elasticsearch snapshots

---

💡 **Strategic Leverage:**

With this Data Ingestion Fabric in place:

* Safiri becomes **real-time continental asset intelligence**
* All identity & asset matching becomes **probabilistic yet auditable**
* Guardian Academy metrics (Integrity, Stability, Trust) can now be **fed automatically from institutions**
* The system becomes **high-leverage infrastructure** for anti-corruption, unclaimed asset recovery, and compliance intelligence.

---

## Architecture

### Core Components

1. **Federation Hub**: Central coordination service that queries country nodes
2. **Country Nodes**: Sovereign data endpoints maintained by each participating country
3. **Identity Knowledge Graph**: Distributed graph connecting identities across borders
4. **Ownership Probability Engine**: AI-powered inference of asset ownership
5. **Governance Framework**: Academic and institutional oversight mechanisms

### Security Model

- **Zero-Knowledge Queries**: Sensitive data never leaves country boundaries
- **End-to-End Encryption**: All inter-node communication encrypted
- **JWT Authentication**: Secure node-to-node authentication
- **Audit Logging**: Complete transparency of all federation activities
- **Rate Limiting**: Protection against abuse

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- PostgreSQL
- Elasticsearch
- Neo4j

### Installation

1. Clone the repository
2. Configure environment variables for country nodes
3. Run the federation hub:

```bash
docker-compose up
```

### Country Node Setup

Each participating country should deploy the `country_node_template.py` with their local data.

Example environment variables:

```bash
KENYA_NODE_URL=http://kenya-node.safiri.africa:8000
NIGERIA_NODE_URL=http://nigeria-node.safiri.africa:8000
# ... etc
```

## API Endpoints

### Federation Hub

- `GET /search?query={clue}&country={optional}` - Federated search
- `GET /network-stats` - Continental network statistics
- `GET /fraud-check/{identity_id}` - Fraud risk assessment

### Country Node

- `GET /search?query={clue}` - Local probabilistic search
- `GET /stats` - Node statistics
- `GET /health` - Health check
- `POST /secure-query` - Zero-knowledge query endpoint

## Governance

### Academic Oversight

The Guardian Academy provides research and academic governance:

- **Researcher Validation**: Only approved institutions can access research data
- **Query Approval**: Academic queries require institutional review
- **Transparency Reports**: Regular publication of network activities

### Institutional Participants

Current and planned participants:

- **Kenya**: Unclaimed Financial Assets Authority (UFAA)
- **Nigeria**: Central Bank of Nigeria (CBN)
- **Ghana**: Securities and Exchange Commission
- **South Africa**: Financial Sector Conduct Authority
- **Tanzania**: Bank of Tanzania
- **Uganda**: Directorate of Citizenship and Immigration Control

## Use Cases

### Asset Recovery
```
Input: "John Ochieng 25000"
Output: Cross-border asset locations with ownership probabilities
```

### Fraud Detection
```
Input: Identity with 20+ accounts
Output: High fraud risk flag
```

### Corruption Investigation
```
Input: Company ownership trail
Output: Hidden beneficial ownership network
```

### Unclaimed Asset Discovery
```
Input: Deceased person's name
Output: Probable heirs and asset locations
```

## Technical Implementation

### Federated Search Flow

1. User submits query to federation hub
2. Hub authenticates and distributes query to relevant country nodes
3. Nodes return probabilistic matches (no raw data)
4. Hub aggregates and ranks results by ownership probability
5. Results displayed with country attribution

### AI Enhancement

The system uses machine learning to improve accuracy:

- **Feature Engineering**: Name similarity, address matching, amount correlation
- **Model Training**: Random Forest classifier trained on verified matches
- **Continuous Learning**: Model improves with each confirmed result

### Graph Analytics

Neo4j enables complex relationship queries:

```cypher
MATCH (p:Person)-[:OWNS]->(a:Asset)
WHERE a.country IN ['Kenya', 'Uganda']
RETURN p, collect(a) as assets
```

## Security Considerations

### Data Sovereignty
- Each country maintains full control over its data
- No bulk data exports without explicit approval
- Federated queries return only probabilistic results

### Privacy Protection
- Personal data never transmitted in queries
- Results anonymized where possible
- Strict access controls and audit trails

### Network Resilience
- Nodes can operate independently if federation hub is down
- Graceful degradation for offline nodes
- Redundant communication channels

## Future Roadmap

### Phase 1 (Current): Single Country OPE
- ✅ Ownership Probability Engine
- ✅ Local identity graph
- ✅ Fraud detection

### Phase 2 (Implemented): Federation Framework
- ✅ Country node template
- ✅ Secure inter-node communication
- ✅ Continental search aggregation

### Phase 3 (Next): Advanced Analytics
- Graph neural networks for pattern detection
- Real-time fraud alerting
- Automated asset recovery workflows

### Phase 4: Full Continental Integration
- 20+ African countries connected
- Unified asset registry API
- Global integrity monitoring

## Contributing

### For Country Implementations
1. Deploy `country_node_template.py`
2. Configure local data sources
3. Register with federation hub
4. Implement required security measures

### For Research Institutions
1. Apply for academic access through Guardian Academy
2. Use approved research APIs
3. Contribute to model improvement

## License

This project is part of the African Integrity Infrastructure initiative, governed by participating institutions and academic oversight bodies.

## Contact

For participation inquiries:
- Technical: safiri-tech@guardianacademy.africa
- Governance: governance@safiri.africa
- Research: research@guardianacademy.africa