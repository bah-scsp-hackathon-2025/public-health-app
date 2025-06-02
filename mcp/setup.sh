#!/bin/bash

# Setup script for Public Health MCP Server

echo "Public Health MCP Server Setup"
echo "==============================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "To run the MCP server:"
echo "  source venv/bin/activate"
echo "  python mcp_public_health.py"
echo ""
echo "To run tests:"
echo "  source venv/bin/activate"
echo "  python test_server.py"
echo ""
echo "Virtual environment is now active. You can start using the server!" 