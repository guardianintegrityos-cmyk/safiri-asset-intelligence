
# Safiri Asset Intelligence - Full Ready-to-Clone Repository

This repository contains the full infrastructure for Safiri Asset Intelligence with multi-country deployment (Kenya, Uganda, Tanzania, Nigeria).

---

## Repository Structure

```
safiri-asset-intelligence/
├─ backend/
│  ├─ app/
│  │  ├─ routes/
│  │  │  ├─ kenya/claims.py
│  │  │  ├─ uganda/claims.py
│  │  │  ├─ tanzania/claims.py
│  │  │  └─ nigeria/claims.py
│  │  │  └─ b2b.py
│  │  ├─ models/ (SQLAlchemy models per country)
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
