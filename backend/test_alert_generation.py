#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the paths needed for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app", "agents"))


from health_dashboard_react_agent import PublicHealthReActAgent


async def test_alert_generation():
    """Test the React agent alert generation system"""
    print("🧪 Testing React Agent Alert Generation")
    print("=" * 60)

    try:
        # Create agent
        print("1. Creating React agent...")
        agent = PublicHealthReActAgent()
        print("✅ Agent created successfully")

        # Run dashboard analysis
        print("\n2. Running dashboard analysis...")
        print("⏳ This may take a moment...")

        # Use a date range when COVID trends were more active
        result = await agent.assemble_dashboard(start_date="2021-01-01", end_date="2021-02-01")

        print("✅ Analysis completed")

        # Check results
        print("\n" + "=" * 60)
        print("📊 ANALYSIS RESULTS")
        print("=" * 60)
        print(f"Success: {result.get('success', False)}")
        print(f"Tools used: {result.get('tools_used', [])}")

        # Check alerts
        alerts = result.get("alerts", [])
        print(f"\n🚨 ALERTS GENERATED: {len(alerts)}")

        if alerts:
            for i, alert in enumerate(alerts, 1):
                print(f"\n  Alert #{i}:")
                print(f"    Name: {alert.get('name', 'Unknown')}")
                print(f"    Risk Score: {alert.get('risk_score', 0)}")
                print(f"    Location: {alert.get('location', 'Unknown')}")
                print(f"    Description: {alert.get('description', 'No description')[:100]}...")
        else:
            print("  ⚠️ No alerts were generated")

        # Check trend analyses
        trends = result.get("rising_trends", [])
        print(f"\n📈 TREND ANALYSES: {len(trends)}")

        if trends:
            for i, trend in enumerate(trends, 1):
                print(f"\n  Trend #{i}:")
                print(f"    Signal: {trend.get('signal_name', 'Unknown')}")
                print(f"    Rising Periods: {trend.get('rising_periods', 0)}")
                print(f"    Total Periods: {trend.get('total_periods', 0)}")
                print(f"    Risk Level: {trend.get('risk_level', 'Unknown')}")

        # Check epidemiological signals
        epi_signals = result.get("epidemiological_signals", [])
        print(f"\n🦠 EPIDEMIOLOGICAL SIGNALS: {len(epi_signals)}")

        # Summary
        print("\n📋 SUMMARY:")
        print(f"   Tools executed: {len(result.get('tools_used', []))}")
        print(f"   Trends detected: {len(trends)}")
        print(f"   Alerts generated: {len(alerts)}")
        print(f"   Epi signals processed: {len(epi_signals)}")

        return result

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(test_alert_generation())
