#!/usr/bin/env python3

import requests
from datetime import datetime


# Test the new strategy generation endpoint


def test_strategy_generation():
    """Test the strategy generation endpoint"""
    print("🧪 Testing Strategy Generation Endpoint")
    print("=" * 60)

    # Sample alert data to test with
    test_alert = {
        "name": "COVID-19 Surge Alert - Seattle Metro",
        "description": "Significant increase in COVID-19 hospitalizations and ICU capacity nearing 85% in Seattle metropolitan area. New variant detected with higher transmission rate.",
        "risk_score": 7,
        "risk_reason": "High hospitalization rate combined with new variant detection and limited ICU capacity",
        "location": "Washington State",
        "latitude": "47.6062",
        "longitude": "-122.3321",
    }

    # Test the endpoint
    try:
        print("1. Sending request to strategy generation endpoint...")
        print(f"   Alert: {test_alert['name']}")
        print(f"   Risk Score: {test_alert['risk_score']}")
        print(f"   Location: {test_alert['location']}")

        response = requests.post(
            "http://localhost:8000/dashboard/generate-strategies",
            json=test_alert,
            timeout=120,  # Allow 2 minutes for Claude processing
        )

        if response.status_code == 200:
            strategies = response.json()
            print(f"\n✅ SUCCESS! Generated {len(strategies)} strategies:")
            print("=" * 60)

            for i, strategy in enumerate(strategies, 1):
                print(f"\n📋 STRATEGY {i}:")
                print(f"Title: {strategy['short_description']}")
                print(f"Details: {strategy['full_description'][:200]}...")
                print("-" * 40)

            # Verify response structure
            if len(strategies) >= 4:
                print(f"\n✅ Requirement met: Generated {len(strategies)} strategies (minimum 4)")
            else:
                print(f"\n⚠️ Warning: Only generated {len(strategies)} strategies (expected minimum 4)")

            # Check strategy variation
            titles = [s["short_description"] for s in strategies]
            unique_titles = set(titles)
            if len(unique_titles) == len(titles):
                print("✅ All strategies have unique titles")
            else:
                print("⚠️ Warning: Some strategy titles are duplicated")

            return True

        else:
            print(f"❌ FAILED with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Request took longer than 2 minutes")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False


def test_with_different_risk_levels():
    """Test with different risk levels to see strategy variation"""
    print("\n🔄 Testing Strategy Variation with Different Risk Levels")
    print("=" * 60)

    risk_scenarios = [
        {
            "name": "Low Risk Monitoring Alert",
            "description": "Slight uptick in respiratory symptoms reported in community surveillance",
            "risk_score": 2,
            "risk_reason": "Early warning signal from community monitoring",
            "location": "Oregon",
            "latitude": "44.9778",
            "longitude": "-123.0351",
        },
        {
            "name": "High Risk Emergency Alert",
            "description": "Critical hospital capacity exceeded, new highly transmissible variant spreading rapidly",
            "risk_score": 9,
            "risk_reason": "Hospital system overwhelmed with new variant outbreak",
            "location": "California",
            "latitude": "34.0522",
            "longitude": "-118.2437",
        },
    ]

    for scenario in risk_scenarios:
        print(f"\n📊 Testing {scenario['name']} (Risk: {scenario['risk_score']})")
        try:
            response = requests.post(
                "http://localhost:8000/dashboard/generate-strategies",
                json=scenario,
                timeout=120,
            )

            if response.status_code == 200:
                strategies = response.json()
                print(f"✅ Generated {len(strategies)} strategies for risk level {scenario['risk_score']}")

                # Show first strategy as example
                if strategies:
                    print(f"   Example: {strategies[0]['short_description']}")
            else:
                print(f"❌ Failed for risk level {scenario['risk_score']}: {response.status_code}")

        except Exception as e:
            print(f"❌ Error testing risk level {scenario['risk_score']}: {e}")


def main():
    """Run all tests"""
    print(f"🚀 Starting Strategy Generation Tests at {datetime.now()}")
    print("This will test the new /dashboard/generate-strategies endpoint\n")

    # Test 1: Basic functionality
    success = test_strategy_generation()

    if success:
        # Test 2: Risk level variation
        test_with_different_risk_levels()

        print("\n🎉 All tests completed!")
        print("\n📝 Summary:")
        print("- New endpoint: POST /dashboard/generate-strategies")
        print("- Input: AlertCreate model")
        print("- Output: List[StrategyCreate] (4+ strategies)")
        print("- Features: Claude with extended thinking, policy document integration")
        print("- Strategy types: Immediate, Moderate, Preventive, Long-term")

    else:
        print("\n❌ Basic test failed. Check server status and try again.")


if __name__ == "__main__":
    main()
