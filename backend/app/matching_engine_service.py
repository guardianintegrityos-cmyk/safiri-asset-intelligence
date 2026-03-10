from fastapi import FastAPI
from matching_engine.fuzzy_match import run_matching
import uvicorn

app = FastAPI(title="Safiri Matching Engine Microservice")

@app.post("/match-assets")
def match_assets():
    """
    Run the matching engine for all new ETL ingested records.
    Returns summary: total matches, confidence > 85%
    """
    summary = run_matching()
    return summary

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100)
