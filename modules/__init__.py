# modules/__init__.py
"""
DSM-5 结构化访谈辅助工具 - 功能模块包
包含：决策树加载、访谈引擎、UI组件、报告生成、AI辅助等模块
"""

from .tree_loader import load_tree_files, get_tree_by_name, get_available_trees
from .interview_engine import (
    init_session_state,
    get_current_node,
    process_answer,
    is_interview_complete,
    get_interview_path,
    reset_interview,
    get_diagnosis_result
)
from .ui_components import (
    render_question_card,
    render_warning_alert,
    render_diagnosis_result,
    render_chat_interface
)
from .report_generator import generate_clinical_report, create_download_link
from .ai_assistant import AIAssistant

__all__ = [
    # tree_loader
    'load_tree_files',
    'get_tree_by_name',
    'get_available_trees',
    # interview_engine
    'init_session_state',
    'get_current_node',
    'process_answer',
    'is_interview_complete',
    'get_interview_path',
    'reset_interview',
    'get_diagnosis_result',
    # ui_components
    'render_question_card',
    'render_warning_alert',
    'render_diagnosis_result',
    'render_chat_interface',
    # report_generator
    'generate_clinical_report',
    'create_download_link',
    # ai_assistant
    'AIAssistant',
]
