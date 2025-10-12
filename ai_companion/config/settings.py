"""
配置管理器
管理应用的各种配置设置
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/settings.json"
        self.config_data: Dict[str, Any] = {}
        self.default_config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "app": {
                "name": "AI虚拟伴侣系统",
                "version": "1.0.0",
                "debug": False,
                "host": "0.0.0.0",
                "port": 5000,
                "secret_key": "ai_companion_web_secret_key"
            },
            "llm": {
                "provider": "zhipu",
                "api_key": "942e8f9637dc41ceb804246cdbe34d79.9IfjsfIblnkwadJN",
                "base_url": "https://open.bigmodel.cn/api/coding/paas/v4",
                "model": "glm-4.5",
                "max_tokens": 1000,
                "temperature": 0.7,
                "timeout": 30
            },
            "persona": {
                "default_state": "private",
                "default_yandere_level": 1,
                "auto_save": True,
                "save_interval": 300  # 5分钟
            },
            "conversation": {
                "max_history": 50,
                "auto_save": True,
                "export_format": "json"
            },
            "cache": {
                "enable_memory_cache": True,
                "enable_persistent_cache": True,
                "max_memory_entries": 1000,
                "default_ttl": 3600,
                "cache_dir": "cache"
            },
            "web": {
                "template_folder": "web/templates",
                "static_folder": "web/static",
                "enable_websocket": True,
                "cors_origins": ["*"]
            },
            "logging": {
                "level": "INFO",
                "file": "logs/ai_companion.log",
                "max_size": "10MB",
                "backup_count": 5,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }

    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)

                # 合并配置（使用加载的配置覆盖默认配置）
                self.config_data = self._merge_config(self.default_config, loaded_config)
                logger.info(f"配置文件加载成功: {self.config_path}")
                return True
            else:
                # 使用默认配置并创建配置文件
                self.config_data = self.default_config.copy()
                self.save_config()
                logger.info(f"使用默认配置并创建配置文件: {self.config_path}")
                return True

        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            self.config_data = self.default_config.copy()
            return False

    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)

            logger.info(f"配置文件保存成功: {self.config_path}")
            return True

        except Exception as e:
            logger.error(f"配置文件保存失败: {e}")
            return False

    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置"""
        result = default.copy()

        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value

        return result

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config_data

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> bool:
        """设置配置值"""
        keys = key.split('.')
        config = self.config_data

        try:
            # 导航到最后一级的父级
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]

            # 设置值
            config[keys[-1]] = value
            return True

        except Exception as e:
            logger.error(f"设置配置失败: {e}")
            return False

    def get_app_config(self) -> Dict[str, Any]:
        """获取应用配置"""
        return self.get("app", {})

    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置"""
        return self.get("llm", {})

    def get_persona_config(self) -> Dict[str, Any]:
        """获取人格配置"""
        return self.get("persona", {})

    def get_conversation_config(self) -> Dict[str, Any]:
        """获取对话配置"""
        return self.get("conversation", {})

    def get_cache_config(self) -> Dict[str, Any]:
        """获取缓存配置"""
        return self.get("cache", {})

    def get_web_config(self) -> Dict[str, Any]:
        """获取Web配置"""
        return self.get("web", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get("logging", {})

    def update_llm_config(self, **kwargs) -> bool:
        """更新LLM配置"""
        for key, value in kwargs.items():
            if not self.set(f"llm.{key}", value):
                return False
        return self.save_config()

    def update_app_config(self, **kwargs) -> bool:
        """更新应用配置"""
        for key, value in kwargs.items():
            if not self.set(f"app.{key}", value):
                return False
        return self.save_config()

    def validate_config(self) -> Dict[str, Any]:
        """验证配置"""
        issues = []

        # 验证应用配置
        app_config = self.get_app_config()
        if not app_config.get("host"):
            issues.append("应用主机地址未设置")
        if not isinstance(app_config.get("port"), int) or app_config.get("port") <= 0:
            issues.append("应用端口必须大于0")

        # 验证LLM配置
        llm_config = self.get_llm_config()
        if not llm_config.get("api_key"):
            issues.append("LLM API密钥未设置")
        if not llm_config.get("base_url"):
            issues.append("LLM基础URL未设置")
        if not llm_config.get("model"):
            issues.append("LLM模型名称未设置")
        if not isinstance(llm_config.get("max_tokens"), int) or llm_config.get("max_tokens") <= 0:
            issues.append("LLM最大token数必须大于0")
        if not isinstance(llm_config.get("temperature"), (int, float)) or not (0 <= llm_config.get("temperature") <= 2):
            issues.append("LLM温度参数必须在0-2之间")

        # 验证人格配置
        persona_config = self.get_persona_config()
        valid_states = ["private", "public", "yandere", "tsundere", "deredere"]
        if persona_config.get("default_state") not in valid_states:
            issues.append("默认人格状态无效")
        if not isinstance(persona_config.get("default_yandere_level"), int) or not (0 <= persona_config.get("default_yandere_level") <= 4):
            issues.append("默认病娇等级必须在0-4之间")

        return {
            "valid": len(issues) == 0,
            "issues": issues
        }

    def export_config(self, file_path: str) -> bool:
        """导出配置"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            logger.info(f"配置导出成功: {file_path}")
            return True
        except Exception as e:
            logger.error(f"配置导出失败: {e}")
            return False

    def import_config(self, file_path: str, merge: bool = True) -> bool:
        """导入配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            if merge:
                self.config_data = self._merge_config(self.config_data, imported_config)
            else:
                self.config_data = imported_config

            return self.save_config()

        except Exception as e:
            logger.error(f"配置导入失败: {e}")
            return False

    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        self.config_data = self.default_config.copy()
        return self.save_config()

    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config_data.copy()