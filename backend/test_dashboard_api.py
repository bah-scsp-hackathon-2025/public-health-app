#!/usr/bin/env python3
"""
Test script for the Dashboard API endpoints

This script demonstrates how to use the new dashboard endpoints
added to the FastAPI application.
"""

import requests
import json
import time
import asyncio
from typing import Dict, Any


class DashboardAPITester:
    """Test client for dashboard API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip('/')
        
    def test_status(self) -> Dict[str, Any]:
        """Test the dashboard status endpoint"""
        print("🔍 Testing dashboard status...")
        
        try:
            response = requests.get(f"{self.base_url}/dashboard/status", timeout=10)
            response.raise_for_status()
            
            status = response.json()
            print(f"✅ Status check successful!")
            print(f"   Agent Available: {status.get('agent_available')}")
            print(f"   MCP Server: {status.get('mcp_server_accessible')}")
            print(f"   LLM Providers: {status.get('llm_providers')}")
            return status
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Status check failed: {e}")
            return {"error": str(e)}
    
    def test_generate_dashboard(self, query: str = None) -> Dict[str, Any]:
        """Test the main dashboard generation endpoint"""
        print("🤖 Testing dashboard generation...")
        
        payload = {
            "query": query or "Generate comprehensive public health dashboard for current situation",
            "llm_provider": "auto"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/dashboard/generate",
                json=payload,
                timeout=60  # Dashboard generation can take time
            )
            end_time = time.time()
            
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Dashboard generation completed in {end_time - start_time:.2f}s")
            print(f"   Success: {result.get('success')}")
            print(f"   Alerts Count: {result.get('alerts_count')}")
            print(f"   Trends Count: {result.get('trends_count')}")
            
            if result.get('dashboard_summary'):
                print("\n📊 Dashboard Summary (preview):")
                summary = result.get('dashboard_summary', '')
                preview = summary[:300] + "..." if len(summary) > 300 else summary
                print(f"   {preview}")
            
            if result.get('error'):
                print(f"❌ Error: {result.get('error')}")
                
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Dashboard generation failed: {e}")
            return {"error": str(e)}
    
    def test_alerts_summary(self) -> Dict[str, Any]:
        """Test the alerts-focused dashboard endpoint"""
        print("🚨 Testing alerts summary...")
        
        try:
            response = requests.get(f"{self.base_url}/dashboard/alerts-summary", timeout=60)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Alerts summary completed")
            print(f"   Success: {result.get('success')}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Alerts summary failed: {e}")
            return {"error": str(e)}
    
    def test_trends_summary(self) -> Dict[str, Any]:
        """Test the trends-focused dashboard endpoint"""
        print("📈 Testing trends summary...")
        
        try:
            response = requests.get(f"{self.base_url}/dashboard/trends-summary", timeout=60)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Trends summary completed")
            print(f"   Success: {result.get('success')}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Trends summary failed: {e}")
            return {"error": str(e)}
    
    def test_async_generation(self) -> Dict[str, Any]:
        """Test the async dashboard generation endpoint"""
        print("⚡ Testing async dashboard generation...")
        
        payload = {
            "query": "Quick emergency response dashboard",
            "llm_provider": "auto"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/dashboard/generate/async",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Async generation started")
            print(f"   Task ID: {result.get('task_id')}")
            print(f"   Message: {result.get('message')}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Async generation failed: {e}")
            return {"error": str(e)}
    
    def test_all_endpoints(self):
        """Run all tests"""
        print("🧪 Dashboard API Test Suite")
        print("=" * 50)
        
        print("\n💡 Note: Make sure the FastAPI server is running:")
        print("   cd backend")
        print("   PYTHONPATH=mcp:. python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
        print("   (Also ensure FastMCP server is running on port 8000)\n")
        
        results = {}
        
        # Test status first
        results['status'] = self.test_status()
        print()
        
        # Only proceed with other tests if status is good
        if not results['status'].get('error'):
            # Test main generation
            results['generate'] = self.test_generate_dashboard()
            print()
            
            # Test specific summaries
            results['alerts'] = self.test_alerts_summary()
            print()
            
            results['trends'] = self.test_trends_summary()
            print()
            
            # Test async
            results['async'] = self.test_async_generation()
            print()
        
        print("🎯 Test Summary:")
        for test_name, result in results.items():
            status = "✅ PASS" if not result.get('error') else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        return results


def main():
    """Main test function"""
    tester = DashboardAPITester()
    
    print("Welcome to the Dashboard API Tester!")
    print("This script tests the new dashboard endpoints.\n")
    
    # Check if FastAPI server is running
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI server is running\n")
        else:
            print("⚠️  FastAPI server responded but with error\n")
    except requests.exceptions.RequestException:
        print("❌ FastAPI server is not running!")
        print("   Please start it with:")
        print("   cd backend && PYTHONPATH=mcp:. python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001")
        return
    
    # Run all tests
    results = tester.test_all_endpoints()
    
    print(f"\n🎉 Testing completed! Check results above.")


if __name__ == "__main__":
    main() 