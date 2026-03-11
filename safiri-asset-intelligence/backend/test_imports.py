#!/usr/bin/env python3
"""
Simple test script to verify that all required packages can be imported
"""

try:
    import fastapi
    import sqlalchemy
    import numpy as np
    import sklearn
    import neo4j
    import jwt
    import rapidfuzz
    import elasticsearch
    print("✅ All imports resolved successfully!")
    print(f"FastAPI: {fastapi.__version__}")
    print(f"SQLAlchemy: {sqlalchemy.__version__}")
    print(f"NumPy: {np.__version__}")
    print(f"Neo4j: {neo4j.__version__}")
    print(f"JWT: {jwt.__version__}")
    print(f"RapidFuzz: {rapidfuzz.__version__}")
    print(f"Elasticsearch: {elasticsearch.__version__}")
except Exception as e:
    print("❌ Import error:", e)