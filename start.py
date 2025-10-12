#!/usr/bin/env python3
"""
AI Virtual Companion System Startup Script
Using Python 3.11.12 and Anaconda environment
"""

import os
import sys
import logging
from pathlib import Path

def setup_environment():
    """Setup environment"""
    # Add project root directory to Python path
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def check_dependencies():
    """Check dependencies"""
    try:
        import flask
        import flask_socketio
        import requests
        print("Dependencies check passed")
        return True
    except ImportError as e:
        print(f"Missing dependencies: {e}")
        return False

def show_banner():
    """Display startup banner"""
    banner = """
    ========================================================
                    AI Virtual Companion System
                      Intelligent Dialogue - Emotional Interaction
    ========================================================
    Based on Python 3.11.12 + Flask + Socket.IO
    Supports OpenAI, Claude, GLM and other large language models
    Real-time web chat interface
    Multiple persona state switching
    Dynamic emotional level adjustment
    ========================================================
    """
    print(banner)

def start_server():
    """Start server"""
    try:
        from ai_companion.web.app import create_app
        from ai_companion.utils.logger import setup_logging
        from ai_companion.config.settings import ConfigManager

        # Setup logging
        config_manager = ConfigManager()
        config_manager.load_config()
        log_config = config_manager.get_logging_config()
        setup_logging(log_config)

        # Create Flask application
        app, socketio, web_app = create_app()

        # Get configuration
        host = config_manager.get("app.host", "0.0.0.0")
        port = config_manager.get("app.port", 5000)
        debug = config_manager.get("app.debug", False)

        print(f"\nStarting AI Companion server...")
        print(f"Access URLs:")
        print(f"   Home: http://localhost:{port}")
        print(f"   Chat Interface: http://localhost:{port}/chat")
        print(f"Debug Mode: {'Enabled' if debug else 'Disabled'}")
        print("=" * 60)

        # Start server
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True
        )

    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Startup failed: {e}")
        return False

    return True

def main():
    """Main function"""
    show_banner()
    setup_environment()

    if not check_dependencies():
        print("\nPlease install dependencies:")
        print("  Method 1: conda env update -f environment.yml")
        print("  Method 2: pip install -r requirements.txt")
        print("  Method 3: pip install flask flask-socketio requests")
        return 1

    print("\nStarting AI Companion system...")
    return 0 if start_server() else 1

if __name__ == "__main__":
    sys.exit(main())