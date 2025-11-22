@echo off
chcp 65001 >nul
echo ========================================================
echo              AI Virtual Companion System - Installation Script
echo                    (UV Python Environment)
echo ========================================================
echo.

REM Check UV installation
uv --version >nul 2>&1
if errorlevel 1 (
    echo Error: UV not found, please install UV first
    echo    Install with PowerShell: irm https://astral.sh/uv/install.ps1 ^| iex
    echo    Or visit: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

echo UV installed

REM Create and activate environment
echo.
echo Creating UV Python environment...
uv venv --python 3.11.12

echo.
echo Activating environment...
call .venv\Scripts\activate

REM Install dependencies
echo.
echo Installing Python dependencies...
uv pip install -e .
uv pip install -e ".[dev]"

REM Create necessary directories
echo.
echo Creating directory structure...
if not exist "logs" mkdir logs
if not exist "cache" mkdir cache
if not exist "data" mkdir data

REM Copy configuration file
echo.
echo Configuring environment...
if not exist ".env" (
    copy ".env.example" ".env"
    echo .env configuration file created, please modify as needed
)

REM Verify installation
echo.
echo Verifying installation...
python -c "import flask, flask_socketio, requests; print('All dependencies installed successfully')"

echo.
echo ========================================================
echo                   Installation Complete!
echo ========================================================
echo.
echo Startup commands:
echo    1. .venv\Scripts\activate
echo    2. python start.py
echo.
echo Or use:
echo    python run.py --mode dev
echo.
echo Access URL: http://localhost:5000
echo Chat Interface: http://localhost:5000/chat
echo.
pause