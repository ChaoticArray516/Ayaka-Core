"""
对话管理器
管理对话历史、上下文和消息处理
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ConversationManager:
    """对话管理器"""

    def __init__(self, max_history: int = 50):
        self.conversation_id: str = str(uuid.uuid4())
        self.messages: List[Dict] = []
        self.max_history: int = max_history
        self.session_start: datetime = datetime.now()
        self.last_activity: datetime = datetime.now()

        logger.info(f"ConversationManager初始化完成，会话ID: {self.conversation_id}")

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> str:
        """添加消息到对话历史"""
        message_id = str(uuid.uuid4())
        message = {
            "id": message_id,
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.messages.append(message)
        self.last_activity = datetime.now()

        # 限制历史记录长度
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

        logger.debug(f"添加消息: {role} ({message_id})")
        return message_id

    def get_messages(self, limit: Optional[int] = None) -> List[Dict]:
        """获取对话历史"""
        if limit:
            return self.messages[-limit:]
        return self.messages.copy()

    def get_last_message(self, role: Optional[str] = None) -> Optional[Dict]:
        """获取最后一条消息"""
        if role:
            for message in reversed(self.messages):
                if message["role"] == role:
                    return message
            return None

        return self.messages[-1] if self.messages else None

    def get_context_for_llm(self, max_tokens: int = 4000) -> List[Dict]:
        """为LLM准备上下文消息"""
        context_messages = []
        current_tokens = 0

        # 简单的token估算 (1 token ≈ 4 字符)
        for message in reversed(self.messages[-10:]):  # 最多使用最近10条消息
            estimated_tokens = len(message["content"]) // 4
            if current_tokens + estimated_tokens > max_tokens:
                break

            context_messages.insert(0, {
                "role": message["role"],
                "content": message["content"]
            })
            current_tokens += estimated_tokens

        return context_messages

    def clear_history(self) -> bool:
        """清空对话历史"""
        self.messages.clear()
        self.conversation_id = str(uuid.uuid4())
        self.session_start = datetime.now()
        self.last_activity = datetime.now()

        logger.info("对话历史已清空")
        return True

    def export_conversation(self) -> Dict:
        """导出对话数据"""
        return {
            "conversation_id": self.conversation_id,
            "messages": self.messages,
            "session_start": self.session_start.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "message_count": len(self.messages)
        }

    def import_conversation(self, data: Dict) -> bool:
        """导入对话数据"""
        try:
            if "messages" in data:
                self.messages = data["messages"]
            if "conversation_id" in data:
                self.conversation_id = data["conversation_id"]
            if "session_start" in data:
                self.session_start = datetime.fromisoformat(data["session_start"])
            if "last_activity" in data:
                self.last_activity = datetime.fromisoformat(data["last_activity"])

            logger.info(f"对话数据导入成功，共 {len(self.messages)} 条消息")
            return True
        except Exception as e:
            logger.error(f"对话数据导入失败: {e}")
            return False

    def get_conversation_statistics(self) -> Dict:
        """获取对话统计信息"""
        user_messages = sum(1 for msg in self.messages if msg["role"] == "user")
        assistant_messages = sum(1 for msg in self.messages if msg["role"] == "assistant")

        # 计算平均消息长度
        user_avg_length = sum(len(msg["content"]) for msg in self.messages if msg["role"] == "user") / max(user_messages, 1)
        assistant_avg_length = sum(len(msg["content"]) for msg in self.messages if msg["role"] == "assistant") / max(assistant_messages, 1)

        return {
            "conversation_id": self.conversation_id,
            "total_messages": len(self.messages),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "session_duration": (datetime.now() - self.session_start).total_seconds(),
            "last_activity": self.last_activity.isoformat(),
            "average_user_message_length": round(user_avg_length, 2),
            "average_assistant_message_length": round(assistant_avg_length, 2)
        }

    def search_messages(self, query: str, role: Optional[str] = None) -> List[Dict]:
        """搜索消息"""
        results = []
        query_lower = query.lower()

        for message in self.messages:
            if role and message["role"] != role:
                continue

            if query_lower in message["content"].lower():
                results.append({
                    "id": message["id"],
                    "role": message["role"],
                    "content": message["content"],
                    "timestamp": message["timestamp"],
                    "context_snippet": self._get_context_snippet(message["content"], query)
                })

        return results

    def _get_context_snippet(self, content: str, query: str, snippet_length: int = 100) -> str:
        """获取上下文片段"""
        query_lower = query.lower()
        content_lower = content.lower()
        query_pos = content_lower.find(query_lower)

        if query_pos == -1:
            return content[:snippet_length] + "..." if len(content) > snippet_length else content

        start_pos = max(0, query_pos - snippet_length // 2)
        end_pos = min(len(content), query_pos + len(query) + snippet_length // 2)

        snippet = content[start_pos:end_pos]
        if start_pos > 0:
            snippet = "..." + snippet
        if end_pos < len(content):
            snippet = snippet + "..."

        return snippet

    def delete_message(self, message_id: str) -> bool:
        """删除特定消息"""
        for i, message in enumerate(self.messages):
            if message["id"] == message_id:
                del self.messages[i]
                logger.info(f"删除消息: {message_id}")
                return True
        return False

    def edit_message(self, message_id: str, new_content: str) -> bool:
        """编辑消息内容"""
        for message in self.messages:
            if message["id"] == message_id:
                message["content"] = new_content
                message["timestamp"] = datetime.now().isoformat()
                logger.info(f"编辑消息: {message_id}")
                return True
        return False

    def get_recent_activity(self, minutes: int = 30) -> List[Dict]:
        """获取最近的活动"""
        cutoff_time = datetime.now().timestamp() - (minutes * 60)
        recent_messages = []

        for message in self.messages:
            message_time = datetime.fromisoformat(message["timestamp"]).timestamp()
            if message_time >= cutoff_time:
                recent_messages.append(message)

        return recent_messages