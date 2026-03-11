
# Safiri Continental Asset Intelligence Network (CAIN)

This repository implements the **Continental Asset Intelligence Network (CAIN)** - a federated system connecting African countries' asset registries for secure, cross-border asset ownership tracing and integrity monitoring.

## Vision

**If an asset exists anywhere in Africa, Safiri should be able to trace the probable owner.**

CAIN transforms isolated national registries into a unified intelligence network while preserving data sovereignty.

---

## Architecture Overview

### Four-Layer Intelligence System

```
User Query
    │
    ▼
Smart Query Parser          ← Intelligent input detection
    │
    ▼
Identity Knowledge Graph    ← Distributed cross-border graph
    │
    ▼
Ownership Probability Engine ← AI-powered inference
    │
    ▼
Ranked Ownership Results    ← Continental search results
```

### Federated Security Model

- **Zero-Knowledge Queries**: Sensitive data never leaves country boundaries
- **End-to-End Encryption**: All inter-node communication secured
- **Academic Governance**: Guardian Academy oversight
- **Sovereign Data Control**: Each country maintains full authority

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL, Elasticsearch, Neo4j

### Launch Federation Hub

```bash
# Clone repository
git clone <repository-url>
cd safiri-asset-intelligence

# Start continental network
docker-compose up
```

### Access Interfaces
- **Frontend**: http://localhost:3000 (Continental search interface)
- **API**: http://localhost:8000 (Federation hub)
- **Network Stats**: http://localhost:8000/network-stats

---

## Repository Structure

```
safiri-asset-intelligence/
├─ backend/
│  ├─ app/
│  │  ├─ services/
│  │  │  ├─ federation_service.py     ← Continental coordination
│  │  │  ├─ governance_service.py     ← Academic oversight
│  │  │  └─ graph_service.py          ← Neo4j integration
│  │  ├─ matching_engine/
│  │  │  ├─ ai_service.py             ← ML ownership scoring
│  │  │  └─ matching_engine.py        ← OPE implementation
│  │  ├─ country_node_template.py     ← Node deployment template
│  │  └─ main.py                      ← Federation API
├─ frontend/                          ← Continental search UI
├─ etl-pipelines/                     ← Cross-border data ingestion
├─ CAIN_README.md                     ← Detailed technical docs
└─ docker-compose.yml                 ← Multi-service orchestration
```

---

## Key Features

### 🔍 Continental Search
Search across all participating African countries simultaneously.

```javascript
// Example: Find assets for "John Ochieng"
{
  "query": "John Ochieng",
  "results": [
    {
      "name": "John Ochieng",
      "country": "kenya",
      "ownership_probability": 0.92,
      "assets": [...]
    },
    {
      "name": "John Ochieng Odhiambo",
      "country": "uganda",
      "ownership_probability": 0.64
    }
  ]
}
```

### 🛡️ Security & Governance
- **JWT Authentication** between federation nodes
- **Audit Logging** of all cross-border queries
- **Rate Limiting** and abuse prevention
- **Academic Oversight** through Guardian Academy

### 🤖 AI-Powered Intelligence
- **Machine Learning** ownership probability scoring
- **Graph Analytics** for relationship discovery
- **Fraud Detection** across borders
- **Continuous Learning** from verified results

### 🌍 Country Participation
Current framework supports:
- **Kenya** (UFAA integration)
- **Nigeria** (CBN integration)
- **Ghana, Tanzania, Uganda, South Africa** (Framework ready)

---

## API Usage

### Federated Search
```bash
# Search entire continent
curl "http://localhost:8000/search?query=John%20Ochieng"

# Search specific country
curl "http://localhost:8000/search?query=John%20Ochieng&country=kenya"
```

### Network Monitoring
```bash
# Get continental statistics
curl "http://localhost:8000/network-stats"
```

### Country Node Deployment
Each participating country deploys:

```python
# From country_node_template.py
app = FastAPI(title=f"Safiri Node - {COUNTRY_NAME}")

@app.get("/search")
def search_assets(query: str, db: Session = Depends(get_db)):
    # Local probabilistic search
    return search_ownership_probability(query, db)
```

---

## Use Cases

### Asset Recovery
- **Lost Inheritance**: Find unclaimed assets for deceased relatives
- **Divorce Settlements**: Locate hidden marital assets
- **Bankruptcy Proceedings**: Identify all debtor holdings

### Integrity Monitoring
- **Corruption Detection**: Trace illicit wealth networks
- **Fraud Prevention**: Cross-border suspicious activity alerts
- **Policy Research**: Academic studies on asset distribution

### Financial Inclusion
- **Unclaimed Assets**: Connect owners with lost funds
- **Investment Tracking**: Monitor portfolio across jurisdictions
- **Estate Planning**: Comprehensive wealth visibility

---

## Governance Framework

### Academic Oversight
- **Guardian Academy** provides research governance
- **Institutional Approval** required for sensitive queries
- **Transparency Reports** published quarterly

### Technical Governance
- **Open Source** core algorithms
- **Peer Review** of AI models
- **Independent Auditing** of security measures

---

## Development Roadmap

### Phase 1 ✅ (Current): Foundation
- Ownership Probability Engine
- Local identity graphs
- Basic federation framework

### Phase 2 🔄 (Active): Continental Integration
- Multi-country node deployment
- Secure inter-node communication
- Continental search aggregation

### Phase 3 📋 (Next): Advanced Analytics
- Graph neural networks
- Real-time fraud detection
- Automated recovery workflows

### Phase 4 🎯 (Future): Global Impact
- 20+ African countries
- Unified continental API
- International cooperation

---

## Contributing

### For Countries
1. Deploy `country_node_template.py`
2. Configure local asset registries
3. Register with federation hub
4. Participate in governance framework

### For Researchers
1. Apply through Guardian Academy
2. Use approved research endpoints
3. Contribute to model validation

### For Developers
1. Fork and create feature branches
2. Follow security guidelines
3. Submit PRs with test coverage

---

## Security Notice

CAIN implements **bank-grade security**:
- End-to-end encryption
- Zero-trust architecture
- Comprehensive audit trails
- Academic governance oversight

All data remains under sovereign control of participating countries.

---

## Contact & Support

- **Technical Implementation**: safiri-tech@guardianacademy.africa
- **Country Participation**: countries@safiri.africa
- **Research Collaboration**: research@guardianacademy.africa
- **Governance**: governance@safiri.africa

---

## License

Part of the African Integrity Infrastructure initiative. Governed by participating institutions and academic oversight bodies.
│  │  ├─ services/ (matching engine, outreach, verification)
│  │  ├─ core.py (FastAPI app)
│  │  └─ config.py (DB connections, env vars)
├─ etl/
│  ├─ kenya_dag.py
│  ├─ uganda_dag.py
│  ├─ tanzania_dag.py
│  └─ nigeria_dag.py
├─ frontend/
│  ├─ src/
│  │  ├─ components/
│  │  ├─ pages/
│  │  └─ App.js
│  ├─ package.json
│  └─ tailwind.config.js
├─ terraform/
│  ├─ main.tf
│  ├─ variables.tf
│  └─ outputs.tf
├─ docker-compose.yml
└─ README.md
```

---

## Backend

* **FastAPI** with multi-country endpoints
* Matching engine microservices in `services/`
* B2B API with throttling and auth

### Example core.py

```python
from fastapi import FastAPI
from routes.kenya.claims import router as kenya_claims
from routes.uganda.claims import router as uganda_claims
from routes.tanzania.claims import router as tanzania_claims
from routes.nigeria.claims import router as nigeria_claims
from routes.b2b import router as b2b_router

app = FastAPI(title="Safiri Asset Intelligence")

app.include_router(kenya_claims, prefix="/kenya/claims")
app.include_router(uganda_claims, prefix="/uganda/claims")
app.include_router(tanzania_claims, prefix="/tanzania/claims")
app.include_router(nigeria_claims, prefix="/nigeria/claims")
app.include_router(b2b_router, prefix="/b2b")
```

---

## ETL Pipelines (Airflow DAGs)

* Daily ingestion per country
* UFAA, bank, insurer, and public enrichment sources

### Example Nigeria DAG

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from pipelines.nigeria_ingest import ingest_ufaa, ingest_bank, ingest_insurer

default_args = {
		'owner': 'safiri',
		'depends_on_past': False,
		'retries': 1,
		'retry_delay': timedelta(minutes=10)
}

dag = DAG('safiri_nigeria_etl', default_args=default_args, schedule_interval='@daily', start_date=datetime(2026,3,1))

t1 = PythonOperator(task_id='ufaa_ingest', python_callable=ingest_ufaa, dag=dag)
t2 = PythonOperator(task_id='bank_ingest', python_callable=ingest_bank, dag=dag)
t3 = PythonOperator(task_id='insurer_ingest', python_callable=ingest_insurer, dag=dag)

t1 >> t2 >> t3
```

---

## Frontend

* React + Tailwind dashboard
* Multi-country selection
* Claims status and metrics

### Example App.js

```javascript
import React, { useState, useEffect } from "react";

function Dashboard({ country }) {
	const [claims, setClaims] = useState([]);

	useEffect(() => {
		fetch(`http://localhost:8000/${country}/claims/all`)
			.then(res => res.json())
			.then(data => setClaims(data.claims));
	}, [country]);

	return (
		<div>
			<h1>{country.toUpperCase()} Dashboard</h1>
			<table>
				<thead><tr><th>Owner</th><th>Asset</th><th>Status</th></tr></thead>
				<tbody>
					{claims.map(c => (
						<tr key={c.claim_id}>
							<td>{c.owner_name}</td>
							<td>{c.asset_type}</td>
							<td>{c.status}</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>
	);
}

export default Dashboard;
```

---

## Terraform (AWS Multi-AZ PostgreSQL & Elasticsearch)

```hcl
provider "aws" {
	region = "us-east-1"
}

locals {
	countries = ["kenya", "uganda", "tanzania", "nigeria"]
}

resource "aws_db_instance" "safiri_db" {
	for_each = toset(local.countries)

	allocated_storage    = 50
	engine               = "postgres"
	engine_version       = "15.3"
	instance_class       = "db.m6g.large"
	name                 = "safiri_${each.key}"
	username             = "safiri"
	password             = var.db_password
	multi_az             = true
	storage_type         = "gp3"
	backup_retention_period = 7
}

resource "aws_elasticsearch_domain" "safiri_es" {
	domain_name           = "safiri-assets"
	elasticsearch_version = "8.13"

	cluster_config {
		instance_type  = "r6g.large.elasticsearch"
		instance_count = 4
		zone_awareness_enabled = true
	}

	ebs_options {
		ebs_enabled = true
		volume_size = 50
		volume_type = "gp3"
	}

	node_to_node_encryption { enabled = true }
	encrypt_at_rest { enabled = true }
}
```

---

## Docker Compose for Local Testing

```yaml
version: "3.9"
services:
	backend:
		build: ./backend
		ports:
			- "8000:8000"
		depends_on:
			- postgres_kenya
			- es
		environment:
			- DATABASE_URL=postgresql://safiri:pass@postgres_kenya:5432/safiri_kenya

	postgres_kenya:
		image: postgres:15
		environment:
			POSTGRES_USER: safiri
			POSTGRES_PASSWORD: pass
			POSTGRES_DB: safiri_kenya
		ports: ["5432:5432"]

	es:
		image: docker.elastic.co/elasticsearch/elasticsearch:8.13.0
		environment:
			- discovery.type=single-node
		ports:
			- "9200:9200"
```

> Repeat PostgreSQL for Uganda, Tanzania, Nigeria with different ports.

---

## Matching Engine Microservice

* Python microservice using **RapidFuzz** for fuzzy matching
* Multi-layer confidence scoring
* Duplicate detection
* Country-specific rules

### Example matching snippet

```python
from rapidfuzz import fuzz

def match_names(name1, name2):
		score = fuzz.token_sort_ratio(name1, name2)
		return score >= 85  # Confidence threshold
```

---

## Next Steps

1. Clone the repository
2. Set environment variables (`DB_PASSWORD`, `API_KEYS`)
3. Deploy Terraform to AWS
4. Start Docker Compose for local testing
5. Run Airflow DAGs for ETL ingestion
6. Launch FastAPI backend & React frontend
7. Begin multi-country claims matching and outreach

This full repo structure is **ready to clone and start development** for pan-African unclaimed asset recovery.
