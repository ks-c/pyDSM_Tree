# modules/tree_loader.py
"""
决策树加载模块
负责扫描、读取和缓存 JSON 决策树文件
使用 @st.cache_data 装饰器缓存数据以避免重复 I/O 操作
"""

import json
import os
from typing import Dict, List, Optional
import streamlit as st


# 默认数据目录路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


@st.cache_data(ttl=3600, show_spinner=False)
def load_tree_files(data_dir: str = DATA_DIR) -> Dict[str, dict]:
    """
    加载指定目录下的所有 JSON 决策树文件
    使用 Streamlit 的 cache_data 装饰器缓存结果，避免重复读取文件
    
    参数:
        data_dir: JSON 文件所在目录路径，默认为项目根目录下的 data 文件夹
    
    返回:
        字典，键为文件名，值为解析后的 JSON 数据
    """
    trees = {}
    
    # 检查目录是否存在
    if not os.path.exists(data_dir):
        st.warning(f"数据目录不存在: {data_dir}")
        return trees
    
    # 遍历目录中的所有 JSON 文件
    for filename in os.listdir(data_dir):
        if filename.endswith('.json') or filename.endswith('.JSON'):
            file_path = os.path.join(data_dir, filename)
            try:
                # 使用 UTF-8 编码读取文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree_data = json.load(f)
                    # 使用文件名（不含扩展名）作为键
                    tree_name = os.path.splitext(filename)[0]
                    trees[tree_name] = tree_data
            except json.JSONDecodeError as e:
                st.error(f"JSON 解析错误 ({filename}): {e}")
            except Exception as e:
                st.error(f"读取文件失败 ({filename}): {e}")
    
    return trees


def get_available_trees(data_dir: str = DATA_DIR) -> List[str]:
    """
    获取所有可用的决策树名称列表
    
    参数:
        data_dir: JSON 文件所在目录路径
    
    返回:
        决策树名称列表（按字母顺序排序）
    """
    trees = load_tree_files(data_dir)
    return sorted(trees.keys())


def get_tree_by_name(tree_name: str, data_dir: str = DATA_DIR) -> Optional[dict]:
    """
    根据名称获取特定的决策树数据
    
    参数:
        tree_name: 决策树名称（不含 .json 扩展名）
        data_dir: JSON 文件所在目录路径
    
    返回:
        决策树数据字典，如果不存在则返回 None
    """
    trees = load_tree_files(data_dir)
    return trees.get(tree_name)


def get_tree_display_name(tree_data: dict) -> str:
    """
    获取决策树的显示名称
    优先使用 JSON 中的"访谈树名称"字段，如果不存在则返回默认名称
    
    参数:
        tree_data: 决策树数据字典
    
    返回:
        决策树的显示名称
    """
    if tree_data and "访谈树名称" in tree_data:
        return tree_data["访谈树名称"]
    return "未命名决策树"


def get_starting_node(tree_data: dict) -> str:
    """
    获取决策树的起始节点 ID
    
    参数:
        tree_data: 决策树数据字典
    
    返回:
        起始节点 ID，默认为 "节点_1"
    """
    if tree_data and "起始节点" in tree_data:
        return tree_data["起始节点"]
    return "节点_1"


def get_node_by_id(tree_data: dict, node_id: str) -> Optional[dict]:
    """
    根据节点 ID 获取节点数据
    
    参数:
        tree_data: 决策树数据字典
        node_id: 节点 ID
    
    返回:
        节点数据字典，如果不存在则返回 None
    """
    if not tree_data or "节点列表" not in tree_data:
        return None
    return tree_data["节点列表"].get(node_id)


def clear_tree_cache():
    """
    清除决策树数据缓存
    当 JSON 文件更新后调用此函数刷新缓存
    """
    load_tree_files.clear()
    st.success("缓存已清除，将重新加载决策树数据")
