#!/usr/bin/env python3
"""
Test script for the dashboard API endpoints

This script demonstrates how to use the new dashboard endpoints
added to the FastAPI application.
"""

import requests
import time
import os
from typing import Dict, Any


class DashboardAPITester:
    """Test client for dashboard API endpoints"""

    def __init__(self, base_url: str = None):
        if base_url is None:
            host = os.getenv("FASTAPI_HOST", "localhost")
            port = os.getenv("FASTAPI_PORT", "8000")
            base_url = f"http://{host}:{port}"
        self.base_url = base_url.rstrip("/")

    def test_status(self) -> Dict[str, Any]:
        """Test the dashboard status endpoint"""
        print("🔍 Testing dashboard status...")

        try:
            response = requests.get(f"{self.base_url}/dashboard/status", timeout=10)
            response.raise_for_status()

            status = response.json()
            print("✅ Status check successful!")
            print(f"   Agent Available: {status.get('agent_available')}")
            print(f"   MCP Server: {status.get('mcp_server_accessible')}")
            print(f"   Anthropic API: {status.get('anthropic_api_available')}")
            return status

        except requests.exceptions.RequestException as e:
            print(f"❌ Status check failed: {e}")
            return {"error": str(e)}

    def test_generate_dashboard(self, query: str = None) -> Dict[str, Any]:
        """Test the main dashboard generation endpoint"""
        print("🤖 Testing dashboard generation...")

        payload = {
            "query": query or "Generate test dashboard for API testing",
            "agent_type": "standard",
        }

        try:
            start_time = time.time()
            response = requests.post(f"{self.base_url}/dashboard/generate", json=payload, timeout=30)
            end_time = time.time()

            response.raise_for_status()
            result = response.json()

            print(f"✅ Dashboard generation completed in {end_time - start_time:.2f}s")
            print(f"   Success: {result.get('success')}")
            print(f"   Agent Type: {result.get('agent_type')}")

            if result.get("dashboard_summary"):
                print("\n📊 Dashboard Summary (preview):")
                summary = result.get("dashboard_summary", "")
                preview = summary[:100] + "..." if len(summary) > 100 else summary
                print(f"   {preview}")

            # Check enhanced structured data
            alerts_count = len(result.get("alerts", []))
            trends_count = len(result.get("rising_trends", []))
            epi_signals_count = len(result.get("epidemiological_signals", []))
            recommendations_count = len(result.get("recommendations", []))

            print("\n📈 Structured Data:")
            print(f"   Alerts: {alerts_count}")
            print(f"   Rising Trends: {trends_count}")
            print(f"   Epi Signals: {epi_signals_count}")
            print(f"   Risk Assessment: {'Yes' if result.get('risk_assessment') else 'No'}")
            print(f"   Recommendations: {recommendations_count}")

            # Show total items for summary
            total_items = alerts_count + trends_count + epi_signals_count + recommendations_count
            print(f"   Total Data Items: {total_items}")

            if result.get("error"):
                print(f"❌ Error: {result.get('error')}")

            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ Dashboard generation failed: {e}")
            return {"error": str(e)}

    def test_alerts_summary(self) -> Dict[str, Any]:
        """Test the alerts-focused dashboard endpoint"""
        print("🚨 Testing alerts summary...")

        try:
            response = requests.get(f"{self.base_url}/dashboard/alerts-summary", timeout=30)
            response.raise_for_status()

            result = response.json()
            print("✅ Alerts summary completed")
            print(f"   Success: {result.get('success')}")
            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ Alerts summary failed: {e}")
            return {"error": str(e)}

    def test_trends_summary(self) -> Dict[str, Any]:
        """Test the trends-focused dashboard endpoint"""
        print("📈 Testing trends summary...")

        try:
            response = requests.get(f"{self.base_url}/dashboard/trends-summary", timeout=30)
            response.raise_for_status()

            result = response.json()
            print("✅ Trends summary completed")
            print(f"   Success: {result.get('success')}")
            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ Trends summary failed: {e}")
            return {"error": str(e)}

    def test_epidemiological_analysis(self) -> Dict[str, Any]:
        """Test the epidemiological analysis endpoint"""
        print("🔬 Testing epidemiological analysis...")

        payload = {
            "query": "Analyze COVID trends using real epidemiological data",
            "agent_type": "react",
        }

        try:
            response = requests.post(
                f"{self.base_url}/dashboard/epidemiological-analysis",
                json=payload,
                timeout=60,  # Longer timeout for ReAct agent
            )
            response.raise_for_status()

            result = response.json()
            print("✅ Epidemiological analysis completed")
            print(f"   Success: {result.get('success')}")
            print(f"   Agent Type: {result.get('agent_type')}")
            print(f"   Tools Used: {result.get('tools_used', [])}")

            # Show enhanced epidemiological data
            print(f"\n🔬 Epidemiological Data:")
            print(f"   Rising Trends Detected: {len(result.get('rising_trends', []))}")
            print(f"   Signals Analyzed: {len(result.get('epidemiological_signals', []))}")
            if result.get("risk_assessment"):
                risk = result["risk_assessment"]
                print(f"   Overall Risk: {risk.get('overall_risk_level', 'unknown')}")
                print(f"   Confidence: {risk.get('confidence_level', 'unknown')}")

            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ Epidemiological analysis failed: {e}")
            return {"error": str(e)}

    def test_all_endpoints(self):
        """Run all tests"""
        print("🧪 Dashboard API Test Suite")
        print("=" * 50)

        print("\n💡 Note: Make sure the FastAPI server is running:")
        print("   cd backend")
        print("   PYTHONPATH=mcp:. python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print("   (Also ensure FastMCP server is running on port 8001)\n")

        results = {}

        # Test status first
        results["status"] = self.test_status()
        print()

        # Only proceed with other tests if status is good
        if not results["status"].get("error"):
            # Test main generation
            results["generate"] = self.test_generate_dashboard()
            print()

            # Test specific summaries
            results["alerts"] = self.test_alerts_summary()
            print()

            results["trends"] = self.test_trends_summary()
            print()

            # Test epidemiological analysis
            results["epidemiological_analysis"] = self.test_epidemiological_analysis()
            print()

        print("🎯 Test Summary:")
        for test_name, result in results.items():
            status = "✅ PASS" if not result.get("error") else "❌ FAIL"
            print(f"   {test_name}: {status}")

        return results


def main():
    """Main test function"""
    tester = DashboardAPITester()

    print("Welcome to the Dashboard API Tester!")
    print("This script tests the new dashboard endpoints.\n")

    # Check if FastAPI server is running
    try:
        host = os.getenv("FASTAPI_HOST", "localhost")
        port = os.getenv("FASTAPI_PORT", "8001")
        health_url = f"http://{host}:{port}/health"

        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI server is running\n")
        else:
            print("⚠️  FastAPI server responded but with error\n")
    except requests.exceptions.RequestException:
        print("❌ FastAPI server is not running!")
        print("   Please start it with:")
        print("   cd backend && python3 start_fastapi.py")
        print("   (or use the VS Code task 'Start FastAPI App')")
        return

    # Run all tests
    tester.test_all_endpoints()

    print("\n🎉 Testing completed! Check results above.")


if __name__ == "__main__":
    main()
