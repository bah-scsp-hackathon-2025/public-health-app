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

# get the id of the last alert created to use for  the strategies
alert_id = result.json()["id"]

# create strategies for the last alert
strategies = [
    {
        "short_description": "Activate Emergency Operations Center",
        "full_description": "Mobilize the emergency operations center to coordinate the public health response.\n\nPriority: High\nResponsible Agency: Public Health Department\nExpected Outcome: Streamlined communication and resource allocation during the event.\nEstimated Duration: 7 days.",
        "alert_id": alert_id,
    },
    {
        "short_description": "Issue Public Health Advisory",
        "full_description": "Inform the public about the health risks and recommended preventive measures.\n\nPriority: High\nResponsible Agency: CDC\nExpectedOutcome: Increased public awareness and compliance with health guidelines.\nEstimated Duration: 3 days.\n",
        "alert_id": alert_id,
    },
    {
        "short_description": "Implement Travel Restrictions",
        "full_description": "Restrict travel to and from affected areas to limit disease spread.\n\nPriority: Medium\nResponsible Agency: Department of Transportation\nExpected Outcome: Reduced transmission across regions.\nEstimated Duration: 14 days.\n",
        "alert_id": alert_id,
    },
]
for strategy in strategies:
    result = requests.post(f"{API_URL}/policies/strategy/", json=strategy)
    print(result.json())


approved_policy = {
    "title": "Travel Restrictions",
    "author": "CDC",
    "content": "Restrict travel to and from affected areas to limit disease spread.",
    "approved": True,
    "alert_id": alert_id,
}
result = requests.post(f"{API_URL}/policies/", json=approved_policy)
print(result.json())
