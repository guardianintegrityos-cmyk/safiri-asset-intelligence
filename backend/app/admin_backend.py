# admin_backend.py
from fastapi import FastAPI
from db import get_claims, get_metrics

app = FastAPI()

@app.get("/claims")
def claims_endpoint(country: str):
    return get_claims(country)

@app.get("/metrics")
def metrics_endpoint():
    return get_metrics()
