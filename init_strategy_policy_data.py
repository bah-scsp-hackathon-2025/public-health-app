import requests
import json


API_URL = "http://localhost:8000"

alerts = requests.get(f"{API_URL}/alerts/").json()
alert_ids = [alert["id"] for alert in alerts]

with open("documents/data/strategies.ndjson", "r") as f:
    strategies = [json.loads(line) for line in f.read().splitlines()]

for strategy in strategies:
    if strategy["alert_id"] == "alert_001":
        strategy["alert_id"] = alert_ids[0]
    elif strategy["alert_id"] == "alert_002":
        strategy["alert_id"] = alert_ids[1]
    elif strategy["alert_id"] == "alert_003":
        strategy["alert_id"] = alert_ids[2]
    else:
        strategy["alert_id"] = alert_ids[3]
    result = requests.post(f"{API_URL}/strategies/", json=strategy)
    print(result.json())

with open("documents/data/policy_drafts.jsonl", "r") as f:
    policies = [json.loads(line) for line in f.read().splitlines()]

for policy in policies:
    if policy["alert_id"] == "alert_001":
        policy["alert_id"] = alert_ids[0]
    elif policy["alert_id"] == "alert_002":
        policy["alert_id"] = alert_ids[1]
    elif policy["alert_id"] == "alert_003":
        policy["alert_id"] = alert_ids[2]
    else:
        policy["alert_id"] = alert_ids[3]
    result = requests.post(f"{API_URL}/policies/", json=policy)
    print(result.json())
