# modules/interview_engine.py
"""
访谈引擎模块
负责管理访谈状态、处理用户选择、追踪访谈路径
使用 Streamlit 的 session_state 维护访谈进度
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import streamlit as st
from .tree_loader import get_node_by_id, get_starting_node


# Session State 键名常量
KEY_CURRENT_TREE = "current_tree"
KEY_CURRENT_NODE_ID = "current_node_id"
KEY_INTERVIEW_PATH = "interview_path"
KEY_INTERVIEW_COMPLETED = "interview_completed"
KEY_DIAGNOSIS_RESULT = "diagnosis_result"
KEY_START_TIME = "interview_start_time"


def init_session_state(tree_name: str, tree_data: dict):
    """
    初始化访谈相关的 session_state 变量
    在开始新的访谈或切换决策树时调用
    
    参数:
        tree_name: 当前决策树名称
        tree_data: 决策树数据字典
    """
    # 如果切换了决策树，重置所有状态
    if st.session_state.get(KEY_CURRENT_TREE) != tree_name:
        st.session_state[KEY_CURRENT_TREE] = tree_name
        st.session_state[KEY_CURRENT_NODE_ID] = get_starting_node(tree_data)
        st.session_state[KEY_INTERVIEW_PATH] = []
        st.session_state[KEY_INTERVIEW_COMPLETED] = False
        st.session_state[KEY_DIAGNOSIS_RESULT] = None
        st.session_state[KEY_START_TIME] = datetime.now()


def get_current_node(tree_data: dict) -> Optional[dict]:
    """
    获取当前节点的数据
    
    参数:
        tree_data: 决策树数据字典
    
    返回:
        当前节点数据字典，如果未初始化则返回 None
    """
    current_node_id = st.session_state.get(KEY_CURRENT_NODE_ID)
    if not current_node_id:
        return None
    return get_node_by_id(tree_data, current_node_id)


def process_answer(tree_data: dict, choice_label: str) -> bool:
    """
    处理用户的选择（是/否），更新访谈状态
    
    参数:
        tree_data: 决策树数据字典
        choice_label: 用户选择的标签（"是"或"否"）
    
    返回:
        是否成功处理了选择
    """
    current_node = get_current_node(tree_data)
    if not current_node:
        return False
    
    # 获取当前节点的问题文本
    question = current_node.get("问题", "")
    
    # 在选项中查找匹配的目标节点
    options = current_node.get("选项", [])
    target_node_id = None
    
    for option in options:
        if option.get("标签") == choice_label:
            target_node_id = option.get("目标")
            break
    
    if not target_node_id:
        st.error(f"未找到选项 '{choice_label}' 对应的目标节点")
        return False
    
    # 记录到访谈路径
    path_entry = {
        "question": question,
        "choice": choice_label,
        "from_node": st.session_state.get(KEY_CURRENT_NODE_ID),
        "to_node": target_node_id
    }
    st.session_state[KEY_INTERVIEW_PATH].append(path_entry)
    
    # 更新当前节点
    st.session_state[KEY_CURRENT_NODE_ID] = target_node_id
    
    # 检查是否到达终点
    target_node = get_node_by_id(tree_data, target_node_id)
    if target_node and target_node.get("是否终点", False):
        st.session_state[KEY_INTERVIEW_COMPLETED] = True
        st.session_state[KEY_DIAGNOSIS_RESULT] = {
            "诊断结果": target_node.get("诊断结果", ""),
            "报告摘要": target_node.get("报告摘要", "")
        }
    
    return True


def is_interview_complete() -> bool:
    """
    检查访谈是否已完成（到达终点节点）
    
    返回:
        True 如果访谈已完成，否则 False
    """
    return st.session_state.get(KEY_INTERVIEW_COMPLETED, False)


def get_interview_path() -> List[Dict]:
    """
    获取完整的访谈路径历史
    
    返回:
        访谈路径列表，每个元素包含问题、选择、节点跳转信息
    """
    return st.session_state.get(KEY_INTERVIEW_PATH, [])


def get_diagnosis_result() -> Optional[Dict]:
    """
    获取诊断结果（仅在访谈完成后有效）
    
    返回:
        包含诊断结果和报告摘要的字典，如果未完成则返回 None
    """
    return st.session_state.get(KEY_DIAGNOSIS_RESULT)


def reset_interview(tree_name: str, tree_data: dict):
    """
    重置当前访谈，从头开始
    
    参数:
        tree_name: 当前决策树名称
        tree_data: 决策树数据字典
    """
    # 清除当前树的状态，强制重新初始化
    st.session_state[KEY_CURRENT_TREE] = None
    init_session_state(tree_name, tree_data)


def get_interview_progress() -> Tuple[int, int]:
    """
    获取访谈进度信息
    
    返回:
        (当前步数, 总步数估计) 的元组
    """
    path = get_interview_path()
    current_step = len(path)
    # 由于不知道总步数，返回当前步数和 -1 表示未知
    return current_step, -1


def get_start_time() -> Optional[datetime]:
    """
    获取访谈开始时间
    
    返回:
        访谈开始时间，如果未开始则返回 None
    """
    return st.session_state.get(KEY_START_TIME)


def can_go_back() -> bool:
    """
    检查是否可以回退到上一个问题
    
    返回:
        True 如果有历史记录可以回退
    """
    path = get_interview_path()
    return len(path) > 0


def go_back(tree_data: dict) -> bool:
    """
    回退到上一个问题
    
    参数:
        tree_data: 决策树数据字典
    
    返回:
        True 如果成功回退
    """
    path = get_interview_path()
    if not path:
        return False
    
    # 移除最后一步
    last_entry = path.pop()
    
    # 恢复到上一个节点
    previous_node_id = last_entry.get("from_node")
    if previous_node_id:
        st.session_state[KEY_CURRENT_NODE_ID] = previous_node_id
        
        # 清除完成状态（如果之前已完成）
        if st.session_state.get(KEY_INTERVIEW_COMPLETED):
            st.session_state[KEY_INTERVIEW_COMPLETED] = False
            st.session_state[KEY_DIAGNOSIS_RESULT] = None
        
        return True
    
    return False


def save_note(note_content: str):
    """
    保存当前步骤的笔记
    
    参数:
        note_content: 笔记内容
    """
    if "interview_notes" not in st.session_state:
        st.session_state["interview_notes"] = {}
    
    current_node_id = st.session_state.get(KEY_CURRENT_NODE_ID, "")
    if current_node_id:
        st.session_state["interview_notes"][current_node_id] = {
            "content": note_content,
            "timestamp": datetime.now()
        }


def get_note(node_id: str = None) -> str:
    """
    获取指定节点的笔记内容
    
    参数:
        node_id: 节点 ID，默认为当前节点
    
    返回:
        笔记内容，如果没有则返回空字符串
    """
    if node_id is None:
        node_id = st.session_state.get(KEY_CURRENT_NODE_ID, "")
    
    notes = st.session_state.get("interview_notes", {})
    note_data = notes.get(node_id, {})
    return note_data.get("content", "")


def get_all_notes() -> Dict[str, Dict]:
    """
    获取所有笔记
    
    返回:
        所有笔记的字典，键为节点 ID
    """
    return st.session_state.get("interview_notes", {})


def get_notes_for_ai() -> str:
    """
    获取格式化的笔记内容，用于发送给 AI
    
    返回:
        格式化的笔记文本
    """
    notes = get_all_notes()
    if not notes:
        return ""
    
    result = "【用户笔记记录】\n"
    for node_id, note_data in notes.items():
        content = note_data.get("content", "").strip()
        if content:
            result += f"- {content}\n"
    
    return result
