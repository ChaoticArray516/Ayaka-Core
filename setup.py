#!/usr/bin/env python3
"""
AI Virtual Companion System Installation Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements file
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "Flask>=3.0.0",
        "Flask-SocketIO>=5.3.6",
        "requests>=2.31.0",
        "python-socketio>=5.9.0",
        "eventlet>=0.33.3",
        "python-json-logger>=2.0.7",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "Pillow>=10.1.0"
    ]

setup(
    name="ai-companion",
    version="1.0.0",
    author="AI Companion Team",
    author_email="team@ai-companion.dev",
    description="AI Virtual Companion System based on Multiple LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ai-companion/ai-virtual-companion",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Flask",
        "Topic :: Communications :: Chat",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-flask>=1.3.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "pre-commit>=3.5.0",
        ],
        "prod": [
            "gunicorn>=21.2.0",
            "redis>=5.0.1",
        ]
    },
    entry_points={
        "console_scripts": [
            "ai-companion=start:main",
            "ai-companion-web=start:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_companion": [
            "web/templates/*.html",
            "web/static/**/*",
            "config/*.json",
        ],
    },
    zip_safe=False,
)