# modules/ai_assistant.py
"""
AI 辅助问答模块
负责与 OpenAI 兼容的 API 进行交互，提供专业的 DSM-5 咨询服务
配置从 st.secrets 中读取，确保灵活性和安全性
"""

from typing import List, Dict, Optional
import streamlit as st


class AIAssistant:
    """
    AI 助手类，封装与 OpenAI 兼容 API 的交互
    支持从 st.secrets 读取配置，包括 API_KEY、BASE_URL 和 MODEL_NAME
    """
    
    # Session State 键名常量
    KEY_CHAT_HISTORY = "ai_chat_history"
    KEY_CLIENT_INITIALIZED = "ai_client_initialized"
    
    def __init__(self):
        """
        初始化 AI 助手
        从 st.secrets 读取 API 配置
        """
        self.client = None
        self.api_key = None
        self.base_url = None
        self.model_name = None
        
        # 从 st.secrets 读取配置
        self._load_config()
        
        # 初始化客户端
        self._init_client()
        
        # 初始化聊天历史
        if self.KEY_CHAT_HISTORY not in st.session_state:
            st.session_state[self.KEY_CHAT_HISTORY] = []
    
    def _load_config(self):
        """
        从 st.secrets 加载 API 配置
        支持的配置项：
        - api.api_key 或 api.DASHSCOPE_API_KEY: API 密钥
        - api.base_url: API 基础 URL
        - api.model_name: 模型名称
        """
        try:
            # 读取 API Key
            self.api_key = st.secrets.get("api", {}).get("api_key") or \
                          st.secrets.get("api", {}).get("DASHSCOPE_API_KEY")
            
            # 读取 Base URL
            self.base_url = st.secrets.get("api", {}).get("base_url")
            
            # 读取模型名称
            self.model_name = st.secrets.get("api", {}).get("model_name")
            
        except Exception as e:
            st.warning(f"读取 API 配置时出错: {e}")
    
    def _init_client(self):
        """
        初始化 OpenAI 客户端
        """
        if not self.api_key:
            return
        
        try:
            from openai import OpenAI
            
            # 构建客户端配置
            client_kwargs = {"api_key": self.api_key}
            
            # 如果配置了 base_url，则使用自定义 URL
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            
            self.client = OpenAI(**client_kwargs)
            st.session_state[self.KEY_CLIENT_INITIALIZED] = True
            
        except ImportError:
            st.error("未安装 openai 库，请运行: pip install openai")
        except Exception as e:
            st.error(f"初始化 AI 客户端失败: {e}")
    
    def is_configured(self) -> bool:
        """
        检查 AI 助手是否已正确配置
        
        返回:
            True 如果已配置，否则 False
        """
        return self.client is not None and self.api_key is not None
    
    def get_system_prompt(self) -> str:
        """
        获取系统提示词，定义 AI 的角色和行为
        
        返回:
            系统提示词文本
        """
        return """你是一位专业的心理学和精神医学顾问，精通 DSM-5（《精神障碍诊断与统计手册》第五版）的诊断标准。

# 你的职责是：
1. 回答关于 DSM-5 诊断标准、症状特征、鉴别诊断的专业问题,为受训咨询师提供清晰、准确的临床指导
2. 解释各种精神障碍的核心特征、诊断要点和注意事项
4. 在回答中保持专业、客观、循证的态度

# 注意事项：
- 所有回复都应以中文输出
- 简洁明了，使用纯文本输出,禁用Markdown格式（**、#、-、>等）
- 不添加总结性语句
- 不重复用户问题
"""
    
    def send_message(self, user_message: str) -> str:
        """
        发送消息并获取 AI 回复
        
        参数:
            user_message: 用户输入的消息
        
        返回:
            AI 的回复文本
        """
        if not self.is_configured():
            return "⚠️ AI 助手未配置。请在 .streamlit/secrets.toml 中配置 API 密钥。"
        
        try:
            # 构建消息列表
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
            ]
            
            # 添加历史消息（保留最近 10 轮对话）
            history = st.session_state.get(self.KEY_CHAT_HISTORY, [])
            for msg in history[-20:]:  # 保留最近 20 条消息（10 轮）
                messages.append({
                    "role": msg.get("role"),
                    "content": msg.get("content")
                })
            
            # 添加当前消息
            messages.append({"role": "user", "content": user_message})
            
            # 调用 API
            model = self.model_name 
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                # temperature=0.7,
                max_tokens=2000
            )
            
            # 提取回复内容
            reply = response.choices[0].message.content
            print(reply)

            # 保存到历史
            self._add_to_history("user", user_message)
            self._add_to_history("assistant", reply)
            
            return reply
            
        except Exception as e:
            error_msg = f"调用 AI 服务时出错: {str(e)}"
            st.error(error_msg)
            return f"⚠️ {error_msg}"
    
    def _add_to_history(self, role: str, content: str):
        """
        添加消息到聊天历史
        
        参数:
            role: 消息角色（"user" 或 "assistant"）
            content: 消息内容
        """
        if self.KEY_CHAT_HISTORY not in st.session_state:
            st.session_state[self.KEY_CHAT_HISTORY] = []
        
        st.session_state[self.KEY_CHAT_HISTORY].append({
            "role": role,
            "content": content
        })
    
    def clear_history(self):
        """
        清空聊天历史
        """
        st.session_state[self.KEY_CHAT_HISTORY] = []
    
    def get_history(self) -> List[Dict]:
        """
        获取聊天历史
        
        返回:
            聊天历史列表
        """
        return st.session_state.get(self.KEY_CHAT_HISTORY, [])
    
    def get_config_info(self) -> Dict:
        """
        获取当前配置信息（用于调试，隐藏敏感信息）
        
        返回:
            配置信息字典
        """
        return {
            "base_url": self.base_url or "默认 (OpenAI)",
            "model_name": self.model_name or "默认 (qwen-plus)",
            "api_key_configured": bool(self.api_key),
            "client_initialized": self.client is not None
        }
