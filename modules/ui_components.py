# modules/ui_components.py
"""
UI 组件模块
封装 Streamlit 界面组件的渲染逻辑
包含问题卡片、警告提示、诊断结果、聊天界面等组件
"""

import streamlit as st
from typing import Optional, Dict, List, Callable


def render_question_card(question: str, node_id: str = ""):
    """
    渲染问题卡片，显示当前节点的问题
    
    参数:
        question: 问题文本
        node_id: 当前节点 ID（可选，用于调试）
    """
    st.markdown("---")
    
    # 使用卡片样式展示问题
    with st.container():
        st.markdown("### 📋 当前问题")
        st.markdown(f"<div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 4px solid #4CAF50;'>"
                   f"<p style='font-size: 18px; margin: 0; color: #333;'>{question}</p>"
                   f"</div>", unsafe_allow_html=True)
        
        # 调试模式下显示节点 ID
        if node_id and st.session_state.get("debug_mode", False):
            st.caption(f"节点 ID: {node_id}")


def render_warning_alert(warning: Optional[Dict]):
    """
    渲染警告提示，根据级别显示不同的警告样式
    
    参数:
        warning: 警告信息字典，包含"级别"和"信息"字段，如果为 None 则不显示
    """
    if not warning:
        return
    
    level = warning.get("级别", "")
    message = warning.get("信息", "")
    
    if not level or not message:
        return
    
    # 根据级别选择不同的警告样式
    level_lower = level.strip().lower()
    
    if "高" in level_lower or "danger" in level_lower:
        # 高危警告 - 使用红色错误框
        st.error(f"⚠️ **{level}警告**\n\n{message}")
    elif "中" in level_lower or "warning" in level_lower:
        # 中危警告 - 使用黄色警告框
        st.warning(f"⚠️ **{level}警告**\n\n{message}")
    else:
        # 其他级别 - 使用蓝色信息框
        st.info(f"ℹ️ **{level}提示**\n\n{message}")


def render_choice_buttons(on_yes: Callable, on_no: Callable, on_back: Callable = None, disabled: bool = False, can_go_back: bool = False):
    """
    渲染【是】和【否】选择按钮，以及回退按钮
    
    参数:
        on_yes: 点击"是"按钮时的回调函数
        on_no: 点击"否"按钮时的回调函数
        on_back: 点击"回退"按钮时的回调函数
        disabled: 是否禁用按钮
        can_go_back: 是否可以回退
    """
    st.markdown("### 🎯 请选择")
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        if st.button("✅ 是", key="btn_yes", disabled=disabled, use_container_width=True):
            on_yes()
            st.rerun()
    
    with col2:
        if st.button("❌ 否", key="btn_no", disabled=disabled, use_container_width=True):
            on_no()
            st.rerun()
    
    with col3:
        back_disabled = disabled or not can_go_back
        back_help = "返回上一个问题" if can_go_back else "已经是第一个问题"
        if st.button("⬅️ 回退", key="btn_back", disabled=back_disabled, use_container_width=True, help=back_help):
            if on_back:
                on_back()
                st.rerun()


def render_note_section(current_note: str = "", on_save: Callable = None):
    """
    渲染笔记输入区域
    
    参数:
        current_note: 当前笔记内容
        on_save: 保存笔记时的回调函数
    """
    st.markdown("---")
    st.markdown("### 📝 当前笔记")
    
    # 使用 session_state 来管理输入框的值
    note_key = "current_note_input"
    if note_key not in st.session_state:
        st.session_state[note_key] = current_note
    
    # 文本输入区域
    note_content = st.text_area(
        "记录当前情况（可选）",
        value=st.session_state[note_key],
        key=note_key,
        placeholder="在此记录当前问题的具体情况、观察到的症状、患者的补充说明等...",
        height=100
    )
    
    # 保存按钮
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("💾 保存笔记", key="save_note_btn"):
            if on_save:
                on_save(note_content)
                st.success("笔记已保存！")
                st.rerun()
    
    with col2:
        if note_content.strip():
            st.caption(f"当前笔记字数: {len(note_content.strip())} 字")


def render_diagnosis_result(diagnosis: str, summary: str, report_text: str):
    """
    渲染诊断结果展示界面
    
    参数:
        diagnosis: 诊断结果文本
        summary: 报告摘要
        report_text: 完整的报告文本（用于下载）
    """
    st.markdown("---")
    st.markdown("## 🏥 诊断结果")
    
    # 诊断结果卡片
    with st.container():
        st.markdown("<div style='background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50;'>"
                   "<h3 style='color: #2e7d32; margin-top: 0;'>✅ 诊断结论</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 20px; font-weight: bold; color: #1b5e20;'>{diagnosis}</p>",
                   unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("### 📝 报告摘要")
    st.markdown(f"<div style='background-color: #f5f5f5; padding: 15px; border-radius: 8px;'>"
               f"<p style='font-size: 16px; color: #555;'>{summary}</p>"
               f"</div>", unsafe_allow_html=True)
    
    # 操作按钮
    st.markdown("### 📋 报告操作")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 复制报告按钮
        st.code(report_text, language="text")
        if st.button("📋 复制报告到剪贴板", key="copy_report"):
            # 使用 JavaScript 复制到剪贴板
            # 先处理报告文本中的反引号，避免与 JavaScript 模板字符串冲突
            escaped_text = report_text.replace('`', '\\`')
            st.markdown(f"""
            <script>
                navigator.clipboard.writeText(`{escaped_text}`);
            </script>
            """, unsafe_allow_html=True)
            st.success("报告已复制到剪贴板！")
    
    with col2:
        # 下载报告按钮
        st.download_button(
            label="📥 下载报告",
            data=report_text,
            file_name=f"诊断报告_{diagnosis.replace(' ', '_')}.txt",
            mime="text/plain",
            key="download_report"
        )


def render_progress_indicator():
    """
    渲染访谈进度指示器
    """
    from .interview_engine import get_interview_path
    
    path = get_interview_path()
    step_count = len(path)
    
    if step_count > 0:
        st.markdown(f"<p style='color: #666; font-size: 14px;'>已回答 {step_count} 个问题</p>",
                   unsafe_allow_html=True)


def render_chat_interface(ai_assistant, chat_history_key: str = "chat_messages", context: dict = None):
    """
    渲染 AI 辅助聊天界面（右侧栏版本）
    
    参数:
        ai_assistant: AIAssistant 实例
        chat_history_key: session_state 中存储聊天历史的键名
        context: 访谈上下文信息，包含当前问题、历史回答等
    """
    st.markdown("### 🤖 AI 专业辅助")
    
    # 显示当前上下文信息
    if context and context.get("current_question"):
        with st.expander("📌 当前问题上下文", expanded=False):
            st.markdown(f"**访谈主题:** {context.get('tree_name', '')}")
            st.markdown(f"**当前问题:** {context.get('current_question', '')}")
            st.markdown(f"**已回答:** {context.get('total_steps', 0)} 个问题")
            
            # 显示历史问答
            answered = context.get("answered_questions", [])
            if answered:
                st.markdown("**历史问答:**")
                for idx, qa in enumerate(answered[-3:], 1):  # 只显示最近3个
                    st.markdown(f"{idx}. {qa.get('question', '')[:30]}... → **{qa.get('answer', '')}**")
    
    st.markdown("<p style='color: #666; font-size: 12px;'>您可以向 AI 咨询 DSM-5 相关的专业问题</p>",
               unsafe_allow_html=True)
    
    # 初始化聊天历史
    if chat_history_key not in st.session_state:
        st.session_state[chat_history_key] = []
    
    # 显示聊天历史
    chat_container = st.container()
    with chat_container:
        for message in st.session_state[chat_history_key]:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "user":
                with st.chat_message("user"):
                    st.markdown(content)
            else:
                with st.chat_message("assistant"):
                    st.markdown(f"<span style='font-size: 14px;'>{content}</span>", unsafe_allow_html=True)
    
    # 聊天输入框
    user_input = st.chat_input("请输入您的问题...", key="chat_input")
    
    if user_input:
        # 添加用户消息到历史
        st.session_state[chat_history_key].append({
            "role": "user",
            "content": user_input
        })
        
        # 显示用户消息
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
        
        # 构建带有上下文的用户消息
        enhanced_message = enhance_message_with_context(user_input, context)
        
        # 获取 AI 回复
        with st.spinner("AI 正在思考..."):
            response = ai_assistant.send_message(enhanced_message)
        
        # 添加 AI 回复到历史
        st.session_state[chat_history_key].append({
            "role": "assistant",
            "content": response
        })
        
        # 显示 AI 回复
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(response)
        
        # 刷新页面以更新聊天界面
        st.rerun()
    
    # 清空对话按钮
    if st.session_state[chat_history_key]:
        if st.button("🗑️ 清空对话", key="clear_chat"):
            st.session_state[chat_history_key] = []
            ai_assistant.clear_history()
            st.rerun()


def enhance_message_with_context(user_message: str, context: dict = None) -> str:
    """
    将用户消息与访谈上下文结合，发送给 AI
    
    参数:
        user_message: 用户原始消息
        context: 访谈上下文信息
    
    返回:
        增强后的消息文本
    """
    if not context:
        return user_message
    
    # 构建上下文提示
    context_parts = []
    
    # 添加访谈主题
    if context.get("tree_name"):
        context_parts.append(f"【当前访谈主题】{context['tree_name']}")
    
    # 添加当前问题
    if context.get("current_question"):
        context_parts.append(f"【当前问题】{context['current_question']}")
    
    # 添加历史问答
    answered = context.get("answered_questions", [])
    if answered:
        history_text = "【已完成的问答】\n"
        for qa in answered:
            history_text += f"- 问题: {qa.get('question', '')}\n"
            history_text += f"  回答: {qa.get('answer', '')}\n"
        context_parts.append(history_text)
    
    # 添加用户笔记
    notes = context.get("notes", "")
    if notes:
        context_parts.append(notes)
    
    # 组合完整消息
    if context_parts:
        full_message = f"{user_message}\n\n{'-'*40}\n当前访谈上下文信息:\n" + "\n".join(context_parts)
        return full_message
    
    return user_message


def render_sidebar_header():
    """
    渲染侧边栏头部信息
    """
    st.sidebar.markdown("# 🧠 DSM-5 访谈辅助工具")
    st.sidebar.markdown("<p style='color: #666;'>面向受训咨询师的专业诊断辅助工具</p>",
                       unsafe_allow_html=True)
    st.sidebar.markdown("---")


def render_tree_selector(available_trees: List[str], tree_names_map: Dict[str, str], on_change: Callable):
    """
    渲染决策树选择器，显示文件名和访谈树名称
    
    参数:
        available_trees: 可用的决策树文件名列表
        tree_names_map: 文件名到访谈树名称的映射字典
        on_change: 选择改变时的回调函数
    """
    st.sidebar.markdown("### 📂 选择访谈主题")
    
    if not available_trees:
        st.sidebar.warning("未找到决策树文件，请检查 data 目录")
        return None
    
    # 构建显示选项：文件名 + 访谈树名称
    display_options = []
    for tree_file in available_trees:
        tree_name = tree_names_map.get(tree_file, tree_file)
        display_text = f"{tree_file} | {tree_name}"
        display_options.append((tree_file, display_text))
    
    # 使用文件名作为实际值，显示文本作为标签
    selected_display = st.sidebar.selectbox(
        "选择诊断决策树",
        options=[opt[1] for opt in display_options],
        key="tree_selector_display"
    )
    
    # 根据显示文本找到对应的文件名
    selected_tree = None
    for tree_file, display_text in display_options:
        if display_text == selected_display:
            selected_tree = tree_file
            break
    
    # 保存到 session_state 供其他地方使用
    if selected_tree:
        st.session_state["tree_selector"] = selected_tree
    
    return selected_tree
        
