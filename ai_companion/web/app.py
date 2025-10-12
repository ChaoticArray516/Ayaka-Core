"""
Flask Application Main File
Create and configure Flask application instance
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import logging
import os
from pathlib import Path

from ..ai.persona_manager import PersonaManager, PersonaState
from ..ai.conversation_manager import ConversationManager
from ..services.llm_client import LLMClient
from ..services.cache_service import CacheService
from ..config.settings import ConfigManager
from ..memory.chat_history_manager import ChatHistoryManager
from ..memory.memory_manager import MemoryManager
from .socketio_handlers import register_handlers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AICompanionWebApp:
    """AI Companion Web Application Class"""

    def __init__(self):
        self.app = None
        self.socketio = None
        self.persona_manager = None
        self.conversation_manager = None
        self.llm_client = None
        self.cache_service = None
        self.config_manager = None
        self.chat_history_manager = None
        self.memory_manager = None

    def initialize(self):
        """Initialize application components"""
        logger.info("Initializing AI Companion Web application...")

        # Load configuration
        self.config_manager = ConfigManager()
        self.config_manager.load_config()

        # Initialize core components
        self.persona_manager = PersonaManager()
        self.conversation_manager = ConversationManager()
        self.llm_client = LLMClient()
        self.cache_service = CacheService()
        self.chat_history_manager = ChatHistoryManager()
        self.memory_manager = MemoryManager(self.chat_history_manager)

        # Configure LLM client
        self._configure_llm_client()

        # Test LLM connection
        self._test_llm_connection()

        logger.info("Application components initialized")

    def _configure_llm_client(self):
        """Configure LLM client"""
        try:
            config_data = self.config_manager.get_llm_config()
            from ..services.llm_client import LLMConfig, LLMProvider

            config = LLMConfig(
                api_key=config_data.get("api_key"),
                base_url=config_data.get("base_url"),
                model=config_data.get("model"),
                max_tokens=config_data.get("max_tokens", 1000),
                temperature=config_data.get("temperature", 0.7),
                provider=LLMProvider(config_data.get("provider", "openai"))
            )

            self.llm_client.config = config
            logger.info("LLM client configuration completed")

        except Exception as e:
            logger.error(f"LLM client configuration failed: {e}")

    def _test_llm_connection(self):
        """Test LLM connection"""
        try:
            test_result = self.llm_client.test_connection()
            if test_result.get("success"):
                logger.info("LLM connection test successful")
            else:
                logger.warning(f"LLM connection test failed: {test_result.get('message')}")
        except Exception as e:
            logger.error(f"LLM connection test exception: {e}")

def create_app():
    """Create Flask application"""
    # Get absolute paths - template and static directories are relative to the app.py file
    current_dir = Path(__file__).parent.parent.parent.parent
    template_dir = current_dir / 'core' / 'web' / 'templates'
    static_dir = current_dir / 'core' / 'web' / 'static'
    
    print(f"Current directory: {current_dir}")
    print(f"Template directory: {template_dir}")
    print(f"Static directory: {static_dir}")
    print(f"Template exists: {template_dir.exists()}")
    print(f"Static exists: {static_dir.exists()}")
    
    # Create Flask instance with explicit template and static folders
    app = Flask(__name__,
                template_folder=str(template_dir),
                static_folder=str(static_dir))
    
    # Add some debugging for requests
    @app.before_request
    def before_request():
        print(f"Before request: {request.method} {request.url} from {request.remote_addr}")
        print(f"Headers: {dict(request.headers)}")
        return None
    
    @app.after_request
    def after_request(response):
        print(f"After request: {request.method} {request.url} -> {response.status_code}")
        return response

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ai_companion_web_secret_key')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Create SocketIO instance
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

    # Create application instance
    web_app = AICompanionWebApp()
    web_app.app = app
    web_app.socketio = socketio
    web_app.initialize()

    # Register routes
    register_routes(app, web_app)

    # Register Socket.IO handlers
    register_handlers(socketio, web_app)

    # Print registered routes for debugging
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")

    return app, socketio, web_app

def register_routes(app: Flask, web_app: AICompanionWebApp):
    """Register routes"""

    @app.route('/')
    def index():
        """Home page"""
        try:
            print(f"Index route called, template folder: {app.template_folder}")
            return render_template('index.html')
        except Exception as e:
            logger.error(f"Home page rendering failed: {e}")
            print(f"Home page rendering failed: {e}")
            return f"Page loading failed: {e}", 500

    @app.route('/chat')
    def chat():
        """Chat page"""
        try:
            print(f"Chat route called, template folder: {app.template_folder}")
            return render_template('chat.html')
        except Exception as e:
            logger.error(f"Chat page rendering failed: {e}")
            print(f"Chat page rendering failed: {e}")
            return f"Page loading failed: {e}", 500

    @app.route('/api/status')
    def get_status():
        """Get status information"""
        try:
            persona_info = web_app.persona_manager.get_current_persona()
            conv_stats = web_app.conversation_manager.get_conversation_statistics()
            cache_stats = web_app.cache_service.get_stats()

            return jsonify({
                "success": True,
                "data": {
                    "persona": {
                        "state": web_app.persona_manager.current_state.value,
                        "name": persona_info["name"],
                        "description": persona_info["description"],
                        "emotional_level": web_app.persona_manager.yandere_level,
                        "emotional_description": web_app.persona_manager.get_yandere_level_description()
                    },
                    "conversation": conv_stats,
                    "cache": cache_stats,
                    "llm": web_app.llm_client.get_model_info()
                }
            })
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/set_persona', methods=['POST'])
    def set_persona():
        """Set persona state"""
        try:
            data = request.get_json()
            persona_name = data.get('persona')

            # Find the corresponding persona state
            persona_state = None
            for state in PersonaState:
                if state.value == persona_name:
                    persona_state = state
                    break

            if not persona_state:
                return jsonify({
                    "success": False,
                    "error": "Invalid persona state"
                }), 400

            # Set persona
            success = web_app.persona_manager.set_persona(persona_state)
            if success:
                new_persona = web_app.persona_manager.get_current_persona()
                return jsonify({
                    "success": True,
                    "data": {
                        "persona": persona_state.value,
                        "name": new_persona["name"],
                        "description": new_persona["description"],
                        "emotional_level": web_app.persona_manager.yandere_level
                    }
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to set persona"
                }), 500

        except Exception as e:
            logger.error(f"Failed to set persona: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/set_emotional_level', methods=['POST'])
    def set_emotional_level():
        """Set emotional level"""
        try:
            data = request.get_json()
            level = data.get('level')

            if not isinstance(level, int) or level < 0 or level > 4:
                return jsonify({
                    "success": False,
                    "error": "Emotional level must be between 0-4"
                }), 400

            # Set emotional level
            success = web_app.persona_manager.set_yandere_level(level)
            if success:
                return jsonify({
                    "success": True,
                    "data": {
                        "emotional_level": level,
                        "description": web_app.persona_manager.get_yandere_level_description()
                    }
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to set emotional level"
                }), 500

        except Exception as e:
            logger.error(f"Failed to set emotional level: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/get_history')
    def get_history():
        """Get conversation history"""
        try:
            limit = request.args.get('limit', type=int, default=50)
            messages = web_app.chat_history_manager.get_session_messages(limit)

            return jsonify({
                "success": True,
                "data": {
                    "messages": messages,
                    "total": len(messages)
                }
            })
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/clear_history', methods=['POST'])
    def clear_history():
        """Clear conversation history"""
        try:
            web_app.chat_history_manager.clear_current_session()
            web_app.conversation_manager.clear_history()
            web_app.cache_service.clear(memory_only=True)

            return jsonify({
                "success": True,
                "message": "Conversation history cleared"
            })

        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/chat_history/search')
    def search_chat_history():
        """Search chat history"""
        try:
            keyword = request.args.get('keyword', '')
            limit = request.args.get('limit', type=int, default=20)

            if not keyword:
                return jsonify({
                    "success": False,
                    "error": "Search keyword cannot be empty"
                }), 400

            results = web_app.chat_history_manager.search_history(keyword, limit)

            return jsonify({
                "success": True,
                "data": {
                    "results": results,
                    "total": len(results),
                    "keyword": keyword
                }
            })

        except Exception as e:
            logger.error(f"Failed to search chat history: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/chat_history/files')
    def get_chat_history_files():
        """Get chat history file list"""
        try:
            limit = request.args.get('limit', type=int, default=10)
            files = web_app.chat_history_manager.get_history_files(limit)

            return jsonify({
                "success": True,
                "data": {
                    "files": files,
                    "total": len(files)
                }
            })

        except Exception as e:
            logger.error(f"Failed to get history file list: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/chat_history/load')
    def load_chat_history_file():
        """Load specified chat history file"""
        try:
            file_path = request.args.get('file', '')
            if not file_path:
                return jsonify({
                    "success": False,
                    "error": "File path cannot be empty"
                }), 400

            # Security check: ensure file is within history directory
            if not str(Path(file_path)).startswith(str(web_app.chat_history_manager.history_dir)):
                return jsonify({
                    "success": False,
                    "error": "Invalid file path"
                }), 400

            messages = web_app.chat_history_manager.load_history_file(file_path)

            return jsonify({
                "success": True,
                "data": {
                    "messages": messages,
                    "total": len(messages),
                    "file": file_path
                }
            })

        except Exception as e:
            logger.error(f"Failed to load history file: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/chat_history/statistics')
    def get_chat_history_statistics():
        """Get chat history statistics"""
        try:
            stats = web_app.chat_history_manager.get_session_statistics()

            return jsonify({
                "success": True,
                "data": stats
            })

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/memory/preferences')
    def get_user_preferences():
        """Get user preferences"""
        try:
            preferences = web_app.memory_manager.get_user_preferences()

            return jsonify({
                "success": True,
                "data": preferences
            })

        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/memory/summary')
    def get_conversation_summary():
        """Get conversation summary"""
        try:
            days = request.args.get('days', type=int, default=7)
            summary = web_app.memory_manager.get_conversation_summary(days)

            return jsonify({
                "success": True,
                "data": summary
            })

        except Exception as e:
            logger.error(f"Failed to get conversation summary: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/memory/relevant')
    def get_relevant_memories():
        """Get relevant memories"""
        try:
            query = request.args.get('query', '')
            limit = request.args.get('limit', type=int, default=10)

            if not query:
                return jsonify({
                    "success": False,
                    "error": "Query content cannot be empty"
                }), 400

            memories = web_app.memory_manager.get_relevant_memories(query, limit)

            return jsonify({
                "success": True,
                "data": {
                    "memories": memories,
                    "total": len(memories),
                    "query": query
                }
            })

        except Exception as e:
            logger.error(f"Failed to get relevant memories: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/memory/context')
    def get_memory_context():
        """Get memory context"""
        try:
            query = request.args.get('query', '')
            max_context = request.args.get('max_context', type=int, default=500)

            if not query:
                return jsonify({
                    "success": False,
                    "error": "Query content cannot be empty"
                }), 400

            context = web_app.memory_manager.get_context_for_llm(query, max_context)

            return jsonify({
                "success": True,
                "data": {
                    "context": context,
                    "query": query,
                    "context_length": len(context)
                }
            })

        except Exception as e:
            logger.error(f"Failed to get memory context: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/memory/clear_cache', methods=['POST'])
    def clear_memory_cache():
        """Clear memory cache"""
        try:
            web_app.memory_manager.clear_cache()

            return jsonify({
                "success": True,
                "message": "Memory cache cleared"
            })

        except Exception as e:
            logger.error(f"Failed to clear memory cache: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/llm/test', methods=['POST'])
    def test_llm():
        """Test LLM connection"""
        try:
            result = web_app.llm_client.test_connection()
            return jsonify(result)
        except Exception as e:
            logger.error(f"LLM test failed: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/config/validate')
    def validate_config():
        """Validate configuration"""
        try:
            llm_validation = web_app.llm_client.validate_config()
            return jsonify({
                "success": True,
                "data": {
                    "llm": llm_validation
                }
            })
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    # Error handling
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": "Page not found"
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}")
        return jsonify({
            "success": False,
            "error": "Unknown server error occurred"
        }), 500