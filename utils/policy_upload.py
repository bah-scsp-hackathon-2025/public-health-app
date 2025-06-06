#!/usr/bin/env python3
"""
Policy Document Upload Script

This script uploads PDF policy documents from the documents/policies folder
to Anthropic's cloud storage using the beta Files API for use with Claude.

Usage:
    python utils/policy_upload.py

Requirements:
    - Anthropic API key in environment or .env file
    - PDF files in documents/policies/ folder
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


class PolicyUploader:
    """Handles uploading policy documents to Anthropic Files API"""

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

        # Set policies directory path
        self.policies_dir = Path(__file__).parent.parent / "documents" / "policies"

        print(f"📁 Policies directory: {self.policies_dir}")
        print(f"🔑 API key configured: {'*' * 20}{self.api_key[-8:] if len(self.api_key) > 8 else '***'}")

    def find_policy_pdfs(self) -> List[Path]:
        """Find all PDF files in the policies directory"""

        if not self.policies_dir.exists():
            raise FileNotFoundError(f"Policies directory not found: {self.policies_dir}")

        if not self.policies_dir.is_dir():
            raise NotADirectoryError(f"Policies path is not a directory: {self.policies_dir}")

        # Find all PDF files (case insensitive)
        pdf_files = []
        for pattern in ["*.pdf", "*.PDF"]:
            pdf_files.extend(self.policies_dir.glob(pattern))

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
                "uploaded_at": (file_response.created_at if hasattr(file_response, "created_at") else "unknown"),
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

    async def upload_all_policies(self) -> List[Dict]:
        """Upload all policy documents"""

        print("🚀 Starting policy document upload...")
        print("=" * 60)

        # Find PDF files
        try:
            pdf_files = self.find_policy_pdfs()
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

    def list_uploaded_files(self) -> None:
        """List all files uploaded to Anthropic account"""

        try:
            print("\n📋 Listing all uploaded files...")
            files_response = self.client.beta.files.list()

            if hasattr(files_response, "data") and files_response.data:
                print(f"\n📁 Found {len(files_response.data)} uploaded file(s):")
                print(f"{'Name':<40} {'File ID':<30} {'Size':<10}")
                print("-" * 80)

                for file_obj in files_response.data:
                    name = getattr(file_obj, "filename", getattr(file_obj, "id", "unknown"))
                    file_id = file_obj.id
                    size = getattr(file_obj, "size", "unknown")
                    print(f"{name:<40} {file_id:<30} {size:<10}")
            else:
                print("📭 No files found in your Anthropic account")

        except Exception as e:
            print(f"❌ Error listing files: {e}")

    def print_summary(self, uploaded_files: List[Dict]) -> None:
        """Print a summary of uploaded files"""

        if not uploaded_files:
            print("\n📭 No files were successfully uploaded")
            return

        print(f"\n{'='*70}")
        print(f"📊 UPLOAD SUMMARY")
        print(f"{'='*70}")
        print(f"✅ Successfully uploaded: {len(uploaded_files)} file(s)")

        total_size_mb = sum(f["size_mb"] for f in uploaded_files)
        print(f"📦 Total size: {total_size_mb:.1f} MB")

        print(f"\n📋 File Details:")
        print(f"{'Name':<35} {'File ID':<30} {'Size (MB)':<12}")
        print("-" * 77)

        for file_info in uploaded_files:
            print(f"{file_info['name']:<35} {file_info['id']:<30} {file_info['size_mb']:<12.1f}")

        print("\n🔗 File IDs for Claude usage:")
        for file_info in uploaded_files:
            print(f"   {file_info['id']} # {file_info['name']}")

        print("\n💡 Usage in Claude:")
        print("   You can now reference these files in Claude conversations using their File IDs")
        print("   Example: 'Analyze the policy document with ID: file-xxx'")


async def main():
    """Main entry point"""

    print("🏥 Public Health Policy Document Uploader")
    print("=" * 60)
    print("Uploading PDF documents from documents/policies/ to Anthropic Files API")
    print()

    try:
        # Initialize uploader
        uploader = PolicyUploader()

        # Confirm before uploading
        pdf_files = uploader.find_policy_pdfs()
        if not pdf_files:
            return

        total_size_mb = sum(f.stat().st_size / (1024 * 1024) for f in pdf_files)
        print("\n📊 Upload Summary:")
        print(f"   Files to upload: {len(pdf_files)}")
        print(f"   Total size: {total_size_mb:.1f} MB")

        # Ask for confirmation
        confirm = input(f"\nProceed with upload? (y/N): ").strip().lower()
        if confirm != "y":
            print("❌ Upload cancelled")
            return

        # Upload files
        uploaded_files = await uploader.upload_all_policies()

        # Print summary
        uploader.print_summary(uploaded_files)

        # Optionally list all files
        if uploaded_files:
            list_all = input("\nList all files in your Anthropic account? (y/N): ").strip().lower()
            if list_all == "y":
                uploader.list_uploaded_files()

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Upload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
