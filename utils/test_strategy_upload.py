#!/usr/bin/env python3

"""
Test script for the strategy document upload functionality
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the utils directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from strategy_upload import StrategyUploader
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


async def test_strategy_uploader():
    """Test the StrategyUploader class"""
    print("🧪 Testing Strategy Document Uploader")
    print("=" * 50)

    try:
        # Test 1: Initialize uploader
        print("1. Testing uploader initialization...")
        uploader = StrategyUploader()
        print("✅ StrategyUploader initialized successfully")

        # Test 2: Check strategy directory
        print("\n2. Testing strategy directory discovery...")
        strategy_dir = uploader.strategy_dir
        print(f"   Strategy directory: {strategy_dir}")

        if strategy_dir.exists():
            print("✅ Strategy directory exists")
        else:
            print("❌ Strategy directory not found")
            return False

        # Test 3: Find PDF files
        print("\n3. Testing PDF file discovery...")
        pdf_files = uploader.find_strategy_pdfs()
        print(f"✅ Found {len(pdf_files)} PDF file(s)")

        # Test 4: Check file types
        print("\n4. Testing document type detection...")
        for pdf in pdf_files:
            name = pdf.name.lower()
            doc_type = "General Strategy"
            if "epidemic" in name or "outbreak" in name:
                doc_type = "Epidemic/Outbreak Response"
            elif "pandemic" in name:
                doc_type = "Pandemic Preparedness"
            elif "communication" in name:
                doc_type = "Crisis Communication"
            elif "preparedness" in name:
                doc_type = "Emergency Preparedness"
            elif "paho" in name or "who" in name:
                doc_type = "WHO/PAHO Guidelines"
            print(f"   • {pdf.name} → {doc_type}")

        print("\n✅ All tests passed!")

        # Test 5: Simulate upload preview (don't actually upload)
        print("\n5. Upload preview simulation...")
        total_size_mb = sum(f.stat().st_size / (1024 * 1024) for f in pdf_files)
        print(f"   Would upload: {len(pdf_files)} files")
        print(f"   Total size: {total_size_mb:.1f} MB")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("🚀 Strategy Upload Script Test")
    print("This validates the strategy_upload.py script without actually uploading files\n")

    success = await test_strategy_uploader()

    if success:
        print("\n🎉 Strategy uploader tests completed successfully!")
        print("\nTo actually upload files, run:")
        print("   python utils/strategy_upload.py")
    else:
        print("\n❌ Tests failed")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
