"""
LLM客户端
支持GLM4.5V和其他大语言模型的API调用
"""

import json
import time
import requests
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """LLM提供商枚举"""
    ZHIPU = "zhipu"          # AI AI
    OPENAI = "openai"        # OpenAI
    ANTHROPIC = "anthropic"  # Anthropic
    AZURE = "azure"          # Azure OpenAI
    LOCAL = "local"          # 本地模型

@dataclass
class LLMConfig:
    """LLM配置"""
    api_key: str
    base_url: str
    model: str
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    provider: LLMProvider = LLMProvider.ZHIPU

class LLMClient:
    """LLM客户端"""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or self._get_default_config()
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "AI-Companion/1.0"
        })

        logger.info(f"LLMClient初始化完成，提供商: {self.config.provider.value}, 模型: {self.config.model}")

    def _get_default_config(self) -> LLMConfig:
        """获取默认配置"""
        return LLMConfig(
            api_key="942e8f9637dc41ceb804246cdbe34d79.9IfjsfIblnkwadJN",
            base_url="https://open.bigmodel.cn/api/coding/paas/v4",
            model="glm-4.5",
            max_tokens=1000,
            temperature=0.7,
            provider=LLMProvider.ZHIPU
        )

    def update_config(self, **kwargs) -> None:
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"配置更新: {key} = {value}")

    def generate_response(self, user_input: str, system_prompt: str,
                         conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """生成AI回复"""
        try:
            # 清理输入内容
            user_input = user_input.replace('\x00', '').strip()
            system_prompt = system_prompt.replace('\x00', '').strip()

            # 构建消息
            messages = [{"role": "system", "content": system_prompt}]

            # 添加对话历史并清理
            if conversation_history:
                for msg in conversation_history[-5:]:  # 最近5轮对话
                    if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"].replace('\x00', '').strip()
                        })

            messages.append({"role": "user", "content": user_input})

            # 调用API
            response_data = self._call_api(messages)

            if response_data.get("success"):
                return {
                    "success": True,
                    "response": response_data["content"],
                    "model": self.config.model,
                    "provider": self.config.provider.value,
                    "tokens_used": response_data.get("tokens_used", 0),
                    "response_time": response_data.get("response_time", 0)
                }
            else:
                return {
                    "success": False,
                    "error": response_data.get("error", "未知错误"),
                    "error_code": response_data.get("error_code")
                }

        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            return {
                "success": False,
                "error": f"生成回复时发生错误: {str(e)}"
            }

    def _call_api(self, messages: List[Dict]) -> Dict[str, Any]:
        """调用LLM API"""
        start_time = time.time()

        try:
            # 根据提供商构建请求
            if self.config.provider == LLMProvider.ZHIPU:
                response = self._call_zhipu_api(messages)
            elif self.config.provider == LLMProvider.OPENAI:
                response = self._call_openai_api(messages)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                response = self._call_anthropic_api(messages)
            else:
                return {"success": False, "error": f"不支持的提供商: {self.config.provider}"}

            response_time = time.time() - start_time
            response["response_time"] = response_time

            return response

        except requests.exceptions.Timeout:
            return {"success": False, "error": "API请求超时", "error_code": "timeout"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "API连接失败", "error_code": "connection_error"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"API请求失败: {str(e)}", "error_code": "request_error"}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {str(e)}", "error_code": "unknown_error"}

    def _call_zhipu_api(self, messages: List[Dict]) -> Dict[str, Any]:
        """调用AI AI API"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}"
        }

        # 确保消息内容正确处理Unicode字符
        sanitized_messages = []
        for message in messages:
            sanitized_messages.append({
                "role": message["role"],
                "content": message["content"].replace('\x00', '').strip()
            })

        data = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": sanitized_messages
        }

        try:
            response = self.session.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )
        except Exception as e:
            logger.error(f"AI API请求失败: {e}")
            return {"success": False, "error": f"API请求失败: {str(e)}"}

        if response.status_code == 200:
            try:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    tokens_used = result.get("usage", {}).get("total_tokens", 0)

                    return {
                        "success": True,
                        "content": content,
                        "tokens_used": tokens_used,
                        "raw_response": result
                    }
                else:
                    return {"success": False, "error": "API返回格式错误"}
            except json.JSONDecodeError as e:
                return {"success": False, "error": f"JSON解析失败: {str(e)}", "error_code": "json_parse_error"}
        else:
            error_msg = f"API调用失败: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('error', {}).get('message', '未知错误')}"
            except json.JSONDecodeError:
                error_msg += f" - {response.text}"

            return {"success": False, "error": error_msg, "error_code": response.status_code}

    def _call_openai_api(self, messages: List[Dict]) -> Dict[str, Any]:
        """调用OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}"
        }

        data = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": messages
        }

        response = self.session.post(
            f"{self.config.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=self.config.timeout
        )

        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)

                return {
                    "success": True,
                    "content": content,
                    "tokens_used": tokens_used,
                    "raw_response": result
                }
            else:
                return {"success": False, "error": "API返回格式错误"}
        else:
            return {"success": False, "error": f"API调用失败: {response.status_code}", "error_code": response.status_code}

    def _call_anthropic_api(self, messages: List[Dict]) -> Dict[str, Any]:
        """调用Anthropic API"""
        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01"
        }

        # 转换消息格式
        system_message = ""
        formatted_messages = []

        for message in messages:
            if message["role"] == "system":
                system_message = message["content"]
            else:
                formatted_messages.append(message)

        data = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": formatted_messages
        }

        if system_message:
            data["system"] = system_message

        response = self.session.post(
            f"{self.config.base_url}/messages",
            headers=headers,
            json=data,
            timeout=self.config.timeout
        )

        if response.status_code == 200:
            result = response.json()
            if "content" in result and len(result["content"]) > 0:
                content = result["content"][0]["text"]
                tokens_used = result.get("usage", {}).get("input_tokens", 0) + result.get("usage", {}).get("output_tokens", 0)

                return {
                    "success": True,
                    "content": content,
                    "tokens_used": tokens_used,
                    "raw_response": result
                }
            else:
                return {"success": False, "error": "API返回格式错误"}
        else:
            return {"success": False, "error": f"API调用失败: {response.status_code}", "error_code": response.status_code}

    def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        test_message = "你好，请回复'连接测试成功'"

        try:
            response = self.generate_response(
                test_message,
                "你是一个测试助手，请简短回复。"
            )

            if response.get("success"):
                return {
                    "success": True,
                    "message": "API连接测试成功",
                    "provider": self.config.provider.value,
                    "model": self.config.model,
                    "response_time": response.get("response_time", 0)
                }
            else:
                return {
                    "success": False,
                    "message": f"API连接测试失败: {response.get('error')}",
                    "error_code": response.get("error_code")
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"连接测试异常: {str(e)}"
            }

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": self.config.provider.value,
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "base_url": self.config.base_url,
            "timeout": self.config.timeout
        }

    def stream_generate_response(self, user_input: str, system_prompt: str,
                                conversation_history: Optional[List[Dict]] = None):
        """流式生成回复（暂不实现）"""
        # TODO: 实现流式响应
        yield {
            "type": "error",
            "content": "流式响应暂未实现"
        }

    def estimate_tokens(self, text: str) -> int:
        """估算token数量"""
        # 简单估算：中文1字符≈1token，英文1token≈4字符
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_chars = len(text) - chinese_chars
        return chinese_chars + (english_chars // 4)

    def validate_config(self) -> Dict[str, Any]:
        """验证配置"""
        issues = []

        if not self.config.api_key:
            issues.append("API密钥未设置")
        elif len(self.config.api_key) < 10:
            issues.append("API密钥长度不足")

        if not self.config.base_url:
            issues.append("API基础URL未设置")
        elif not (self.config.base_url.startswith("http://") or self.config.base_url.startswith("https://")):
            issues.append("API基础URL格式错误")

        if not self.config.model:
            issues.append("模型名称未设置")

        if self.config.max_tokens <= 0:
            issues.append("最大token数必须大于0")

        if not (0 <= self.config.temperature <= 2):
            issues.append("温度参数必须在0-2之间")

        if self.config.timeout <= 0:
            issues.append("超时时间必须大于0")

        return {
            "valid": len(issues) == 0,
            "issues": issues
        }