#!/bin/bash

# AI Virtual Companion System - Linux/macOS Installation Script (UV Version)

echo "========================================================"
echo "           AI Virtual Companion System - Installation Script"
echo "                    (UV Python Environment)              "
echo "========================================================"
echo

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check UV installation
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ Error: UV not found, please install UV first${NC}"
    echo "   Install UV with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   Or visit: https://github.com/astral-sh/uv"
    exit 1
fi

echo -e "${GREEN}✅ UV installed${NC}"

# Create and activate environment
echo
echo "📦 Creating UV Python environment..."

# Create UV virtual environment
uv venv --python 3.11.12

# Activate environment
source .venv/bin/activate
echo -e "${GREEN}✅ UV virtual environment created and activated${NC}"

# Install dependencies
echo
echo "📥 Installing Python dependencies..."
uv pip install -e .
uv pip install -e ".[dev]"

# Create necessary directories
echo
echo "📁 Creating directory structure..."
mkdir -p logs cache data

# Copy configuration file
echo
echo "⚙️ Configuring environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ .env configuration file created, please modify as needed${NC}"
fi

# Verify installation
echo
echo "🔍 Verifying installation..."
python3 -c "import flask, flask_socketio, requests; print('✅ All dependencies installed successfully')" 2>/dev/null || {
    echo -e "${RED}❌ Dependencies installation failed${NC}"
    exit 1
}

echo
echo "========================================================"
echo "                     Installation Complete!"
echo "========================================================"
echo
echo "🚀 Startup commands:"
echo "   1. source .venv/bin/activate"
echo "   2. python start.py"
echo
echo "Or use:"
echo "   python run.py --mode dev"
echo
echo "🌐 Access URL: http://localhost:5000"
echo "💬 Chat Interface: http://localhost:5000/chat"
echo
echo -e "${GREEN}Installation complete! You can now start AI Companion!${NC}"