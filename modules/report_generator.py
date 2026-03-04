# modules/report_generator.py
"""
报告生成模块
负责生成临床访谈报告、格式化报告文本、创建下载链接
"""

import base64
from datetime import datetime
from typing import List, Dict
import streamlit as st


def generate_clinical_report(
    tree_name: str,
    tree_display_name: str,
    interview_path: List[Dict],
    diagnosis_result: Dict,
    start_time: datetime
) -> str:
    """
    生成完整的临床访谈报告
    
    参数:
        tree_name: 决策树文件名
        tree_display_name: 决策树显示名称
        interview_path: 访谈路径历史
        diagnosis_result: 诊断结果字典
        start_time: 访谈开始时间
    
    返回:
        格式化的报告文本
    """
    end_time = datetime.now()
    duration = end_time - start_time if start_time else "未知"
    
    # 构建报告文本
    report_lines = []
    
    # 报告头部
    report_lines.append("=" * 60)
    report_lines.append("DSM-5 结构化访谈临床记录报告")
    report_lines.append("=" * 60)
    report_lines.append("")
    
    # 基本信息
    report_lines.append("【基本信息】")
    report_lines.append(f"访谈主题: {tree_display_name}")
    report_lines.append(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S') if start_time else '未知'}")
    report_lines.append(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"访谈时长: {duration}")
    report_lines.append(f"问答步数: {len(interview_path)}")
    report_lines.append("")
    
    # 诊断结果
    report_lines.append("=" * 60)
    report_lines.append("【诊断结果】")
    report_lines.append("=" * 60)
    report_lines.append("")
    report_lines.append(f"诊断: {diagnosis_result.get('诊断结果', '未知')}")
    report_lines.append("")
    report_lines.append("【报告摘要】")
    report_lines.append(diagnosis_result.get('报告摘要', '无'))
    report_lines.append("")
    
    # 访谈路径
    report_lines.append("=" * 60)
    report_lines.append("【访谈路径记录】")
    report_lines.append("=" * 60)
    report_lines.append("")
    
    if interview_path:
        for idx, entry in enumerate(interview_path, 1):
            report_lines.append(f"步骤 {idx}:")
            report_lines.append(f"  问题: {entry.get('question', '')}")
            report_lines.append(f"  回答: {entry.get('choice', '')}")
            report_lines.append("")
    else:
        report_lines.append("无访谈路径记录")
        report_lines.append("")
    
    # 报告尾部
    report_lines.append("=" * 60)
    report_lines.append("报告生成时间: " + end_time.strftime('%Y-%m-%d %H:%M:%S'))
    report_lines.append("本报告由 DSM-5 结构化访谈辅助工具自动生成")
    report_lines.append("=" * 60)
    
    return "\n".join(report_lines)


def create_download_link(report_text: str, filename: str) -> str:
    """
    创建用于下载报告的 HTML 链接
    
    参数:
        report_text: 报告文本内容
        filename: 下载文件名
    
    返回:
        HTML 下载链接
    """
    # 将文本编码为 base64
    b64 = base64.b64encode(report_text.encode()).decode()
    
    # 创建下载链接
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}" style="text-decoration: none;">'
    href += f'<button style="padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">📥 下载报告</button></a>'
    
    return href


def format_path_summary(interview_path: List[Dict]) -> str:
    """
    格式化访谈路径为简洁的摘要文本
    
    参数:
        interview_path: 访谈路径历史
    
    返回:
        格式化的路径摘要
    """
    if not interview_path:
        return "无访谈记录"
    
    summary_lines = []
    for idx, entry in enumerate(interview_path, 1):
        question = entry.get('question', '')
        choice = entry.get('choice', '')
        # 截断过长的问题文本
        if len(question) > 50:
            question = question[:50] + "..."
        summary_lines.append(f"{idx}. {question} → {choice}")
    
    return "\n".join(summary_lines)


def get_report_filename(diagnosis: str) -> str:
    """
    生成报告文件名
    
    参数:
        diagnosis: 诊断结果
    
    返回:
        安全的文件名
    """
    from utils.helpers import sanitize_filename
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_diagnosis = sanitize_filename(diagnosis, "_")
    
    if safe_diagnosis:
        return f"诊断报告_{safe_diagnosis}_{timestamp}.txt"
    else:
        return f"诊断报告_{timestamp}.txt"
