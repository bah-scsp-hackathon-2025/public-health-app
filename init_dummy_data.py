import requests

API_URL = "http://localhost:8000"


# Create some alerts

alert_data = [
    {
        "name": "Alert for New York",
        "description": "High hospitalization rate",
        "risk_score": 45,
        "risk_reason": "High hospitalization rate",
        "location": "New York",
        "latitude": "40.7128",
        "longitude": "-74.006",
    },
    {
        "name": "Alert for Los Angeles",
        "description": "Moderate COVID cases",
        "risk_score": 58,
        "risk_reason": "Moderate COVID cases",
        "location": "Los Angeles",
        "latitude": "34.0522",
        "longitude": "-118.2437",
    },
    {
        "name": "Alert for Chicago",
        "description": "Vaccination drive ongoing",
        "risk_score": 3,
        "risk_reason": "Vaccination drive ongoing",
        "location": "Chicago",
        "latitude": "41.8781",
        "longitude": "-87.6298",
    },
    {
        "name": "Alert for Houston",
        "description": "New variant detected",
        "risk_score": 23,
        "risk_reason": "New variant detected",
        "location": "Houston",
        "latitude": "29.7604",
        "longitude": "-95.3698",
    },
]

for alert in alert_data:
    result = requests.post(f"{API_URL}/alerts/", json=alert)
    print(result.json())
