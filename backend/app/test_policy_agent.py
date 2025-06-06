#!/usr/bin/env python3
"""
Test script for PolicyDraftGenerationAgent

This script tests the policy draft generation functionality by creating
sample strategy and alert data and processing them through the agent.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from app.agents.policy_draft_generation_agent import PolicyDraftGenerationAgent
    from app.models.alert import AlertCreate
    from app.models.strategy import StrategyCreate
    from app.models.policy import PolicyCreate
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Test data
TEST_ALERT = AlertCreate(
    name="COVID-19 Symptom and Loss of Smell Trend Alert",
    description="Rising trend detected in COVID-like symptoms and anosmia/ageusia (loss of smell/taste) search activity. While hospital admissions remain stable, increased symptom searches and clinical manifestations suggest potential community transmission increase. Based on WHO policy guidelines, this warrants enhanced surveillance and public health messaging about vaccination importance, especially for high-risk groups.",
    risk_score=5,
    risk_reason="Moderate risk assigned due to rising symptom trends without corresponding hospital surge. While stable hospital admissions suggest current variants maintain lower severity profiles, increasing symptom searches and anosmia/ageusia indicators point to expanding community circulation.",
    location="United States",
    latitude="39.8283",
    longitude="-98.5795",
)

TEST_STRATEGY = StrategyCreate(
    short_description="Emergency Response for COVID-19 Symptom and Loss of Smell Trend Alert",
    full_description="Immediate emergency response to address rising trend detected in COVID-like symptoms and anosmia/ageusia (loss of smell/taste) search activity. Deploy emergency protocols including enhanced surveillance, rapid testing expansion, healthcare system preparation, and coordinated public health messaging. Establish incident command structure, activate emergency operations centers, and implement surge capacity protocols. Coordinate with CDC, state health departments, and local authorities for unified response.",
    alert_id="alert_001",
)


async def test_policy_agent():
    """Test the PolicyDraftGenerationAgent"""

    print("🧪 Testing PolicyDraftGenerationAgent")
    print("=" * 60)

    # Initialize the agent
    try:
        logger.info("Initializing PolicyDraftGenerationAgent...")
        agent = PolicyDraftGenerationAgent()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return False

    # Test environment variables
    print("\n🔧 Environment Check:")
    anthropic_key = "✅" if os.getenv("ANTHROPIC_API_KEY") else "❌"
    langfuse_public = "✅" if os.getenv("LANGFUSE_PUBLIC_KEY") else "❌"
    langfuse_secret = "✅" if os.getenv("LANGFUSE_SECRET_KEY") else "❌"
    print(f"  ANTHROPIC_API_KEY: {anthropic_key}")
    print(f"  LANGFUSE_PUBLIC_KEY: {langfuse_public}")
    print(f"  LANGFUSE_SECRET_KEY: {langfuse_secret}")

    # Test policy generation
    print("\n📝 Testing Policy Generation:")
    print(f"  Alert: {TEST_ALERT.name}")
    print(f"  Strategy: {TEST_STRATEGY.short_description}")
    print(f"  Risk Score: {TEST_ALERT.risk_score}")
    print(f"  Location: {TEST_ALERT.location}")

    try:
        # Generate policy draft
        logger.info("Generating policy draft...")
        start_time = datetime.now()

        policy_draft = await agent.generate_policy_draft(strategy=TEST_STRATEGY, alert=TEST_ALERT, author="Test System")

        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()

        # Validate the result
        if isinstance(policy_draft, PolicyCreate):
            print("✅ Policy generation successful!")
            print(f"   Generation time: {generation_time:.2f} seconds")
            print(f"   Title: {policy_draft.title}")
            print(f"   Author: {policy_draft.author}")
            print(f"   Approved: {policy_draft.approved}")
            print(f"   Alert ID: {policy_draft.alert_id}")
            print(f"   Strategy ID: {policy_draft.strategy_id}")
            print(f"   Content length: {len(policy_draft.content)} characters")

            # Show first few lines of content
            content_lines = policy_draft.content.split("\n")[:5]
            print("   Content preview:")
            for line in content_lines:
                if line.strip():
                    print(f"     {line.strip()[:80]}...")

            return True
        else:
            print(f"❌ Unexpected result type: {type(policy_draft)}")
            return False

    except Exception as e:
        print(f"❌ Policy generation failed: {e}")
        logger.exception("Policy generation error:")
        return False


async def test_multiple_strategies():
    """Test policy generation with multiple different strategies"""

    print("\n🔄 Testing Multiple Strategy Types:")
    print("=" * 60)

    # Create different strategy types
    strategies = [
        StrategyCreate(
            short_description="Monitoring Strategy for COVID-19 Symptoms",
            full_description="Enhanced monitoring and surveillance for rising COVID-like symptoms. Implement systematic tracking and early warning systems through strengthened surveillance networks, expanded testing protocols, and enhanced data collection.",
            alert_id="alert_001",
        ),
        StrategyCreate(
            short_description="Prevention Protocol for Community Health",
            full_description="Preventive measures to mitigate COVID-like symptoms in the community. Focus on community education, preparedness, vaccination campaigns, and public health messaging to prevent transmission.",
            alert_id="alert_001",
        ),
        StrategyCreate(
            short_description="Long-term Planning for Health System Resilience",
            full_description="Strategic long-term response planning for health system strengthening. Build resilient systems and capacity for future response through infrastructure development, workforce training, and policy framework enhancement.",
            alert_id="alert_001",
        ),
    ]

    agent = PolicyDraftGenerationAgent()
    success_count = 0

    for i, strategy in enumerate(strategies, 1):
        print(f"\n📋 Strategy {i}: {strategy.short_description}")

        try:
            policy_draft = await agent.generate_policy_draft(
                strategy=strategy,
                alert=TEST_ALERT,
                author=f"Test System - Strategy {i}",
            )

            print(f"✅ Policy {i} generated successfully")
            print(f"   Title: {policy_draft.title}")
            print(f"   Content length: {len(policy_draft.content)} characters")
            success_count += 1

        except Exception as e:
            print(f"❌ Policy {i} generation failed: {e}")

    print("\n📊 Multiple Strategy Test Results:")
    print(f"   Successful: {success_count}/{len(strategies)}")
    print(f"   Success rate: {(success_count/len(strategies)*100):.1f}%")

    return success_count == len(strategies)


async def main():
    """Main test runner"""

    print("🚀 PolicyDraftGenerationAgent Test Suite")
    print("=" * 80)

    # Check required environment variables
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("Please set your Anthropic API key before running tests")
        return

    test_results = []

    # Run single policy test
    result1 = await test_policy_agent()
    test_results.append(("Single Policy Generation", result1))

    # Run multiple strategies test
    result2 = await test_multiple_strategies()
    test_results.append(("Multiple Strategy Types", result2))

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
        print("🎉 All tests passed! PolicyDraftGenerationAgent is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the logs above for details.")


if __name__ == "__main__":
    # Run the async test suite
    asyncio.run(main())
