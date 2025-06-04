import requests
import json


API_URL = "http://localhost:8000"

with open("documents/data/strategies.ndjson", "r") as f:
    strategies = [json.loads(line) for line in f.read().splitlines()]

alerts = requests.get(f"{API_URL}/alerts/").json()
alert_ids = [alert["id"] for alert in alerts]

for strategy in strategies:
    if strategy["alert_id"] == "alert_001":
        strategy["alert_id"] = alert_ids[0]
    if strategy["alert_id"] == "alert_002":
        strategy["alert_id"] = alert_ids[1]
    if strategy["alert_id"] == "alert_003":
        strategy["alert_id"] = alert_ids[2]
    result = requests.post(f"{API_URL}/strategies/", json=strategy)
    print(result.json())

policies = []
for policy in policies:
    result = requests.post(f"{API_URL}/policies/", json=policy)
    print(result.json())
