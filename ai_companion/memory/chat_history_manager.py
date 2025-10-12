"""
聊天历史管理器
负责管理和存储聊天记录
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ChatHistoryManager:
    """聊天历史管理器"""

    def __init__(self, history_dir: str = None):
        """
        初始化聊天历史管理器

        Args:
            history_dir: 聊天历史存储目录
        """
        if history_dir is None:
            # 默认存储目录
            current_dir = Path(__file__).parent
            history_dir = current_dir / "memory" / "chathistory"

        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)

        # 当前会话文件
        self.session_file = self.history_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.current_session = []

        logger.info(f"ChatHistoryManager初始化完成，历史目录: {self.history_dir}")

    def add_message(self, role: str, content: str, persona: str = None, yandere_level: int = None, timestamp: str = None):
        """
        添加消息到当前会话

        Args:
            role: 消息角色 (user/assistant)
            content: 消息内容
            persona: 当前人格状态
            yandere_level: 当前病娇等级
            timestamp: 时间戳
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp,
            "persona": persona,
            "yandere_level": yandere_level
        }

        self.current_session.append(message)

        # 实时保存到文件
        self._save_session()

        logger.debug(f"添加消息: {role} - {content[:50]}...")

    def get_session_messages(self, limit: int = 50) -> List[Dict]:
        """
        获取当前会话的消息

        Args:
            limit: 返回消息数量限制

        Returns:
            消息列表
        """
        return self.current_session[-limit:] if limit > 0 else self.current_session

    def get_history_files(self, limit: int = 10) -> List[str]:
        """
        获取历史文件列表

        Args:
            limit: 返回文件数量限制

        Returns:
            历史文件路径列表
        """
        files = []
        for file_path in sorted(self.history_dir.glob("session_*.json"), reverse=True):
            files.append(str(file_path))
            if len(files) >= limit:
                break
        return files

    def load_history_file(self, file_path: str) -> List[Dict]:
        """
        加载指定历史文件

        Args:
            file_path: 历史文件路径

        Returns:
            消息列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('messages', [])
        except Exception as e:
            logger.error(f"加载历史文件失败 {file_path}: {e}")
            return []

    def search_history(self, keyword: str, limit: int = 20) -> List[Dict]:
        """
        搜索历史记录

        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            匹配的消息列表
        """
        results = []

        # 搜索当前会话
        for msg in self.current_session:
            if keyword.lower() in msg.get('content', '').lower():
                results.append(msg)
                if len(results) >= limit:
                    return results

        # 搜索历史文件
        for file_path in self.get_history_files():
            messages = self.load_history_file(file_path)
            for msg in messages:
                if keyword.lower() in msg.get('content', '').lower():
                    results.append(msg)
                    if len(results) >= limit:
                        return results

        return results

    def get_recent_memories(self, limit: int = 10) -> List[str]:
        """
        获取最近的记忆片段（用于上下文）

        Args:
            limit: 返回记忆数量限制

        Returns:
            记忆片段列表
        """
        memories = []

        # 从当前会话提取
        for msg in reversed(self.current_session[-limit*2:]):
            content = msg.get('content', '')
            if len(content) > 50:  # 只保留有意义的内容
                memories.append(f"[{msg.get('role', 'unknown')}] {content}")
                if len(memories) >= limit:
                    break

        return list(reversed(memories))

    def clear_current_session(self):
        """清空当前会话"""
        self.current_session = []
        if self.session_file.exists():
            self.session_file.unlink()
        logger.info("当前会话已清空")

    def _save_session(self):
        """保存当前会话到文件"""
        try:
            session_data = {
                "session_id": self.session_file.stem,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "message_count": len(self.current_session),
                "messages": self.current_session
            }

            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"保存会话失败: {e}")

    def get_session_statistics(self) -> Dict:
        """
        获取会话统计信息

        Returns:
            统计信息字典
        """
        total_files = len(list(self.history_dir.glob("session_*.json")))
        total_messages = len(self.current_session)

        # 计算消息类型分布
        user_messages = sum(1 for msg in self.current_session if msg.get('role') == 'user')
        ai_messages = sum(1 for msg in self.current_session if msg.get('role') == 'assistant')

        return {
            "total_sessions": total_files,
            "current_messages": total_messages,
            "user_messages": user_messages,
            "ai_messages": ai_messages,
            "current_session_file": str(self.session_file),
            "history_directory": str(self.history_dir)
        }

    def archive_old_sessions(self, days: int = 7):
        """
        归档旧会话文件

        Args:
            days: 保留天数，超过此天数的文件将被归档
        """
        archive_dir = self.history_dir / "archive"
        archive_dir.mkdir(exist_ok=True)

        cutoff_date = datetime.now().timestamp() - (days * 24 * 3600)
        archived_count = 0

        for file_path in self.history_dir.glob("session_*.json"):
            if file_path.stat().st_mtime < cutoff_date:
                try:
                    archive_path = archive_dir / file_path.name
                    file_path.rename(archive_path)
                    archived_count += 1
                except Exception as e:
                    logger.error(f"归档文件失败 {file_path}: {e}")

        logger.info(f"归档了 {archived_count} 个旧会话文件")
        return archived_count