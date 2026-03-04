# DSM-5 结构化访谈辅助工具

面向受训咨询师的专业诊断辅助工具，基于决策树算法实现动态问题生成，集成 AI 辅助功能。

## 功能特性

- **动态访谈流程** - 根据用户回答自动导航决策树
- **诊断预警** - 关键节点实时显示警告提示
- **AI 辅助** - 右侧栏集成智能问答，支持上下文感知
- **报告生成** - 自动输出结构化临床报告
- **多主题支持** - 支持加载多个 JSON 决策树文件

## 项目结构

```
DSM-TREE/
├── app.py                 # 主应用入口
├── start.bat              # 一键启动脚本
├── requirements.txt       # 依赖文件
├── README.md              # 本文件
├── .streamlit/
│   └── secrets.toml       # API 配置文件
├── modules/               # 功能模块
│   ├── tree_loader.py     # 决策树加载（带缓存）
│   ├── interview_engine.py # 访谈引擎（状态管理）
│   ├── ui_components.py   # UI 组件
│   ├── ai_assistant.py    # AI 助手
│   └── report_generator.py # 报告生成
├── data/                  # 决策树数据
│   ├── 2_1.json
│   ├── 2_2.json
│   └── ...
└── utils/                 # 工具函数
    └── helpers.py
```

## 快速开始

### 1. 配置 API

编辑 `.streamlit/secrets.toml`：

```toml
[api]
api_key = "your-api-key-here"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
model_name = "qwen-plus"
```

支持：阿里百炼 DashScope、OpenAI、其他兼容 API。

### 2. 启动应用

双击运行 `start.bat`，或在命令行执行：

```bash
streamlit run app.py
```

### 3. 使用流程

1. 从左侧栏选择访谈主题
2. 在主界面回答问题（是/否）
3. 右侧 AI 栏可随时咨询相关问题
4. 完成所有问题后查看诊断报告

## 决策树格式

JSON 文件结构示例：

```json
{
  "name": "决策树名称",
  "tree": {
    "start": {
      "问题": "问题文本",
      "是否终点": false,
      "警告提示": "提示信息（可选）",
      "选项": {
        "是": "next_node_id_yes",
        "否": "next_node_id_no"
      }
    },
    "end_node": {
      "问题": "最终问题",
      "是否终点": true,
      "诊断结果": "诊断名称",
      "报告摘要": "摘要内容"
    }
  }
}
```

## 依赖要求

- Python 3.8+
- streamlit >= 1.28.0
- openai >= 1.0.0

## 注意事项

- `secrets.toml` 包含敏感信息，请勿提交到版本控制
- 决策树 JSON 文件需使用 UTF-8 编码
- 首次启动需要联网安装依赖
