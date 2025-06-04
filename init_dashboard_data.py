import requests
import json


API_URL = "http://localhost:8000"

with open("documents/data/dashboard.json", "r") as f:
    data = json.load(f)

for alert in data["alerts"]:
    result = requests.post(f"{API_URL}/alerts/", json=alert)
    print(result.json())

result = requests.post(f"{API_URL}/summaries/", json={"description": data["dashboard_summary"]})
print(result.json())

for trend in data["trends"]:
    result = requests.post(f"{API_URL}/trends", json={"data": json.dumps(trend["data"])})
    print(result.json())
