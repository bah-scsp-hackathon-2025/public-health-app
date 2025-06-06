#!/usr/bin/env python3
"""
Test script for the policy draft generation REST endpoint

This script tests the new /dashboard/generate-policy-draft endpoint
by sending a request with sample strategy and alert data.
"""

import requests
import json
from datetime import datetime

# Test data
TEST_ALERT = {
    "name": "COVID-19 Symptom and Loss of Smell Trend Alert",
    "description": "Rising trend detected in COVID-like symptoms and anosmia/ageusia (loss of smell/taste) search activity. While hospital admissions remain stable, increased symptom searches and clinical manifestations suggest potential community transmission increase.",
    "risk_score": 5,
    "risk_reason": "Moderate risk assigned due to rising symptom trends without corresponding hospital surge.",
    "location": "United States",
    "latitude": "39.8283",
    "longitude": "-98.5795",
}

TEST_STRATEGY = {
    "short_description": "Emergency Response for COVID-19 Symptom and Loss of Smell Trend Alert",
    "full_description": "Immediate emergency response to address rising trend detected in COVID-like symptoms and anosmia/ageusia (loss of smell/taste) search activity. Deploy emergency protocols including enhanced surveillance, rapid testing expansion, healthcare system preparation, and coordinated public health messaging.",
    "alert_id": "alert_001",
}


def test_policy_draft_endpoint():
    """Test the policy draft generation endpoint"""

    print("🧪 Testing Policy Draft Generation Endpoint")
    print("=" * 60)

    # API endpoint (FastAPI is running on port 8000)
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/dashboard/generate-policy-draft"

    # Request payload
    payload = {"strategy": TEST_STRATEGY, "alert": TEST_ALERT, "author": "Test System"}

    print(f"📡 Sending request to: {endpoint}")
    print("📋 Request payload:")
    print(f"   Strategy: {TEST_STRATEGY['short_description']}")
    print(f"   Alert: {TEST_ALERT['name']}")
    print("   Author: Test System")

    try:
        # Send the request
        start_time = datetime.now()
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=600,  # 10 minute timeout for extended thinking
        )
        end_time = datetime.now()

        generation_time = (end_time - start_time).total_seconds()

        print(f"\n⏱️  Response time: {generation_time:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")

        if response.status_code == 200:
            # Success response
            policy_data = response.json()

            print("✅ Policy draft generated successfully!")
            print("📝 Policy Details:")
            print(f"   Title: {policy_data.get('title', 'N/A')}")
            print(f"   Author: {policy_data.get('author', 'N/A')}")
            print(f"   Approved: {policy_data.get('approved', 'N/A')}")
            print(f"   Alert ID: {policy_data.get('alert_id', 'N/A')}")
            print(f"   Strategy ID: {policy_data.get('strategy_id', 'N/A')}")
            print(
                f"   Content length: {len(policy_data.get('content', ''))} characters"
            )

            # Show content preview
            content = policy_data.get("content", "")
            if content:
                content_lines = content.split("\n")[:5]
                print("   Content preview:")
                for line in content_lines:
                    if line.strip():
                        print(f"     {line.strip()[:80]}...")

            return True

        elif response.status_code == 422:
            # Validation error
            error_data = response.json()
            print("❌ Validation error:")
            print(f"   {json.dumps(error_data, indent=2)}")
            return False

        else:
            # Other error
            try:
                error_data = response.json()
                print(f"❌ Error {response.status_code}:")
                print(f"   {json.dumps(error_data, indent=2)}")
            except:
                print("❌ Error {response.status_code}: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the FastAPI server running?")
        print("   Start the server with: uvicorn app.main:app --reload --port 8000")
        return False

    except requests.exceptions.Timeout:
        print("❌ Request timed out (>10 minutes)")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def test_invalid_request():
    """Test the endpoint with invalid request data"""

    print("\n🧪 Testing Invalid Request Handling")
    print("=" * 60)

    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/dashboard/generate-policy-draft"

    # Invalid payload (missing required fields)
    invalid_payload = {
        "strategy": {"short_description": "Test"},  # Missing required fields
        "alert": {"name": "Test"},  # Missing required fields
    }

    print(f"📡 Sending invalid request to: {endpoint}")

    try:
        response = requests.post(
            endpoint,
            json=invalid_payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        print(f"📊 Status code: {response.status_code}")

        if response.status_code == 422:
            print("✅ Validation error handled correctly")
            error_data = response.json()
            print(f"   Error details: {error_data}")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error testing invalid request: {str(e)}")
        return False


def main():
    """Main test runner"""

    print("🚀 Policy Draft Generation Endpoint Test Suite")
    print("=" * 80)

    # Check if server is accessible
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI server is accessible")
        else:
            print("⚠️  FastAPI server responded but may not be fully ready")
    except:
        print("❌ FastAPI server is not accessible")
        print(
            "   Please start the server with: uvicorn app.main:app --reload --port 8000"
        )
        return

    test_results = []

    # Run tests
    result1 = test_policy_draft_endpoint()
    test_results.append(("Policy Draft Generation", result1))

    result2 = test_invalid_request()
    test_results.append(("Invalid Request Handling", result2))

    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall Result: {passed}/{len(test_results)} tests passed")

    if passed == len(test_results):
        print("🎉 All tests passed! Policy draft endpoint is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the logs above for details.")


if __name__ == "__main__":
    main()
