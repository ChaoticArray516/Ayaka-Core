#!/bin/bash

# AI Virtual Companion System - Linux/macOS Installation Script

echo "========================================================"
echo "           AI Virtual Companion System - Installation Script"
echo "========================================================"
echo

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python3 not found, please install Python 3.11.12 first${NC}"
    echo "   Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "   CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "   macOS: brew install python@3.11"
    exit 1
fi

echo -e "${GREEN}✅ Python3 installed${NC}"

# Check Conda
if ! command -v conda &> /dev/null; then
    echo -e "${YELLOW}⚠️  Warning: Conda not found, will use Python virtual environment${NC}"
    USE_VENV=true
else
    echo -e "${GREEN}✅ Conda installed${NC}"
    USE_VENV=false
fi

# Create and activate environment
echo
echo "📦 Creating Python environment..."

if [ "$USE_VENV" = true ]; then
    # Use Python virtual environment
    python3 -m venv ai_companion-env
    source ai_companion-env/bin/activate
    echo -e "${GREEN}✅ Virtual environment created and activated${NC}"
else
    # Use Conda
    conda env create -f environment.yml
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Environment creation failed, trying to update existing environment...${NC}"
        conda env update -f environment.yml
    fi

    # Activate environment
    eval "$(conda shell.bash hook)"
    conda activate ai_companion
    echo -e "${GREEN}✅ Conda environment created and activated${NC}"
fi

# Install dependencies
echo
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

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
if [ "$USE_VENV" = true ]; then
    echo "   1. source ai_companion-env/bin/activate"
else
    echo "   1. conda activate ai_companion"
fi
echo "   2. python start.py"
echo
echo "Or use:"
echo "   python run.py --mode dev"
echo
echo "🌐 Access URL: http://localhost:5000"
echo "💬 Chat Interface: http://localhost:5000/chat"
echo
echo -e "${GREEN}Installation complete! You can now start AI Companion!${NC}"