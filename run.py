#!/usr/bin/env python3
"""
AI Virtual Companion System Run Script
Supports multiple runtime modes
"""

import os
import sys
import argparse
from pathlib import Path

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Virtual Companion System")
    parser.add_argument(
        "--mode",
        choices=["dev", "prod", "test"],
        default="dev",
        help="Runtime mode (dev: development, prod: production, test: testing)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Server host address"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Server port"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--config",
        help="Configuration file path"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level"
    )

    args = parser.parse_args()

    # Set environment variables
    if args.mode == "prod":
        os.environ["FLASK_ENV"] = "production"
        os.environ["FLASK_DEBUG"] = "0"
    elif args.mode == "dev":
        os.environ["FLASK_ENV"] = "development"
        os.environ["FLASK_DEBUG"] = "1" if args.debug else "0"
    elif args.mode == "test":
        os.environ["FLASK_ENV"] = "testing"
        os.environ["FLASK_DEBUG"] = "0"

    if args.config:
        os.environ["AI_COMPANION_CONFIG_PATH"] = args.config

    os.environ["AI_COMPANION_HOST"] = args.host
    os.environ["AI_COMPANION_PORT"] = str(args.port)
    os.environ["AI_COMPANION_LOG_LEVEL"] = args.log_level

    # Start different servers based on mode
    if args.mode == "prod":
        print("🚀 Starting production server...")
        os.system(f"gunicorn --worker-class eventlet -w 1 --bind {args.host}:{args.port} start:app")
    elif args.mode == "test":
        print("🧪 Running tests...")
        os.system("python -m pytest tests/ -v")
    else:
        print("🔧 Starting development server...")
        from start import main as start_main
        sys.exit(start_main())

if __name__ == "__main__":
    main()