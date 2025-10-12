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
- Anaconda/Miniconda (recommended) or Python virtual environment
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

1. **Create Environment**
```bash
# Using Conda (recommended)
conda env create -f environment.yml
conda activate ai-companion

# Or using Python virtual environment
python -m venv ai-companion-env
source ai-companion-env/bin/activate  # Linux/macOS
ai-companion-env\Scripts\activate     # Windows
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit the .env file to configure API keys and other parameters
```

4. **Start Service**
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
├── environment.yml           # Conda environment configuration
├── requirements.txt          # Python dependencies
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

## 📄 License

This project is licensed under the MIT License

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) - GPT model support
- [Anthropic](https://www.anthropic.com/) - Claude model support
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Socket.IO](https://socket.io/) - Real-time communication

---

<div align="center">

**If this project helps you, please give it a ⭐️ to show your support!**

Made with ❤️ by AI Companion Team

</div>