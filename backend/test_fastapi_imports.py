#!/usr/bin/env python3
"""
Test script to verify FastAPI imports are working correctly
"""

import sys
import os

# Add necessary paths for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp"))


def test_fastapi_imports():
    """Test FastAPI imports"""
    print("🧪 Testing FastAPI Import Chain")
    print("=" * 50)

    try:
        print("1️⃣ Testing config import...")
        from app.config import settings

        print(f"   ✅ Settings loaded (env vars from: ../.env)")

        print("2️⃣ Testing agent import...")
        from app.agents.health_dashboard_agent import PublicHealthDashboardAgent

        print("   ✅ Agent import successful")

        print("3️⃣ Testing dashboard router import...")
        from app.routers.dashboard import router

        print("   ✅ Dashboard router import successful")

        print("4️⃣ Testing main app import...")
        from app.main import app

        print("   ✅ Main app import successful")

        print("5️⃣ Testing agent instantiation...")
        agent = PublicHealthDashboardAgent()
        print(f"   ✅ Agent created with LLM: {agent.llm is not None}")

        print("\n🎉 ALL IMPORTS AND INSTANTIATION SUCCESSFUL!")
        print("✅ FastAPI server should start without import errors")

    except Exception as e:
        print(f"\n❌ Import error: {e}")
        print("📋 Full traceback:")
        import traceback

        traceback.print_exc()

        print("\n🔧 Troubleshooting:")
        print("- Check Python path configuration")
        print("- Verify all dependencies are installed in venv")
        print("- Check for circular imports")


if __name__ == "__main__":
    test_fastapi_imports()
