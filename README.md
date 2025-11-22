# AI Virtual Companion System

<div align="center">

![AI Companion Banner](https://img.shields.io/badge/AI-Virtual%20Companion%20System-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11.12-green?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.0.0-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Intelligent Dialogue - Emotional Interaction**

An intelligent dialogue system based on large language models, supporting multiple personality states and dynamic emotional interaction

[Quick Start](#quick-start) • [Features](#features) • [Installation Guide](#installation-guide) • [User Documentation](#user-documentation) • [Development Guide](#development-guide)

</div>

## 📖 Project Overview

The AI Virtual Companion System is an intelligent dialogue system based on Python, integrating advanced natural language processing technology and emotional interaction features. The project adopts a modular design, supporting multiple personality state switching and dynamic emotional expression, which can be customized according to user needs.

### 🌟 Core Features

- 🤖 **Multi-model Support**: Integrates OpenAI, Claude, GLM and other large language models
- 🎭 **Personality System**: 5 different personality states, freely switchable
- ❤️ **Emotional Levels**: 0-4 level dynamic emotional level adjustment
- 💬 **Real-time Dialogue**: WebSocket-based real-time chat interface
- 🧠 **Smart Caching**: Dual guarantee of memory cache and persistent cache
- 🎨 **Beautiful Interface**: Responsive web design, supports mobile devices
- ⚙️ **Flexible Configuration**: Fully configurable parameter system

## 🚀 Quick Start

### Prerequisites

- Python 3.11.12+
- UV (Python package manager) - [Installation Guide](https://github.com/astral-sh/uv)
- 4GB+ RAM

### One-click Installation

**Windows Users:**
```bash
# Run installation script
install.bat
```

**Linux/macOS Users:**
```bash
# Run installation script
chmod +x install.sh
./install.sh
```

### Manual Installation

1. **Install UV** (if not already installed)
```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Create Environment**
```bash
# Create UV virtual environment
uv venv --python 3.11.12

# Activate environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. **Install Dependencies**
```bash
# Install project and dependencies
uv pip install -e .
uv pip install -e ".[dev]"  # Install development dependencies
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit the .env file to configure API keys and other parameters
```

5. **Start Service**
```bash
python start.py
```

### Access Application

After successful startup, visit the following addresses:

- **Home**: http://localhost:5000
- **Chat Interface**: http://localhost:5000/chat
- **API Status**: http://localhost:5000/api/status

## 🎯 Features

### Personality System

| Personality State | Description | Characteristics |
|-------------------|-------------|------------------|
| **Gentle Mode** | Private mode, exclusive gentleness | Gentle, intimate, slightly dependent |
| **Elegant Mode** | Public mode, elegant and dignified | Elegant, polite, maintains distance |
| **Possessive Mode** | Dependent mode, strong possessiveness | Paranoid, possessive, strong attachment |
| **Tsundere Mode** | Tsundere mode, cold outside, warm inside | Stubborn, soft-hearted, says opposite of feelings |
| **Sweet Mode** | Sweet mode, completely immersed in love | Sweet, coquettish, full of love |

### Emotional Levels

- **Level 0**: Normal care
- **Level 1**: Slight concern, hoping for more attention
- **Level 2**: Gentle protection, proactive care and protection
- **Level 3**: Deep affection gaze, strong attachment
- **Level 4**: Complete attachment, hoping to completely possess you

## 📁 Project Structure

```
core/
├── ai_companion/             # Core package
│   ├── ai/                   # AI modules
│   │   ├── persona_manager.py    # Personality manager
│   │   └── conversation_manager.py # Conversation manager
│   ├── services/             # Service layer
│   │   ├── llm_client.py         # LLM client
│   │   └── cache_service.py       # Cache service
│   ├── web/                  # Web application
│   │   ├── app.py               # Flask application
│   │   └── socketio_handlers.py  # WebSocket handlers
│   ├── config/               # Configuration management
│   │   └── settings.py          # Configuration manager
│   └── utils/                # Utility modules
│       ├── logger.py            # Logging configuration
│       ├── helpers.py           # Helper functions
│       └── validators.py        # Validators
├── web/                      # Web resources
│   ├── templates/            # HTML templates
│   └── static/               # Static resources
├── config/                   # Configuration files
├── .uv/                      # UV configuration directory
├── pyproject.toml            # UV project configuration
├── requirements.txt          # Python dependencies (legacy)
├── environment.yml           # Conda environment configuration (deprecated)
├── start.py                  # Startup script
└── README.md                 # Project documentation
```

## ⚙️ Configuration

### Environment Variables

Configure the following parameters in the `.env` file:

```bash
# Application configuration
FLASK_APP=ai_companion.web.app:create_app
SECRET_KEY=your-secret-key-here

# Server configuration
HOST=0.0.0.0
PORT=5000
DEBUG=True

# LLM configuration
LLM_PROVIDER=openai
LLM_API_KEY=your-api-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0.7
```

## 🚀 Deployment Guide

### Development Environment

```bash
python run.py --mode dev --debug
```

### Production Environment

```bash
# Using Gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 start:app

# Or using script
python run.py --mode prod --host 0.0.0.0 --port 5000
```

## 🔧 Troubleshooting

### Common Issues

**Q: Port occupied error on startup**
```bash
# Check port usage
netstat -tulpn | grep 5000
# Or use another port
python start.py --port 5001
```

**Q: LLM API call failed**
- Check if API key is correct
- Confirm network connection is normal
- Check log files for detailed error information

## 🤝 Contributing

1. Fork the project
2. Create feature branch
3. Submit changes
4. Push to branch
5. Create Pull Request

## 📝 Changelog

### v2.0.0 - 2025-11-21

#### 🚀 Major Changes
- **Environment Management Upgrade**: Migrated from Conda to UV Python package manager
  - Added `pyproject.toml` configuration file, complying with modern Python project standards
  - Optimized dependency management and virtual environment creation process
  - Improved installation speed and environment consistency

#### 🔄 Technical Improvements
- **Installation Script Refactoring**:
  - `install.sh` and `install.bat` completely updated to support UV environment
  - Simplified installation process, reducing user configuration complexity
  - Enhanced error handling and user-friendly prompts

- **Project Structure Optimization**:
  - Added `.uv/` configuration directory containing UV-related configurations
  - Retained `requirements.txt` and `environment.yml` for backward compatibility
  - Updated documentation to reflect new environment management approach

#### 📚 Documentation Updates
- **README.md Comprehensive Update**:
  - Updated installation guide with detailed UV usage instructions
  - Corrected project structure description, marking new and deprecated files
  - Added detailed steps for UV installation and configuration

#### 🛠️ Developer Experience Improvements
- **Modernized Dependency Management**:
  - Using `uv pip install -e .` for editable installation
  - Support for independent management of development dependencies `uv pip install -e ".[dev]"`
  - Faster dependency resolution and installation speed

#### 📋 Migration Guide
For users upgrading from previous versions:

1. **Install UV**:
   ```bash
   # Windows (PowerShell)
   irm https://astral.sh/uv/install.ps1 | iex
   
   # Linux/macOS
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Create New Environment**:
   ```bash
   uv venv --python 3.11.12
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**:
   ```bash
   uv pip install -e .
   uv pip install -e ".[dev]"
   ```

#### 🔮 Future Plans
- Consider completely removing Conda support in future versions
- Explore UV's lock file functionality to further improve environment consistency
- Integrate more advanced UV features, such as dependency cache optimization

---

## 📄 License

This project is licensed under the MIT License

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) - GPT model support
- [Anthropic](https://www.anthropic.com/) - Claude model support
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Socket.IO](https://socket.io/) - Real-time communication
- [UV](https://github.com/astral-sh/uv) - Modern Python package manager

---

<div align="center">

**If this project helps you, please give it a ⭐️ to show your support!**

Made with ❤️ by AI Companion Team

</div>