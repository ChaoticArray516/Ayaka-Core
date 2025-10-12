"""
缓存服务
提供内存缓存和持久化缓存功能
"""

import json
import time
import hashlib
import sqlite3
import threading
from pathlib import Path
from typing import Any, Optional, Dict, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    ttl: int  # 生存时间（秒）
    created_at: float
    access_count: int = 0
    last_accessed: float = 0

class CacheService:
    """缓存服务"""

    def __init__(self, cache_dir: str = "cache", max_memory_entries: int = 1000):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # 内存缓存
        self._memory_cache: Dict[str, CacheEntry] = {}
        self.max_memory_entries = max_memory_entries
        self._lock = threading.RLock()

        # SQLite持久化缓存
        self.db_path = self.cache_dir / "cache.db"
        self._init_database()

        logger.info(f"CacheService初始化完成，缓存目录: {self.cache_dir}")

    def _init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cache (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        ttl INTEGER,
                        created_at REAL,
                        access_count INTEGER DEFAULT 0,
                        last_accessed REAL DEFAULT 0
                    )
                """)
                conn.commit()
            logger.info("缓存数据库初始化完成")
        except Exception as e:
            logger.error(f"缓存数据库初始化失败: {e}")

    def _generate_key(self, prefix: str, data: Any) -> str:
        """生成缓存键"""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return f"{prefix}:{hashlib.md5(data_str.encode()).hexdigest()}"

    def set(self, key: str, value: Any, ttl: int = 3600, persist: bool = False):
        """设置缓存"""
        current_time = time.time()

        with self._lock:
            # 内存缓存
            self._memory_cache[key] = CacheEntry(
                key=key,
                value=value,
                ttl=ttl,
                created_at=current_time,
                last_accessed=current_time
            )

            # 检查内存缓存大小
            self._cleanup_memory_cache()

            # 持久化缓存
            if persist:
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            INSERT OR REPLACE INTO cache
                            (key, value, ttl, created_at, last_accessed)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            key,
                            json.dumps(value, ensure_ascii=False),
                            ttl,
                            current_time,
                            current_time
                        ))
                        conn.commit()
                except Exception as e:
                    logger.error(f"持久化缓存写入失败: {e}")

        logger.debug(f"缓存设置: {key} (TTL: {ttl}s, 持久化: {persist})")

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        current_time = time.time()

        with self._lock:
            # 先查内存缓存
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                if current_time - entry.created_at < entry.ttl:
                    entry.access_count += 1
                    entry.last_accessed = current_time
                    return entry.value
                else:
                    # 过期，删除
                    del self._memory_cache[key]

            # 查持久化缓存
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT value, ttl, created_at FROM cache WHERE key = ?",
                        (key,)
                    )
                    row = cursor.fetchone()

                    if row:
                        value, ttl, created_at = row
                        if current_time - created_at < ttl:
                            # 解析并返回
                            parsed_value = json.loads(value)
                            # 更新访问信息
                            conn.execute(
                                "UPDATE cache SET access_count = access_count + 1, last_accessed = ? WHERE key = ?",
                                (current_time, key)
                            )
                            conn.commit()
                            # 加载到内存缓存
                            self._memory_cache[key] = CacheEntry(
                                key=key,
                                value=parsed_value,
                                ttl=ttl,
                                created_at=created_at,
                                last_accessed=current_time
                            )
                            return parsed_value
                        else:
                            # 过期，删除
                            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                            conn.commit()
            except Exception as e:
                logger.error(f"持久化缓存读取失败: {e}")

        return None

    def delete(self, key: str) -> bool:
        """删除缓存"""
        success = False

        with self._lock:
            # 内存缓存删除
            if key in self._memory_cache:
                del self._memory_cache[key]
                success = True

            # 持久化缓存删除
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                    if cursor.rowcount > 0:
                        success = True
                    conn.commit()
            except Exception as e:
                logger.error(f"持久化缓存删除失败: {e}")

        if success:
            logger.debug(f"缓存删除: {key}")

        return success

    def clear(self, memory_only: bool = False):
        """清空缓存"""
        with self._lock:
            # 清空内存缓存
            self._memory_cache.clear()

            if not memory_only:
                # 清空持久化缓存
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("DELETE FROM cache")
                        conn.commit()
                    logger.info("所有缓存已清空")
                except Exception as e:
                    logger.error(f"清空持久化缓存失败: {e}")
            else:
                logger.info("内存缓存已清空")

    def _cleanup_memory_cache(self):
        """清理内存缓存"""
        current_time = time.time()
        keys_to_delete = []

        # 删除过期条目
        for key, entry in self._memory_cache.items():
            if current_time - entry.created_at >= entry.ttl:
                keys_to_delete.append(key)

        # 如果还有过多条目，删除最久未访问的
        if len(self._memory_cache) - len(keys_to_delete) > self.max_memory_entries:
            sorted_entries = sorted(
                [(k, v.last_accessed) for k, v in self._memory_cache.items() if k not in keys_to_delete],
                key=lambda x: x[1]
            )
            excess_count = len(self._memory_cache) - len(keys_to_delete) - self.max_memory_entries
            keys_to_delete.extend([k for k, _ in sorted_entries[:excess_count]])

        # 执行删除
        for key in keys_to_delete:
            del self._memory_cache[key]

        if keys_to_delete:
            logger.debug(f"清理内存缓存，删除 {len(keys_to_delete)} 个条目")

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            # 内存缓存统计
            memory_entries = len(self._memory_cache)
            memory_size = sum(len(str(entry.value)) for entry in self._memory_cache.values())

            # 持久化缓存统计
            persistent_stats = {}
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("""
                        SELECT COUNT(*),
                               SUM(access_count) as total_accesses,
                               AVG(last_accessed) as avg_last_accessed
                        FROM cache
                    """)
                    row = cursor.fetchone()
                    if row:
                        persistent_stats = {
                            "entries": row[0] or 0,
                            "total_accesses": row[1] or 0,
                            "avg_last_accessed": row[2] or 0
                        }
            except Exception as e:
                logger.error(f"获取持久化缓存统计失败: {e}")

            return {
                "memory_cache": {
                    "entries": memory_entries,
                    "size_bytes": memory_size,
                    "max_entries": self.max_memory_entries
                },
                "persistent_cache": persistent_stats
            }

    def cache_llm_response(self, user_input: str, system_prompt: str,
                          response: str, ttl: int = 3600):
        """缓存LLM响应"""
        key = self._generate_key("llm", {
            "user_input": user_input,
            "system_prompt": system_prompt
        })
        self.set(key, response, ttl, persist=True)

    def get_cached_llm_response(self, user_input: str, system_prompt: str) -> Optional[str]:
        """获取缓存的LLM响应"""
        key = self._generate_key("llm", {
            "user_input": user_input,
            "system_prompt": system_prompt
        })
        return self.get(key)

    def export_cache(self, file_path: str) -> bool:
        """导出缓存数据"""
        try:
            export_data = {
                "memory_cache": {},
                "export_time": time.time()
            }

            with self._lock:
                for key, entry in self._memory_cache.items():
                    export_data["memory_cache"][key] = {
                        "value": entry.value,
                        "ttl": entry.ttl,
                        "created_at": entry.created_at,
                        "access_count": entry.access_count,
                        "last_accessed": entry.last_accessed
                    }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            logger.info(f"缓存导出完成: {file_path}")
            return True

        except Exception as e:
            logger.error(f"缓存导出失败: {e}")
            return False

    def import_cache(self, file_path: str, merge: bool = True) -> bool:
        """导入缓存数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            if not merge:
                self.clear()

            current_time = time.time()
            imported_count = 0

            with self._lock:
                for key, data in import_data.get("memory_cache", {}).items():
                    if current_time - data["created_at"] < data["ttl"]:
                        self._memory_cache[key] = CacheEntry(
                            key=key,
                            value=data["value"],
                            ttl=data["ttl"],
                            created_at=data["created_at"],
                            access_count=data["access_count"],
                            last_accessed=data["last_accessed"]
                        )
                        imported_count += 1

            logger.info(f"缓存导入完成，导入 {imported_count} 个条目")
            return True

        except Exception as e:
            logger.error(f"缓存导入失败: {e}")
            return False