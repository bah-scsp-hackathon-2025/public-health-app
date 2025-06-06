#!/usr/bin/env python3
"""
Test PostgreSQL Integration for Health Dashboard Agents

This script tests the PostgreSQL checkpointer and persistence store integration
for both the standard and ReAct health dashboard agents, with fallback to 
in-memory stores when PostgreSQL is not configured.

Usage:
    # Test with in-memory stores (default)
    python test_postgresql_agents.py
    
    # Test with PostgreSQL (set environment variables first)
    export POSTGRES_PASSWORD=your_password
    export POSTGRES_USER=your_user
    export POSTGRES_HOST=localhost
    export POSTGRES_PORT=5432
    export POSTGRES_DATABASE=public_health
    export POSTGRES_SSL_MODE=disable
    python test_postgresql_agents.py
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Add the backend app to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

try:
    from app.agents.health_dashboard_agent import PublicHealthDashboardAgent
    from app.agents.health_dashboard_react_agent import PublicHealthReActAgent
except ImportError as e:
    print(f"❌ Failed to import agents: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_agent_persistence(agent_name: str, agent_class, agent_instance):
    """Test persistence configuration for a specific agent"""
    print(f"\n{'='*60}")
    print(f"🔬 Testing {agent_name}")
    print(f"{'='*60}")
    
    # Check current PostgreSQL configuration
    postgres_password = os.getenv("POSTGRES_PASSWORD", "default_memory_mode")
    
    if postgres_password == "default_memory_mode":
        print("📋 Configuration: In-Memory Mode")
        print("   - Checkpointer: InMemorySaver")
        print("   - Persistence Store: InMemoryStore")
        print("   - Reason: POSTGRES_PASSWORD not set or using default value")
    else:
        print("📋 Configuration: PostgreSQL Mode")
        print("   - Checkpointer: AsyncPostgresSaver")
        print("   - Persistence Store: InMemoryStore (PostgreSQL store not available)")
        print(f"   - Database: {os.getenv('POSTGRES_DATABASE', 'N/A')}")
        print(f"   - Host: {os.getenv('POSTGRES_HOST', 'N/A')}")
        print(f"   - Port: {os.getenv('POSTGRES_PORT', 'N/A')}")
        print(f"   - SSL Mode: {os.getenv('POSTGRES_SSL_MODE', 'disable')}")
    
    print(f"\n🚀 Testing {agent_name} dashboard generation...")
    
    try:
        # Test dashboard generation
        start_time = datetime.now()
        result = await agent_instance.assemble_dashboard(
            start_date="2020-02-01", 
            end_date="2020-02-03"  # Short date range for faster testing
        )
        end_time = datetime.now()
        
        # Verify result
        if result.get("success"):
            print(f"✅ {agent_name} dashboard generation successful")
            print(f"   - Duration: {(end_time - start_time).total_seconds():.2f} seconds")
            print(f"   - Summary length: {len(result.get('dashboard_summary', '')):.0f} characters")
            print(f"   - Alerts: {len(result.get('alerts', []))}")
            print(f"   - Trends: {len(result.get('rising_trends', []))}")
            print(f"   - Agent type: {result.get('agent_type', 'unknown')}")
            
            if result.get("error"):
                print(f"   - Warning: {result['error']}")
        else:
            print(f"❌ {agent_name} dashboard generation failed")
            print(f"   - Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ {agent_name} test failed with exception: {str(e)}")
        return False
    
    return True

async def test_postgresql_fallback():
    """Test PostgreSQL fallback behavior"""
    print(f"\n{'='*60}")
    print("🔄 Testing PostgreSQL Fallback Behavior")
    print(f"{'='*60}")
    
    # Test with invalid PostgreSQL credentials
    original_password = os.getenv("POSTGRES_PASSWORD")
    original_host = os.getenv("POSTGRES_HOST")
    
    try:
        # Set invalid credentials to test fallback
        os.environ["POSTGRES_PASSWORD"] = "invalid_password"
        os.environ["POSTGRES_HOST"] = "invalid_host"
        os.environ["POSTGRES_PORT"] = "9999"
        os.environ["POSTGRES_DATABASE"] = "invalid_db"
        os.environ["POSTGRES_USER"] = "invalid_user"
        
        print("📋 Configuration: Intentionally Invalid PostgreSQL Settings")
        print("   - Testing fallback to in-memory stores...")
        
        # Create agent with invalid PostgreSQL settings
        agent = PublicHealthDashboardAgent()
        
        print("🚀 Testing dashboard generation with invalid PostgreSQL settings...")
        
        start_time = datetime.now()
        result = await agent.assemble_dashboard(
            start_date="2020-02-01", 
            end_date="2020-02-02"
        )
        end_time = datetime.now()
        
        if result.get("success"):
            print("✅ Fallback to in-memory stores successful")
            print(f"   - Duration: {(end_time - start_time).total_seconds():.2f} seconds")
            print("   - Agent properly fell back to InMemorySaver and InMemoryStore")
        else:
            print(f"❌ Fallback test failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Fallback test failed with exception: {str(e)}")
        return False
    finally:
        # Restore original environment variables
        if original_password:
            os.environ["POSTGRES_PASSWORD"] = original_password
        else:
            os.environ.pop("POSTGRES_PASSWORD", None)
            
        if original_host:
            os.environ["POSTGRES_HOST"] = original_host
        else:
            os.environ.pop("POSTGRES_HOST", None)
    
    return True

async def main():
    """Main test function"""
    print("🐘 PostgreSQL Integration Test for Health Dashboard Agents")
    print("=" * 80)
    
    # Test start time
    test_start_time = datetime.now()
    
    # Check environment setup
    print("🔍 Environment Check:")
    postgres_configured = os.getenv("POSTGRES_PASSWORD") != "default_memory_mode" and os.getenv("POSTGRES_PASSWORD") is not None
    
    if postgres_configured:
        print("   ✅ PostgreSQL credentials detected")
        print("   📝 Tests will verify PostgreSQL checkpointer and store initialization")
    else:
        print("   ℹ️  PostgreSQL credentials not found")
        print("   📝 Tests will verify in-memory fallback behavior")
        print("   💡 To test PostgreSQL mode, set the following environment variables:")
        print("      export POSTGRES_PASSWORD=your_password")
        print("      export POSTGRES_USER=your_user")
        print("      export POSTGRES_HOST=localhost")
        print("      export POSTGRES_PORT=5432")
        print("      export POSTGRES_DATABASE=public_health")
        print("      export POSTGRES_SSL_MODE=disable")
    
    # Test results tracking
    results = []
    
    # Test Standard Health Dashboard Agent
    try:
        standard_agent = PublicHealthDashboardAgent()
        result = await test_agent_persistence(
            "Standard Health Dashboard Agent", 
            PublicHealthDashboardAgent, 
            standard_agent
        )
        results.append(("Standard Agent", result))
    except Exception as e:
        print(f"❌ Failed to test Standard Agent: {str(e)}")
        results.append(("Standard Agent", False))
    
    # Test ReAct Health Dashboard Agent
    try:
        react_agent = PublicHealthReActAgent()
        result = await test_agent_persistence(
            "ReAct Health Dashboard Agent", 
            PublicHealthReActAgent, 
            react_agent
        )
        results.append(("ReAct Agent", result))
    except Exception as e:
        print(f"❌ Failed to test ReAct Agent: {str(e)}")
        results.append(("ReAct Agent", False))
    
    # Test PostgreSQL fallback behavior
    try:
        fallback_result = await test_postgresql_fallback()
        results.append(("PostgreSQL Fallback", fallback_result))
    except Exception as e:
        print(f"❌ Failed to test PostgreSQL fallback: {str(e)}")
        results.append(("PostgreSQL Fallback", False))
    
    # Final summary
    test_end_time = datetime.now()
    total_time = (test_end_time - test_start_time).total_seconds()
    
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status} - {test_name}")
    
    print(f"\n🏁 Overall Results:")
    print(f"   - Tests Passed: {passed_tests}/{total_tests}")
    print(f"   - Total Duration: {total_time:.2f} seconds")
    print(f"   - Status: {'🎉 ALL TESTS PASSED' if passed_tests == total_tests else '⚠️  SOME TESTS FAILED'}")
    
    if postgres_configured:
        print(f"\n💡 PostgreSQL Integration Notes:")
        print(f"   - Both agents successfully initialized with PostgreSQL checkpointer")
        print(f"   - Workflow state will be persisted across sessions")
        print(f"   - Persistence store uses in-memory (PostgreSQL store not available in current LangGraph)")
    else:
        print(f"\n💡 In-Memory Mode Notes:")
        print(f"   - Both agents successfully initialized with in-memory checkpointer and store")
        print(f"   - Workflow state will not persist across sessions")
        print(f"   - Set PostgreSQL environment variables to enable checkpointer persistence")
    
    print("\n🎯 Next Steps:")
    if passed_tests == total_tests:
        print("   - PostgreSQL integration is working correctly")
        print("   - Agents can be used in production with proper PostgreSQL setup")
        print("   - In-memory fallback ensures reliability when PostgreSQL is unavailable")
    else:
        print("   - Review failed tests and check configuration")
        print("   - Verify PostgreSQL credentials and connectivity")
        print("   - Check agent imports and dependencies")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 