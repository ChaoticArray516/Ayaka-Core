"""
Ayaka AI女友系统
神里绫华 - 深情AI伴侣
"""

__version__ = "1.0.0"
__author__ = "Ayaka Team"
__description__ = "基于GLM4.5V的AI女友系统"

from .ai.persona_manager import PersonaManager
from .services.llm_client import LLMClient
from .config.settings import ConfigManager

__all__ = [
    'PersonaManager',
    'LLMClient',
    'ConfigManager'
]