from .fuzzy_match import fuzzy_name_match
import pandas as pd

def run_matching(country="Kenya"):
    df_assets = pd.read_csv(f"data/assets_{country}.csv")
    df_claims = pd.read_csv(f"data/claims_{country}.csv")
    results = []
    for _, asset in df_assets.iterrows():
        for _, claim in df_claims.iterrows():
            score = fuzzy_name_match(asset['owner_name'], claim['owner_name'])
            if score >= 85:
                results.append({"asset_name": asset['owner_name'], "claim_name": claim['owner_name'], "confidence": score})
    return {"matches_found": len(results), "details": results[:20]}
