import pandas as pd

def ingest_ufaa():
    # Sample UFAA data
    data = pd.DataFrame([
        {"owner_name": "John Kamau", "asset_type": "Bank Account", "id_number": "12345"},
        {"owner_name": "Mary Wanjiku", "asset_type": "Insurance Payout", "id_number": "67890"},
    ])
    # Save to DB / CSV for matching engine
    data.to_csv("backend/app/data/ufaa.csv", index=False)
    print("UFAA data ingested")
