from fastapi import FastAPI
from typing import List, Dict, Any
import random

app = FastAPI(title="Mock Testing Infrastructure for Safiri Asset Intelligence")

# Mock UFAA API Dataset
mock_assets = [
    {"id": 1, "owner_name": "James Mwangi", "id_number": "12345678", "asset_amount": 50000, "region": "Nairobi", "age": 45},
    {"id": 2, "owner_name": "Mary Wanjiku", "id_number": "87654321", "asset_amount": 75000, "region": "Kisumu", "age": 38},
    {"id": 3, "owner_name": "John Otieno", "id_number": "11223344", "asset_amount": 120000, "region": "Mombasa", "age": 52},
    {"id": 4, "owner_name": "Alice Chebet", "id_number": "44332211", "asset_amount": 65000, "region": "Nakuru", "age": 29},
    {"id": 5, "owner_name": "Peter Kiprop", "id_number": "55667788", "asset_amount": 85000, "region": "Eldoret", "age": 41},
    {"id": 6, "owner_name": "Grace Achieng", "id_number": "99887766", "asset_amount": 95000, "region": "Kisumu", "age": 35},
    {"id": 7, "owner_name": "David Njoroge", "id_number": "33445566", "asset_amount": 110000, "region": "Nairobi", "age": 48},
    {"id": 8, "owner_name": "Sarah Muthoni", "id_number": "77889900", "asset_amount": 60000, "region": "Nakuru", "age": 33},
]

# Synthetic Demographics Dataset (Kenya Open Data style)
mock_demographics = [
    {"county": "Nairobi", "population": 4397073, "median_age": 25, "gdp_per_capita": 2500, "literacy_rate": 0.85},
    {"county": "Kisumu", "population": 1155574, "median_age": 22, "gdp_per_capita": 1200, "literacy_rate": 0.78},
    {"county": "Mombasa", "population": 1208333, "median_age": 24, "gdp_per_capita": 1800, "literacy_rate": 0.82},
    {"county": "Nakuru", "population": 2162202, "median_age": 23, "gdp_per_capita": 1400, "literacy_rate": 0.80},
    {"county": "Eldoret", "population": 475716, "median_age": 21, "gdp_per_capita": 1100, "literacy_rate": 0.75},
]

# Synthetic Global Indicators (World Bank style)
mock_global_indicators = {
    "KE": {  # Kenya
        "gdp_per_capita": 1800,
        "population": 54000000,
        "life_expectancy": 67,
        "unemployment_rate": 0.05,
        "inflation_rate": 0.06
    },
    "TZ": {  # Tanzania
        "gdp_per_capita": 1100,
        "population": 60000000,
        "life_expectancy": 65,
        "unemployment_rate": 0.03,
        "inflation_rate": 0.04
    },
    "UG": {  # Uganda
        "gdp_per_capita": 800,
        "population": 46000000,
        "life_expectancy": 63,
        "unemployment_rate": 0.04,
        "inflation_rate": 0.05
    }
}

@app.get("/api/mock-assets")
def list_assets() -> List[Dict[str, Any]]:
    """Return all mock assets (UFAA-like)"""
    return mock_assets

@app.get("/api/mock-assets/search")
def search_assets(q: str) -> List[Dict[str, Any]]:
    """Fuzzy search mock assets by owner name or ID"""
    q_lower = q.lower()
    return [
        asset for asset in mock_assets
        if q_lower in asset["owner_name"].lower() or q_lower in asset["id_number"]
    ]

@app.get("/api/demographics")
def list_demographics() -> List[Dict[str, Any]]:
    """Return synthetic demographics data (Kenya Open Data style)"""
    return mock_demographics

@app.get("/api/demographics/{county}")
def get_demographics_by_county(county: str) -> Dict[str, Any]:
    """Get demographics for a specific county"""
    for demo in mock_demographics:
        if demo["county"].lower() == county.lower():
            return demo
    return {"error": "County not found"}

@app.get("/api/global/{country_code}")
def get_global_indicators(country_code: str) -> Dict[str, Any]:
    """Get synthetic global indicators for a country (World Bank style)"""
    if country_code.upper() in mock_global_indicators:
        return mock_global_indicators[country_code.upper()]
    return {"error": "Country code not found"}

@app.get("/api/global")
def list_global_indicators() -> Dict[str, Dict[str, Any]]:
    """Return all synthetic global indicators"""
    return mock_global_indicators

@app.get("/api/enriched-assets")
def get_enriched_assets() -> List[Dict[str, Any]]:
    """Return assets enriched with demographic and global data for testing scoring models"""
    enriched = []
    for asset in mock_assets:
        # Find matching demographics
        demo = next((d for d in mock_demographics if d["county"].lower() == asset["region"].lower()), None)
        
        # Get global indicators for Kenya (assuming all assets are Kenyan)
        global_data = mock_global_indicators.get("KE", {})
        
        enriched_asset = {
            **asset,
            "demographics": demo,
            "global_indicators": global_data,
            # Add synthetic scoring probabilities
            "ownership_probability": round(random.uniform(0.7, 0.95), 2),
            "fraud_risk_score": round(random.uniform(0.1, 0.4), 2)
        }
        enriched.append(enriched_asset)
    
    return enriched

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)