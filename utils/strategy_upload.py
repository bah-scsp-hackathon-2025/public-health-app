#!/usr/bin/env python3
"""
Strategy Document Upload Script

This script uploads PDF strategy documents from the documents/strategy folder
to Anthropic's cloud storage using the beta Files API for use with Claude.

Usage:
    python utils/strategy_upload.py

Requirements:
    - Anthropic API key in environment or .env file
    - PDF files in documents/strategy/ folder
    - anthropic package installed (see backend/app/requirements.txt)
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Optional

# Add backend app to path for configuration access
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend", "app"))

try:
    import anthropic
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Please install requirements from backend/app/requirements.txt:")
    print("  cd backend/app && pip install -r requirements.txt")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Try to import backend configuration
try:
    from config import settings

    print("✅ Loaded backend configuration")
except ImportError:
    print("⚠️  Could not load backend config, using environment variables only")
    settings = None


class StrategyUploader:
    """Handles uploading strategy documents to Anthropic Files API"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the uploader with API credentials"""

        # Get API key from multiple sources
        self.api_key = (
            api_key
            or (settings.anthropic_api_key if settings and settings.anthropic_api_key else None)
            or os.getenv("ANTHROPIC_API_KEY")
        )

        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. Please set ANTHROPIC_API_KEY environment variable "
                "or add it to your .env file."
            )

        # Initialize Anthropic client
        self.client = anthropic.Anthropic(api_key=self.api_key)

        # Set strategy directory path
        self.strategy_dir = Path(__file__).parent.parent / "documents" / "strategy"

        print(f"📁 Strategy directory: {self.strategy_dir}")
        print(f"🔑 API key configured: {'*' * 20}{self.api_key[-8:] if len(self.api_key) > 8 else '***'}")

    def find_strategy_pdfs(self) -> List[Path]:
        """Find all PDF files in the strategy directory"""

        if not self.strategy_dir.exists():
            raise FileNotFoundError(f"Strategy directory not found: {self.strategy_dir}")

        if not self.strategy_dir.is_dir():
            raise NotADirectoryError(f"Strategy path is not a directory: {self.strategy_dir}")

        # Find all PDF files (case insensitive)
        pdf_files = []
        for pattern in ["*.pdf", "*.PDF"]:
            pdf_files.extend(self.strategy_dir.glob(pattern))

        # Sort by name for consistent ordering
        pdf_files.sort(key=lambda p: p.name.lower())

        print(f"📋 Found {len(pdf_files)} PDF file(s):")
        for pdf in pdf_files:
            size_mb = pdf.stat().st_size / (1024 * 1024)
            print(f"   • {pdf.name} ({size_mb:.1f} MB)")

        return pdf_files

    async def upload_file(self, pdf_path: Path) -> Optional[Dict]:
        """Upload a single PDF file to Anthropic"""

        try:
            print(f"📤 Uploading {pdf_path.name}...")

            # Check file size (Anthropic has limits)
            file_size = pdf_path.stat().st_size
            size_mb = file_size / (1024 * 1024)

            if size_mb > 100:  # Anthropic file size limit
                print(f"⚠️  Warning: {pdf_path.name} is {size_mb:.1f} MB (may exceed limits)")

            # Upload the file using the beta Files API
            with open(pdf_path, "rb") as f:
                file_response = self.client.beta.files.upload(file=(pdf_path.name, f, "application/pdf"))

            # Build file info
            file_info = {
                "name": pdf_path.name,
                "id": file_response.id,
                "size_bytes": file_size,
                "size_mb": size_mb,
                "path": str(pdf_path),
                "purpose": "user_upload",
                "document_type": "strategy",
                "uploaded_at": file_response.created_at if hasattr(file_response, "created_at") else "unknown",
            }

            print(f"✅ Successfully uploaded: {pdf_path.name}")
            print(f"   File ID: {file_response.id}")
            print(f"   Size: {size_mb:.1f} MB")

            return file_info

        except anthropic.APIError as e:
            print(f"❌ API Error uploading {pdf_path.name}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error uploading {pdf_path.name}: {e}")
            return None

    async def upload_all_strategies(self) -> List[Dict]:
        """Upload all strategy documents"""

        print("🚀 Starting strategy document upload...")
        print("=" * 60)

        # Find PDF files
        try:
            pdf_files = self.find_strategy_pdfs()
        except (FileNotFoundError, NotADirectoryError) as e:
            print(f"❌ {e}")
            return []

        if not pdf_files:
            print("⚠️  No PDF files found to upload")
            return []

        # Upload each file
        uploaded_files = []

        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"\n📄 [{i}/{len(pdf_files)}] Processing {pdf_path.name}")

            file_info = await self.upload_file(pdf_path)
            if file_info:
                uploaded_files.append(file_info)

        return uploaded_files

    def list_uploaded_files(self, strategy_only: bool = True) -> None:
        """List all files uploaded to Anthropic account"""

        try:
            print("\n📋 Listing uploaded files...")
            files_response = self.client.beta.files.list()

            if hasattr(files_response, "data") and files_response.data:
                files_to_show = files_response.data

                # Filter for strategy documents if requested
                if strategy_only:
                    strategy_files = []
                    for file_obj in files_response.data:
                        filename = getattr(file_obj, "filename", getattr(file_obj, "id", "unknown"))
                        # Look for common strategy document patterns
                        if any(
                            pattern in filename.lower()
                            for pattern in [
                                "strategy",
                                "paho",
                                "who",
                                "epidemic",
                                "outbreak",
                                "preparedness",
                                "response",
                            ]
                        ):
                            strategy_files.append(file_obj)
                    files_to_show = strategy_files
                    print(
                        f"\n📁 Found {len(strategy_files)} strategy-related file(s) (filtered from {len(files_response.data)} total):"
                    )
                else:
                    print(f"\n📁 Found {len(files_response.data)} total uploaded file(s):")

                if files_to_show:
                    print(f"{'Name':<50} {'File ID':<30} {'Size':<10}")
                    print("-" * 90)

                    for file_obj in files_to_show:
                        name = getattr(file_obj, "filename", getattr(file_obj, "id", "unknown"))
                        file_id = file_obj.id
                        size = getattr(file_obj, "size", "unknown")
                        print(f"{name:<50} {file_id:<30} {size:<10}")
                else:
                    print("📭 No strategy files found matching the filter criteria")
            else:
                print("📭 No files found in your Anthropic account")

        except Exception as e:
            print(f"❌ Error listing files: {e}")

    def print_summary(self, uploaded_files: List[Dict]) -> None:
        """Print a summary of uploaded strategy files"""

        if not uploaded_files:
            print("\n📭 No files were successfully uploaded")
            return

        print(f"\n{'='*70}")
        print(f"📊 STRATEGY UPLOAD SUMMARY")
        print(f"{'='*70}")
        print(f"✅ Successfully uploaded: {len(uploaded_files)} strategy document(s)")

        total_size_mb = sum(f["size_mb"] for f in uploaded_files)
        print(f"📦 Total size: {total_size_mb:.1f} MB")

        print(f"\n📋 Strategy Document Details:")
        print(f"{'Name':<45} {'File ID':<30} {'Size (MB)':<12}")
        print("-" * 87)

        for file_info in uploaded_files:
            print(f"{file_info['name']:<45} {file_info['id']:<30} {file_info['size_mb']:<12.1f}")

        print(f"\n🔗 File IDs for Claude usage in strategy generation:")
        for file_info in uploaded_files:
            print(f"   {file_info['id']} # {file_info['name']}")

        print(f"\n💡 Usage in Strategy Generation Agent:")
        print("   These strategy documents will be automatically detected and used by the")
        print("   StrategyGenerationAgent when generating evidence-based strategies.")
        print("   The agent looks for files with 'strategy' in their filename.")

        print(f"\n🎯 Strategy Document Types Uploaded:")
        strategy_types = set()
        for file_info in uploaded_files:
            name = file_info["name"].lower()
            if "epidemic" in name or "outbreak" in name:
                strategy_types.add("Epidemic/Outbreak Response")
            if "pandemic" in name:
                strategy_types.add("Pandemic Preparedness")
            if "communication" in name:
                strategy_types.add("Crisis Communication")
            if "preparedness" in name:
                strategy_types.add("Emergency Preparedness")
            if "paho" in name or "who" in name:
                strategy_types.add("WHO/PAHO Guidelines")

        for strategy_type in sorted(strategy_types):
            print(f"   ✓ {strategy_type}")


async def main():
    """Main entry point"""

    print("📋 Public Health Strategy Document Uploader")
    print("=" * 60)
    print("Uploading PDF strategy documents from documents/strategy/ to Anthropic Files API")
    print("These documents will be used by the StrategyGenerationAgent for evidence-based strategy creation.")
    print()

    try:
        # Initialize uploader
        uploader = StrategyUploader()

        # Confirm before uploading
        pdf_files = uploader.find_strategy_pdfs()
        if not pdf_files:
            return

        total_size_mb = sum(f.stat().st_size / (1024 * 1024) for f in pdf_files)
        print(f"\n📊 Upload Preview:")
        print(f"   Strategy documents to upload: {len(pdf_files)}")
        print(f"   Total size: {total_size_mb:.1f} MB")
        print(f"   Destination: Anthropic Files API (for Claude strategy generation)")

        # Show document types
        print(f"\n📋 Document Types Detected:")
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

        # Ask for confirmation
        confirm = input(f"\nProceed with strategy document upload? (y/N): ").strip().lower()
        if confirm != "y":
            print("❌ Upload cancelled")
            return

        # Upload files
        uploaded_files = await uploader.upload_all_strategies()

        # Print summary
        uploader.print_summary(uploaded_files)

        # Optionally list all files
        if uploaded_files:
            list_strategy = input(f"\nList strategy-related files in your Anthropic account? (y/N): ").strip().lower()
            if list_strategy == "y":
                uploader.list_uploaded_files(strategy_only=True)

            list_all = input(f"\nList ALL files in your Anthropic account? (y/N): ").strip().lower()
            if list_all == "y":
                uploader.list_uploaded_files(strategy_only=False)

        print(f"\n🎉 Strategy document upload complete!")
        print("These documents are now available for the StrategyGenerationAgent to reference")
        print("when creating evidence-based public health strategies.")

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n❌ Upload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
