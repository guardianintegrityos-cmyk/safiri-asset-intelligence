from fuzzy_match import fuzzy_name_match
import pandas as pd

def run_matching():
    # Example: read ingested CSV (replace with DB integration)
    df_assets = pd.read_csv("data/ufaa.csv")
    df_claims = pd.read_csv("data/sample_claims.csv")  # placeholder
    
    results = []
    for _, asset in df_assets.iterrows():
        for _, claim in df_claims.iterrows():
            score = fuzzy_name_match(asset['owner_name'], claim['owner_name'])
            if score >= 85:
                results.append({
                    "asset_name": asset['owner_name'],
                    "claim_name": claim['owner_name'],
                    "confidence": score
                })
    return {"matches_found": len(results), "details": results[:20]}
