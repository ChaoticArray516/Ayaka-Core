@echo off
chcp 65001 >nul
echo ========================================================
echo              AI Virtual Companion System - Installation Script
echo ========================================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not found, please install Python 3.11.12 first
    echo    Download URL: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python installed

REM Check Conda
conda --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Conda not found, please install Anaconda or Miniconda first
    echo    Anaconda download URL: https://www.anaconda.com/download/
    echo    Miniconda download URL: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

echo ✅ Conda installed

REM Create and activate environment
echo.
echo 📦 Creating Conda environment...
conda env create -f environment.yml
if errorlevel 1 (
    echo ❌ Environment creation failed, trying to update existing environment...
    conda env update -f environment.yml
)

echo.
echo 🔧 Activating environment...
call conda activate ai_companion

REM Install dependencies
echo.
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo.
echo 📁 Creating directory structure...
if not exist "logs" mkdir logs
if not exist "cache" mkdir cache
if not exist "data" mkdir data

REM Copy configuration file
echo.
echo ⚙️ Configuring environment...
if not exist ".env" (
    copy ".env.example" ".env"
    echo ✅ .env configuration file created, please modify as needed
)

REM Verify installation
echo.
echo 🔍 Verifying installation...
python -c "import flask, flask_socketio, requests; print('✅ All dependencies installed successfully')"

echo.
echo ========================================================
echo                   Installation Complete!
echo ========================================================
echo.
echo 🚀 Startup commands:
echo    1. conda activate ai_companion
echo    2. python start.py
echo.
echo Or use:
echo    python run.py --mode dev
echo.
echo 🌐 Access URL: http://localhost:5000
echo 💬 Chat Interface: http://localhost:5000/chat
echo.
pause