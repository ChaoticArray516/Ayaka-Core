"""
Web Module
Contains Flask application and WebSocket handling
"""

from .app import create_app
from .socketio_handlers import register_handlers

__all__ = ['create_app', 'register_handlers']