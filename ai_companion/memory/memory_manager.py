"""
记忆管理器
负责读取和管理聊天记忆，提供上下文信息
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
import logging

from .chat_history_manager import ChatHistoryManager

logger = logging.getLogger(__name__)

class MemoryManager:
    """记忆管理器"""

    def __init__(self, chat_history_manager: ChatHistoryManager):
        """
        初始化记忆管理器

        Args:
            chat_history_manager: 聊天历史管理器实例
        """
        self.chat_history_manager = chat_history_manager
        self.memory_cache = {}
        self.cache_expiry = 3600  # 缓存1小时

        logger.info("MemoryManager初始化完成")

    def get_relevant_memories(self, query: str, limit: int = 10) -> List[str]:
        """
        根据查询获取相关记忆

        Args:
            query: 查询内容
            limit: 返回记忆数量限制

        Returns:
            相关记忆列表
        """
        # 检查缓存
        cache_key = f"memories_{hash(query)}_{limit}"
        if cache_key in self.memory_cache:
            cache_data = self.memory_cache[cache_key]
            if datetime.now().timestamp() - cache_data['timestamp'] < self.cache_expiry:
                return cache_data['memories']

        # 获取当前会话记忆
        current_memories = self._extract_current_session_memories(query, limit // 2)

        # 获取历史记忆
        historical_memories = self._extract_historical_memories(query, limit // 2)

        # 合并和排序
        all_memories = current_memories + historical_memories
        relevant_memories = self._rank_memories_by_relevance(all_memories, query)[:limit]

        # 缓存结果
        self.memory_cache[cache_key] = {
            'memories': relevant_memories,
            'timestamp': datetime.now().timestamp()
        }

        return relevant_memories

    def get_user_preferences(self) -> Dict[str, Any]:
        """
        从聊天历史中提取用户偏好

        Returns:
            用户偏好字典
        """
        preferences = {
            'topics': [],
            'style': 'normal',
            'frequency': 'medium',
            'persona_preferences': {},
            'mentioned_interests': [],
            'avoided_topics': []
        }

        try:
            # 分析最近的聊天记录
            messages = self.chat_history_manager.get_session_messages(100)

            # 提取话题偏好
            topic_keywords = self._extract_topic_keywords(messages)
            preferences['topics'] = topic_keywords

            # 提取人格偏好
            persona_counts = {}
            for msg in messages:
                persona = msg.get('persona')
                if persona:
                    persona_counts[persona] = persona_counts.get(persona, 0) + 1

            if persona_counts:
                preferred_persona = max(persona_counts.items(), key=lambda x: x[1])
                preferences['persona_preferences'] = {
                    'preferred': preferred_persona[0],
                    'usage_count': preferred_persona[1]
                }

            # 提取兴趣点
            interests = self._extract_user_interests(messages)
            preferences['mentioned_interests'] = interests

            # 分析交互频率
            if len(messages) > 0:
                time_span = self._calculate_time_span(messages)
                if time_span > 0:
                    frequency = len(messages) / time_span
                    if frequency > 0.1:  # 高频
                        preferences['frequency'] = 'high'
                    elif frequency < 0.01:  # 低频
                        preferences['frequency'] = 'low'
                    else:
                        preferences['frequency'] = 'medium'

        except Exception as e:
            logger.error(f"提取用户偏好失败: {e}")

        return preferences

    def get_conversation_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        获取指定天数内的对话摘要

        Args:
            days: 天数

        Returns:
            对话摘要字典
        """
        summary = {
            'total_messages': 0,
            'user_messages': 0,
            'ai_messages': 0,
            'active_days': 0,
            'most_active_day': None,
            'average_messages_per_day': 0,
            'top_topics': [],
            'persona_usage': {},
            'sentiment_trend': 'neutral'
        }

        try:
            # 获取指定天数内的历史文件
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_messages = []

            # 搜索当前会话
            current_messages = self.chat_history_manager.get_session_messages(1000)
            for msg in current_messages:
                try:
                    msg_time = datetime.fromisoformat(msg.get('timestamp', ''))
                    if msg_time >= cutoff_date:
                        recent_messages.append(msg)
                except:
                    continue

            # 搜索历史文件
            for file_path in self.chat_history_manager.get_history_files(50):
                messages = self.chat_history_manager.load_history_file(file_path)
                for msg in messages:
                    try:
                        msg_time = datetime.fromisoformat(msg.get('timestamp', ''))
                        if msg_time >= cutoff_date:
                            recent_messages.append(msg)
                    except:
                        continue

            # 统计信息
            summary['total_messages'] = len(recent_messages)
            summary['user_messages'] = sum(1 for msg in recent_messages if msg.get('role') == 'user')
            summary['ai_messages'] = sum(1 for msg in recent_messages if msg.get('role') == 'assistant')

            # 活跃天数
            active_dates = set()
            for msg in recent_messages:
                try:
                    msg_date = datetime.fromisoformat(msg.get('timestamp', '')).date()
                    active_dates.add(msg_date)
                except:
                    continue

            summary['active_days'] = len(active_dates)
            if summary['active_days'] > 0:
                summary['average_messages_per_day'] = summary['total_messages'] / summary['active_days']

            # 人格使用统计
            persona_usage = {}
            for msg in recent_messages:
                persona = msg.get('persona', 'unknown')
                persona_usage[persona] = persona_usage.get(persona, 0) + 1
            summary['persona_usage'] = persona_usage

            # 提取热门话题
            summary['top_topics'] = self._extract_topic_keywords(recent_messages[:50])

        except Exception as e:
            logger.error(f"生成对话摘要失败: {e}")

        return summary

    def get_context_for_llm(self, query: str, max_context: int = 500) -> str:
        """
        为LLM提供上下文信息

        Args:
            query: 当前查询
            max_context: 最大上下文长度

        Returns:
            上下文字符串
        """
        try:
            # 获取相关记忆
            relevant_memories = self.get_relevant_memories(query, limit=5)

            # 获取用户偏好
            preferences = self.get_user_preferences()

            # 构建上下文
            context_parts = []

            if relevant_memories:
                context_parts.append("相关记忆:")
                for memory in relevant_memories:
                    context_parts.append(f"- {memory}")

            if preferences['topics']:
                context_parts.append(f"用户感兴趣的话题: {', '.join(preferences['topics'][:5])}")

            if preferences['persona_preferences']:
                preferred_persona = preferences['persona_preferences']['preferred']
                context_parts.append(f"用户偏好的人格状态: {preferred_persona}")

            context = "\n".join(context_parts)

            # 限制长度
            if len(context) > max_context:
                context = context[:max_context] + "..."

            return context

        except Exception as e:
            logger.error(f"生成LLM上下文失败: {e}")
            return ""

    def _extract_current_session_memories(self, query: str, limit: int) -> List[str]:
        """从当前会话提取记忆"""
        memories = []
        messages = self.chat_history_manager.get_session_messages(50)

        # 查找包含查询关键词的消息
        query_lower = query.lower()
        for msg in messages:
            content = msg.get('content', '').lower()
            if any(word in content for word in query_lower.split() if len(word) > 2):
                memories.append(f"[{msg.get('role', 'unknown')}] {msg.get('content', '')}")

        return memories[:limit]

    def _extract_historical_memories(self, query: str, limit: int) -> List[str]:
        """从历史记录提取记忆"""
        memories = []

        # 搜索历史文件
        for file_path in self.chat_history_manager.get_history_files(10):
            messages = self.chat_history_manager.load_history_file(file_path)
            query_lower = query.lower()

            for msg in messages:
                content = msg.get('content', '').lower()
                if any(word in content for word in query_lower.split() if len(word) > 2):
                    memories.append(f"[{msg.get('role', 'unknown')}] {msg.get('content', '')}")
                    if len(memories) >= limit:
                        break

            if len(memories) >= limit:
                break

        return memories[:limit]

    def _rank_memories_by_relevance(self, memories: List[str], query: str) -> List[str]:
        """根据相关性对记忆进行排序"""
        query_words = set(query.lower().split())
        scored_memories = []

        for memory in memories:
            memory_lower = memory.lower()
            score = 0

            # 计算相关性分数
            for word in query_words:
                if len(word) > 2:  # 忽略短词
                    count = memory_lower.count(word)
                    score += count * len(word)  # 长词权重更高

            scored_memories.append((memory, score))

        # 按分数排序
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in scored_memories if _ > 0]

    def _extract_topic_keywords(self, messages: List[Dict]) -> List[str]:
        """提取话题关键词"""
        # 简单的关键词提取
        common_words = {'的', '是', '我', '你', '他', '她', '它', '们', '这', '那', '有', '没有', '在', '和', '与', '或', '但', '如果'}
        word_count = {}

        for msg in messages:
            content = msg.get('content', '')
            words = re.findall(r'\b\w+\b', content.lower())

            for word in words:
                if len(word) > 2 and word not in common_words:
                    word_count[word] = word_count.get(word, 0) + 1

        # 返回最常见的词
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:10]]

    def _extract_user_interests(self, messages: List[Dict]) -> List[str]:
        """提取用户兴趣"""
        interests = []

        # 查找用户消息中提到的话题
        for msg in messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '').lower()

                # 简单的兴趣检测
                interest_patterns = [
                    r'我喜欢(.+)',
                    r'我对(.+)感兴趣',
                    r'我最爱(.+)',
                    r'我想了解(.+)',
                    r'告诉我关于(.+)',
                ]

                for pattern in interest_patterns:
                    matches = re.findall(pattern, content)
                    interests.extend(matches)

        return list(set(interests))[:10]  # 去重并限制数量

    def _calculate_time_span(self, messages: List[Dict]) -> float:
        """计算消息时间跨度（天）"""
        if len(messages) < 2:
            return 0

        try:
            times = []
            for msg in messages:
                timestamp = msg.get('timestamp')
                if timestamp:
                    times.append(datetime.fromisoformat(timestamp))

            if len(times) >= 2:
                time_span = (max(times) - min(times)).total_seconds() / 86400  # 转换为天
                return time_span

        except Exception as e:
            logger.error(f"计算时间跨度失败: {e}")

        return 0

    def clear_cache(self):
        """清空缓存"""
        self.memory_cache.clear()
        logger.info("记忆缓存已清空")