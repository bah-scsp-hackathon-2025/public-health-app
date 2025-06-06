#!/usr/bin/env python3
"""
Test script to verify settings and environment variable loading
"""

import os
import sys

# Add the app path for imports
sys.path.insert(0, ".")

from app.config import settings


def test_settings():
    """Test settings and environment variable loading"""
    print("🧪 Testing Settings and Environment Variable Loading")
    print("=" * 60)

    # First check raw environment variables
    print("\n1️⃣ Raw Environment Variables:")
    env_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "NOT SET"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", "NOT SET"),
        "DELPHI_EPIDATA_KEY": os.getenv("DELPHI_EPIDATA_KEY", "NOT SET"),
        "MCP_SERVER_HOST": os.getenv("MCP_SERVER_HOST", "NOT SET"),
        "MCP_SERVER_PORT": os.getenv("MCP_SERVER_PORT", "NOT SET"),
    }

    for key, value in env_vars.items():
        if value != "NOT SET":
            # Mask sensitive values
            if "KEY" in key and len(value) > 10:
                display_value = f"{value[:8]}...{value[-4:]}"
            else:
                display_value = value
            print(f"   ✅ {key}: {display_value}")
        else:
            print(f"   ❌ {key}: NOT SET")

    # Now check Settings class
    print("\n2️⃣ Settings Class Values:")
    try:
        settings_values = {
            "openai_api_key": settings.openai_api_key,
            "anthropic_api_key": settings.anthropic_api_key,
            "delphi_epidata_key": settings.delphi_epidata_key,
            "mcp_server_host": settings.mcp_server_host,
            "mcp_server_port": settings.mcp_server_port,
        }

        for key, value in settings_values.items():
            if value and value != "":
                # Mask sensitive values
                if "key" in key and len(str(value)) > 10:
                    display_value = f"{str(value)[:8]}...{str(value)[-4:]}"
                else:
                    display_value = str(value)
                print(f"   ✅ {key}: {display_value}")
            else:
                print(f"   ❌ {key}: EMPTY/NOT SET")

        # Check if API keys are usable
        print("\n3️⃣ API Key Validation:")
        if settings.openai_api_key and settings.openai_api_key.startswith("sk-"):
            print("   ✅ OpenAI API key format looks valid")
        else:
            print("   ⚠️  OpenAI API key missing or invalid format")

        if settings.anthropic_api_key and settings.anthropic_api_key.startswith("sk-ant-"):
            print("   ✅ Anthropic API key format looks valid")
        else:
            print("   ⚠️  Anthropic API key missing or invalid format")

    except Exception as e:
        print(f"   ❌ Error loading settings: {str(e)}")
        import traceback

        traceback.print_exc()

    print("\n🎯 SUMMARY:")
    print("=" * 60)
    print("If API keys show as 'NOT SET' or 'EMPTY', you need to:")
    print("1. Set them as environment variables, OR")
    print("2. Create a .env file in the project root")
    print("\nThe agent will work in basic mode without API keys,")
    print("but with reduced analysis capabilities.")


if __name__ == "__main__":
    test_settings()
