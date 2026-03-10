import pandas as pd
from matching_engine.fuzzy_match import fuzzy_name_match

# --- ETL Step ---
def load_sample_data():
    # Simulated data ingestion
    data = pd.DataFrame([
        {"owner_name": "John Kamau", "asset_type": "Bank Account", "id_number": "12345"},
        {"owner_name": "Mary Wanjiku", "asset_type": "Insurance", "id_number": "67890"},
    ])
    return data

# --- Matching Step ---
def run_matching(input_name: str, df: pd.DataFrame):
    results = []
    for idx, row in df.iterrows():
        score = fuzzy_name_match(input_name, row["owner_name"])
        results.append({
            "owner_name": row["owner_name"],
            "asset_type": row["asset_type"],
            "confidence": score
        })
    return sorted(results, key=lambda x: x["confidence"], reverse=True)

# --- Demo Execution ---
if __name__ == "__main__":
    df_assets = load_sample_data()
    user_query = input("Enter your name or ID: ")
    matches = run_matching(user_query, df_assets)
    print("\nTop matches:")
    for m in matches:
        print(f"{m['owner_name']} - {m['asset_type']} (Confidence: {m['confidence']}%)")
