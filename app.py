# app.py
"""
DSM-5 结构化访谈辅助工具 - 主应用入口
面向受训咨询师的专业诊断辅助工具

核心逻辑：
1. 设置页面配置
2. 初始化状态
3. 渲染侧边栏（选择决策树）
4. 根据当前状态渲染主界面（左侧问题卡片 | 右侧AI辅助）或最终报告
"""

import streamlit as st
import os
import sys

# 确保模块路径正确
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入功能模块
from modules.tree_loader import (
    get_available_trees,
    get_tree_by_name,
    get_tree_display_name
)
from modules.interview_engine import (
    init_session_state,
    get_current_node,
    process_answer,
    is_interview_complete,
    get_interview_path,
    get_diagnosis_result,
    reset_interview,
    get_start_time,
    can_go_back,
    go_back,
    save_note,
    get_note,
    get_notes_for_ai
)
from modules.ui_components import (
    render_question_card,
    render_warning_alert,
    render_choice_buttons,
    render_diagnosis_result,
    render_progress_indicator,
    render_chat_interface,
    render_sidebar_header,
    render_tree_selector,
    render_note_section
)
from modules.report_generator import (
    generate_clinical_report,
    get_report_filename
)
from modules.ai_assistant import AIAssistant


# =============================================================================
# 页面配置
# =============================================================================
st.set_page_config(
    page_title="DSM-5 结构化访谈辅助工具",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# 初始化状态
# =============================================================================
def initialize_app():
    """
    初始化应用状态
    加载可用的决策树列表，初始化 AI 助手
    """
    # 获取可用的决策树列表
    if "available_trees" not in st.session_state:
        st.session_state.available_trees = get_available_trees()
    
    # 初始化 AI 助手（全局单例）
    if "ai_assistant" not in st.session_state:
        st.session_state.ai_assistant = AIAssistant()


# =============================================================================
# 侧边栏渲染
# =============================================================================
def render_sidebar():
    """
    渲染侧边栏内容
    包含：应用标题、决策树选择器、重置按钮
    """
    # 侧边栏头部
    render_sidebar_header()
    
    # 决策树选择器 - 构建文件名到访谈树名称的映射
    available_trees = st.session_state.get("available_trees", [])
    tree_names_map = {}
    for tree_file in available_trees:
        tree_data = get_tree_by_name(tree_file)
        tree_names_map[tree_file] = get_tree_display_name(tree_data) if tree_data else tree_file
    
    selected_tree = render_tree_selector(available_trees, tree_names_map, lambda: None)
    
    # 重置按钮
    if selected_tree:
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 重新开始访谈", key="reset_interview"):
            tree_data = get_tree_by_name(selected_tree)
            if tree_data:
                reset_interview(selected_tree, tree_data)
                st.rerun()
    
    # 调试模式开关（仅开发使用）
    st.sidebar.markdown("---")
    debug_mode = st.sidebar.checkbox("调试模式", key="debug_mode", value=False)
    if debug_mode:
        st.sidebar.markdown("### 调试信息")
        ai_assistant = st.session_state.get("ai_assistant")
        if ai_assistant:
            config_info = ai_assistant.get_config_info()
            st.sidebar.json(config_info)


# =============================================================================
# 右侧栏渲染 - AI 辅助
# =============================================================================
def render_right_sidebar(tree_data: dict, tree_name: str, current_question: str = ""):
    """
    渲染右侧栏的 AI 辅助界面
    
    参数:
        tree_data: 决策树数据
        tree_name: 决策树名称
        current_question: 当前问题文本（用于上下文）
    """
    ai_assistant = st.session_state.get("ai_assistant")
    if not ai_assistant:
        return
    
    # 构建上下文信息
    context = build_interview_context(tree_data, tree_name, current_question)
    
    # 渲染 AI 聊天界面
    render_chat_interface(
        ai_assistant, 
        chat_history_key="chat_messages",
        context=context
    )


def build_interview_context(tree_data: dict, tree_name: str, current_question: str) -> dict:
    """
    构建访谈上下文信息，供 AI 参考
    
    参数:
        tree_data: 决策树数据
        tree_name: 决策树名称
        current_question: 当前问题文本
    
    返回:
        包含上下文字典
    """
    tree_display_name = get_tree_display_name(tree_data)
    interview_path = get_interview_path()
    
    # 构建已回答的问题历史
    answered_questions = []
    for entry in interview_path:
        answered_questions.append({
            "question": entry.get("question", ""),
            "answer": entry.get("choice", "")
        })
    
    # 获取用户笔记
    notes = get_notes_for_ai()
    
    return {
        "tree_name": tree_display_name,
        "current_question": current_question,
        "answered_questions": answered_questions,
        "total_steps": len(interview_path),
        "notes": notes
    }


# =============================================================================
# 主界面渲染 - 访谈进行中（左右分栏布局）
# =============================================================================
def render_interview_interface(tree_data: dict, tree_name: str):
    """
    渲染访谈进行中的界面
    使用左右分栏布局：左侧问题卡片 | 右侧 AI 辅助
    
    参数:
        tree_data: 决策树数据
        tree_name: 决策树名称
    """
    # 获取当前节点
    current_node = get_current_node(tree_data)
    
    if not current_node:
        st.error("无法获取当前节点数据，请尝试重新开始访谈。")
        return
    
    # 获取当前节点信息
    question = current_node.get("问题", "")
    warning = current_node.get("警告提示")
    node_id = st.session_state.get("current_node_id", "")
    
    # 创建左右两栏布局
    left_col, right_col = st.columns([2, 1])
    
    # ==================== 左侧栏：问题和选择 ====================
    with left_col:
        # 渲染进度指示器
        render_progress_indicator()
        
        # 渲染问题卡片
        render_question_card(question, node_id)
        
        # 渲染警告提示（如果有）
        render_warning_alert(warning)
        
        # 渲染选择按钮（带回退功能）
        def on_yes():
            process_answer(tree_data, "是")
        
        def on_no():
            process_answer(tree_data, "否")
        
        def on_back():
            go_back(tree_data)
        
        render_choice_buttons(
            on_yes, 
            on_no, 
            on_back=on_back,
            can_go_back=can_go_back()
        )
        
        # 渲染笔记区域
        current_note = get_note()
        def on_save_note(content):
            save_note(content)
        
        render_note_section(current_note, on_save_note)
        
        # 显示访谈路径（展开/收起）
        with st.expander("查看访谈路径"):
            path = get_interview_path()
            if path:
                for idx, entry in enumerate(path, 1):
                    st.markdown(f"**步骤 {idx}:** {entry.get('question', '')[:50]}... → **{entry.get('choice', '')}**")
            else:
                st.info("暂无访谈记录")
    
    # ==================== 右侧栏：AI 辅助 ====================
    with right_col:
        st.markdown("---")
        render_right_sidebar(tree_data, tree_name, question)


# =============================================================================
# 主界面渲染 - 访谈完成
# =============================================================================
def render_result_interface(tree_data: dict, tree_name: str):
    """
    渲染访谈完成后的结果界面
    显示诊断结果、报告摘要、下载按钮
    
    参数:
        tree_data: 决策树数据
        tree_name: 决策树名称
    """
    # 获取诊断结果
    diagnosis_result = get_diagnosis_result()
    
    if not diagnosis_result:
        st.error("无法获取诊断结果")
        return
    
    diagnosis = diagnosis_result.get("诊断结果", "")
    summary = diagnosis_result.get("报告摘要", "")
    
    # 生成完整报告
    tree_display_name = get_tree_display_name(tree_data)
    interview_path = get_interview_path()
    start_time = get_start_time()
    
    report_text = generate_clinical_report(
        tree_name=tree_name,
        tree_display_name=tree_display_name,
        interview_path=interview_path,
        diagnosis_result=diagnosis_result,
        start_time=start_time
    )
    
    # 渲染诊断结果
    render_diagnosis_result(diagnosis, summary, report_text)
    
    # 添加回退按钮（即使完成了也可以回退）
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        if can_go_back():
            if st.button("⬅️ 回退修改", key="back_from_result", help="返回上一题修改答案"):
                go_back(tree_data)
                st.rerun()
    with col2:
        st.info("如需修改之前的答案，请点击「回退修改」按钮")
    
    # 显示完整的访谈路径
    with st.expander("查看完整访谈路径", expanded=True):
        st.markdown("### 📋 访谈问答记录")
        for idx, entry in enumerate(interview_path, 1):
            st.markdown(f"**{idx}.** {entry.get('question', '')}")
            st.markdown(f"   → 回答：**{entry.get('choice', '')}**")
            st.markdown("")


# =============================================================================
# 主应用入口
# =============================================================================
def main():
    """
    主应用函数
    核心逻辑：设置页面配置 -> 初始化状态 -> 渲染侧边栏 -> 渲染主界面
    """
    # 初始化应用
    initialize_app()
    
    # 渲染侧边栏
    render_sidebar()
    
    # 主界面内容
    st.markdown("# 🧠 DSM-5 结构化访谈辅助工具")
    
    # 获取当前选中的决策树
    available_trees = st.session_state.get("available_trees", [])
    
    if not available_trees:
        st.warning("⚠️ 未找到决策树文件")
        st.info("请将 JSON 格式的决策树文件放入 `data/` 目录后刷新页面。")
        return
    
    # 获取当前选中的决策树名称
    selected_tree = st.session_state.get("tree_selector")
    
    if not selected_tree:
        st.info("👈 请从侧边栏选择一个访谈主题开始")
        return
    
    # 加载决策树数据
    tree_data = get_tree_by_name(selected_tree)
    
    if not tree_data:
        st.error(f"无法加载决策树: {selected_tree}")
        return
    
    # 显示当前决策树名称
    tree_display_name = get_tree_display_name(tree_data)
    st.markdown(f"### 📂 当前主题: {tree_display_name}")
    st.markdown("---")
    
    # 初始化访谈状态
    init_session_state(selected_tree, tree_data)
    
    # 根据访谈状态渲染不同界面
    if is_interview_complete():
        # 访谈已完成，显示结果
        render_result_interface(tree_data, selected_tree)
    else:
        # 访谈进行中，显示问题
        render_interview_interface(tree_data, selected_tree)


# =============================================================================
# 应用入口
# =============================================================================
if __name__ == "__main__":
    main()
