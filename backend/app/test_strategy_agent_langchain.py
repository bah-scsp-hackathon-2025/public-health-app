#!/usr/bin/env python3

"""
Test script for the updated StrategyGenerationAgent with LangChain, Claude Sonnet 4, and Langfuse
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the path for proper imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Now import using the app module structure
from app.agents.strategy_generation_agent import StrategyGenerationAgent
from app.models.alert import AlertCreate

async def test_strategy_agent():
    """Test the StrategyGenerationAgent with LangChain and Langfuse"""
    print("🧪 Testing StrategyGenerationAgent with LangChain + Claude Sonnet 4 + Langfuse")
    print("=" * 80)
    
    try:
        # Test 1: Initialize agent
        print("1. Initializing StrategyGenerationAgent...")
        agent = StrategyGenerationAgent()
        print("✅ Agent initialized successfully")
        
        # Test 2: Create test alert
        print("\n2. Creating test alert...")
        test_alert = AlertCreate(
            name="COVID-19 Surge in Downtown Medical District",
            description="Significant increase in COVID-19 hospitalizations in downtown medical district. ICU capacity at 85%. Community transmission rate increasing rapidly with new variant detection.",
            risk_score=8,
            risk_reason="High hospitalization rate, ICU near capacity, new variant detected, dense population area",
            location="Downtown Medical District, Metro City",
            latitude="40.7589",
            longitude="-73.9851"
        )
        print("✅ Test alert created")
        print(f"   Alert: {test_alert.name}")
        print(f"   Risk Score: {test_alert.risk_score}/10")
        print(f"   Location: {test_alert.location}")
        
        # Test 3: Generate strategies
        print("\n3. Generating strategies with Claude Sonnet 4...")
        print("   Note: This will use extended thinking mode and Langfuse tracing")
        print("   Expected: 4 distinct strategies with different severity levels")
        
        strategies = await agent.generate_strategies(test_alert)
        
        print(f"\n✅ Successfully generated {len(strategies)} strategies!")
        
        # Test 4: Display results
        print("\n4. Strategy Generation Results:")
        print("=" * 50)
        
        strategy_types = [
            "🚨 Immediate Response (High Severity)",
            "⚠️  Moderate Response (Medium Severity)", 
            "🛡️  Preventive Response (Low-Medium Severity)",
            "📋 Long-term Response (Strategic)"
        ]
        
        for i, (strategy, strategy_type) in enumerate(zip(strategies, strategy_types), 1):
            print(f"\n{strategy_type}")
            print(f"Title: {strategy.short_description}")
            print(f"Description: {strategy.full_description[:200]}...")
            print("-" * 50)
        
        # Test 5: Validate strategy content
        print("\n5. Validating strategy content...")
        
        # Check all strategies have required fields
        for i, strategy in enumerate(strategies, 1):
            if not strategy.short_description or not strategy.full_description:
                print(f"❌ Strategy {i} missing required fields")
                return False
            
            if len(strategy.short_description) > 100:
                print(f"⚠️  Strategy {i} title too long: {len(strategy.short_description)} chars")
            
            # Check for evidence-based content
            description_lower = strategy.full_description.lower()
            evidence_keywords = ['protocol', 'guidelines', 'compliance', 'policy', 'evidence', 'who', 'paho']
            has_evidence = any(keyword in description_lower for keyword in evidence_keywords)
            
            if has_evidence:
                print(f"✅ Strategy {i} contains evidence-based references")
            else:
                print(f"⚠️  Strategy {i} may lack evidence-based references")
        
        print(f"\n✅ All validations passed!")
        
        # Test 6: Langfuse integration check
        print("\n6. Langfuse Integration:")
        print("   ✅ Langfuse tracing should be active")
        print("   ✅ Check your Langfuse dashboard for traces:")
        print("      - strategy_generation_workflow")
        print("      - claude_strategy_generation")
        print("      - fetch_documents, build_prompt, parse_strategies spans")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_agent_without_documents():
    """Test agent behavior when no documents are available"""
    print("\n🧪 Testing agent without policy documents...")
    
    try:
        agent = StrategyGenerationAgent()
        
        # Mock the _get_policy_file_ids to return empty list
        original_method = agent._get_policy_file_ids
        async def mock_get_policy_files():
            return []
        agent._get_policy_file_ids = mock_get_policy_files
        
        test_alert = AlertCreate(
            name="Test Alert Without Docs",
            description="Testing fallback behavior",
            risk_score=5,
            risk_reason="Test scenario",
            location="Test Location",
            latitude="0.0",
            longitude="0.0"
        )
        
        strategies = await agent.generate_strategies(test_alert)
        
        # Restore original method
        agent._get_policy_file_ids = original_method
        
        print(f"✅ Generated {len(strategies)} strategies without documents")
        print("   This should use LangChain ChatAnthropic instead of direct API")
        
        return True
        
    except Exception as e:
        print(f"❌ Test without documents failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 StrategyGenerationAgent LangChain Integration Test")
    print("Testing Claude Sonnet 4 + Extended Thinking + LangChain + Langfuse")
    print("=" * 80)
    
    # Check environment variables
    required_env_vars = ["ANTHROPIC_API_KEY"]
    optional_env_vars = ["LANGFUSE_SECRET_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_HOST"]
    
    print("\n🔍 Environment Check:")
    for var in required_env_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is missing (required)")
            return 1
    
    for var in optional_env_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"⚠️  {var} not set (Langfuse tracing may not work)")
    
    # Run tests
    print("\n" + "=" * 80)
    
    success1 = await test_strategy_agent()
    success2 = await test_agent_without_documents()
    
    print("\n" + "=" * 80)
    print("📊 Test Summary:")
    print(f"   Main strategy generation: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"   Without documents test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed!")
        print("\n💡 Next steps:")
        print("   1. Check Langfuse dashboard for traces")
        print("   2. Test the API endpoint: POST /dashboard/generate-strategies")
        print("   3. Verify extended thinking mode is working")
        print("   4. Upload strategy documents for enhanced context")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 