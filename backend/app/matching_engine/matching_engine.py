# matching_engine.py
from fastapi import FastAPI
from matching import match_records

app = FastAPI()

@app.post("/match")
def match_endpoint(data: dict):
    matches = match_records(data)
    return {"matches": matches}
