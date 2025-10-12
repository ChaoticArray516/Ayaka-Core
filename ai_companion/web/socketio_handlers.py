"""
Socket.IO Event Handlers
Handle WebSocket connections and real-time communication
"""

import json
import time
import logging
from flask_socketio import emit, disconnect
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SocketIOHandlers:
    """Socket.IO Event Handlers"""

    def __init__(self, web_app):
        self.web_app = web_app
        self.connected_clients: Dict[str, Dict] = {}

    def on_connect(self):
        """Client connection event"""
        client_id = str(id(emit))
        connect_time = time.time()

        # Record client information
        self.connected_clients[client_id] = {
            "connect_time": connect_time,
            "last_activity": connect_time,
            "message_count": 0
        }

        logger.info(f"Client connected: {client_id}")

        # Send connection confirmation and current status
        persona_info = self.web_app.persona_manager.get_current_persona()

        emit('connected', {
            'persona': {
                'state': self.web_app.persona_manager.current_state.value,
                'name': persona_info['name'],
                'description': persona_info['description']
            },
            'yandere_level': self.web_app.persona_manager.yandere_level,
            'yandere_description': self.web_app.persona_manager.get_yandere_level_description(),
            'timestamp': time.time()
        })

    def on_disconnect(self):
        """Client disconnection event"""
        client_id = str(id(emit))
        if client_id in self.connected_clients:
            del self.connected_clients[client_id]
        logger.info(f"Client disconnected: {client_id}")

    def on_user_message(self, data):
        """Handle user messages"""
        try:
            client_id = str(id(emit))
            user_input = data.get('text', '').strip()

            if not user_input:
                emit('error', {'message': 'Message cannot be empty'})
                return

            logger.info(f"Received user message: {user_input[:50]}...")

            # Update client activity time
            if client_id in self.connected_clients:
                self.connected_clients[client_id]['last_activity'] = time.time()
                self.connected_clients[client_id]['message_count'] += 1

            # Check cache
            system_prompt = self.web_app.persona_manager.get_system_prompt()
            cached_response = self.web_app.cache_service.get_cached_llm_response(
                user_input, system_prompt
            )

            if cached_response:
                logger.info("Using cached response")
                response_data = {
                    'text': cached_response,
                    'cached': True,
                    'persona': self.web_app.persona_manager.get_current_persona()['name'],
                    'yandere_level': self.web_app.persona_manager.yandere_level,
                    'timestamp': time.time()
                }

                # Add to conversation history and chat records
                self.web_app.conversation_manager.add_message("user", user_input)
                self.web_app.conversation_manager.add_message("assistant", cached_response)

                # Save to chat history
                self.web_app.chat_history_manager.add_message(
                    "user", user_input,
                    persona=self.web_app.persona_manager.current_state.value,
                    yandere_level=self.web_app.persona_manager.yandere_level
                )
                self.web_app.chat_history_manager.add_message(
                    "assistant", cached_response,
                    persona=self.web_app.persona_manager.current_state.value,
                    yandere_level=self.web_app.persona_manager.yandere_level
                )

                emit('ai_response', response_data)
                return

            # Generate AI response
            emit('typing_start', {'message': 'AI is thinking...'})

            # Get conversation context
            conversation_context = self.web_app.conversation_manager.get_context_for_llm()

            # Get memory context
            memory_context = self.web_app.memory_manager.get_context_for_llm(user_input, 300)

            # Merge contexts
            full_context = f"{memory_context}\n\n{conversation_context}" if memory_context else conversation_context

            # Call LLM
            llm_response = self.web_app.llm_client.generate_response(
                user_input, system_prompt, full_context
            )

            emit('typing_end', {})

            if llm_response.get('success'):
                ai_response = llm_response['response']

                # Cache response
                self.web_app.cache_service.cache_llm_response(
                    user_input, system_prompt, ai_response
                )

                # Add to conversation history and chat records
                self.web_app.conversation_manager.add_message("user", user_input)
                self.web_app.conversation_manager.add_message("assistant", ai_response)

                # Send response
                response_data = {
                    'text': ai_response,
                    'cached': False,
                    'persona': self.web_app.persona_manager.get_current_persona()['name'],
                    'yandere_level': self.web_app.persona_manager.yandere_level,
                    'timestamp': time.time(),
                    'tokens_used': llm_response.get('tokens_used', 0),
                    'response_time': llm_response.get('response_time', 0)
                }

                # Save to chat history
                self.web_app.chat_history_manager.add_message(
                    "user", user_input,
                    persona=self.web_app.persona_manager.current_state.value,
                    yandere_level=self.web_app.persona_manager.yandere_level,
                    timestamp=response_data['timestamp']
                )
                self.web_app.chat_history_manager.add_message(
                    "assistant", ai_response,
                    persona=self.web_app.persona_manager.current_state.value,
                    yandere_level=self.web_app.persona_manager.yandere_level,
                    timestamp=response_data['timestamp']
                )

                emit('ai_response', response_data)
                logger.info(f"AI response sent successfully, time taken: {llm_response.get('response_time', 0):.2f}s")

            else:
                error_msg = llm_response.get('error', 'Failed to generate response')
                logger.error(f"AI response generation failed: {error_msg}")

                emit('error', {
                    'message': f'Sorry, I cannot reply right now: {error_msg}',
                    'error_code': llm_response.get('error_code')
                })

        except Exception as e:
            logger.error(f"Failed to process user message: {e}")
            emit('error', {'message': 'An error occurred while processing the message'})

    def on_get_history(self, data=None):
        """Get conversation history"""
        try:
            if data is None:
                data = {}
            limit = data.get('limit', 50)
            messages = self.web_app.chat_history_manager.get_session_messages(limit)

            emit('history', {
                'messages': messages,
                'total': len(messages)
            })

        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            emit('error', {'message': 'Failed to get history'})

    def on_clear_history(self, data=None):
        """Clear conversation history"""
        try:
            # Clear conversation history and chat records
            self.web_app.chat_history_manager.clear_current_session()
            self.web_app.conversation_manager.clear_history()
            self.web_app.cache_service.clear(memory_only=True)

            # Send confirmation message
            emit('history_cleared', {
                'message': 'Conversation history cleared',
                'timestamp': time.time()
            })

            # Broadcast to all clients
            from flask_socketio import broadcast
            emit('history_cleared', {
                'message': 'Conversation history cleared',
                'timestamp': time.time()
            }, broadcast=True)

            logger.info("Conversation history cleared")

        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            emit('error', {'message': 'Failed to clear history'})

    def on_set_persona(self, data):
        """Set persona state"""
        try:
            persona_name = data.get('persona')
            if not persona_name:
                emit('error', {'message': 'Persona name cannot be empty'})
                return

            # Find persona state
            from ..ai.persona_manager import PersonaState
            persona_state = None
            for state in PersonaState:
                if state.value == persona_name:
                    persona_state = state
                    break

            if not persona_state:
                emit('error', {'message': 'Invalid persona state'})
                return

            # Set persona
            success = self.web_app.persona_manager.set_persona(persona_state)
            if success:
                new_persona = self.web_app.persona_manager.get_current_persona()

                # Send confirmation message
                emit('persona_changed', {
                    'persona': persona_state.value,
                    'name': new_persona['name'],
                    'description': new_persona['description'],
                    'yandere_level': self.web_app.persona_manager.yandere_level,
                    'timestamp': time.time()
                })

                # Broadcast to all clients
                from flask_socketio import broadcast
                emit('persona_changed', {
                    'persona': persona_state.value,
                    'name': new_persona['name'],
                    'description': new_persona['description'],
                    'yandere_level': self.web_app.persona_manager.yandere_level,
                    'timestamp': time.time()
                }, broadcast=True)

                logger.info(f"Persona switched to: {persona_state.value}")

            else:
                emit('error', {'message': 'Failed to set persona'})

        except Exception as e:
            logger.error(f"Failed to set persona: {e}")
            emit('error', {'message': 'Failed to set persona'})

    def on_set_yandere_level(self, data):
        """Set yandere level"""
        try:
            level = data.get('level')
            if not isinstance(level, int) or level < 0 or level > 4:
                emit('error', {'message': 'Yandere level must be between 0-4'})
                return

            # Set yandere level
            success = self.web_app.persona_manager.set_yandere_level(level)
            if success:
                # Send confirmation message
                emit('yandere_level_changed', {
                    'level': level,
                    'description': self.web_app.persona_manager.get_yandere_level_description(),
                    'timestamp': time.time()
                })

                # Broadcast to all clients
                from flask_socketio import broadcast
                emit('yandere_level_changed', {
                    'level': level,
                    'description': self.web_app.persona_manager.get_yandere_level_description(),
                    'timestamp': time.time()
                }, broadcast=True)

                logger.info(f"Yandere level set to: {level}")

            else:
                emit('error', {'message': 'Failed to set yandere level'})

        except Exception as e:
            logger.error(f"Failed to set yandere level: {e}")
            emit('error', {'message': 'Failed to set yandere level'})

    def on_ping(self, data=None):
        """Heartbeat detection"""
        client_id = str(id(emit))
        if client_id in self.connected_clients:
            self.connected_clients[client_id]['last_activity'] = time.time()

        emit('pong', {
            'timestamp': time.time(),
            'connected_clients': len(self.connected_clients)
        })

    def on_get_status(self, data=None):
        """Get detailed status"""
        try:
            persona_info = self.web_app.persona_manager.get_current_persona()
            conv_stats = self.web_app.conversation_manager.get_conversation_statistics()
            cache_stats = self.web_app.cache_service.get_stats()

            status_data = {
                'persona': {
                    'state': self.web_app.persona_manager.current_state.value,
                    'name': persona_info['name'],
                    'description': persona_info['description'],
                    'yandere_level': self.web_app.persona_manager.yandere_level,
                    'yandere_description': self.web_app.persona_manager.get_yandere_level_description()
                },
                'conversation': conv_stats,
                'cache': cache_stats,
                'llm': self.web_app.llm_client.get_model_info(),
                'connected_clients': len(self.connected_clients),
                'timestamp': time.time()
            }

            emit('status_update', status_data)

        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            emit('error', {'message': 'Failed to get status'})

def register_handlers(socketio, web_app):
    """Register Socket.IO event handlers"""
    handlers = SocketIOHandlers(web_app)

    # Connection related events
    socketio.on('connect')(handlers.on_connect)
    socketio.on('disconnect')(handlers.on_disconnect)

    # Message related events
    socketio.on('user_message')(handlers.on_user_message)
    socketio.on('get_history')(handlers.on_get_history)
    socketio.on('clear_history')(handlers.on_clear_history)

    # Persona related events
    socketio.on('set_persona')(handlers.on_set_persona)
    socketio.on('set_yandere_level')(handlers.on_set_yandere_level)

    # System related events
    socketio.on('ping')(handlers.on_ping)
    socketio.on('get_status')(handlers.on_get_status)

    logger.info("Socket.IO event handlers registered successfully")