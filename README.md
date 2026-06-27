# 🤖 Multi-Agent Data Analysis Platform

<div align="center">

**基于 Strands Agents 的多智能体数据分析与知识库问答平台**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [使用指南](#-使用指南) • [系统架构](#-系统架构)

</div>

---

## 📋 项目简介

一个**双模式**的多 Agent 协作平台，面向政府文职人员等非技术用户设计。

- **模式 A — 文件分析**：上传 Excel/Word/PDF → 选择分析模板 → 自动生成交互式 HTML 报告
- **模式 B — 知识库问答**：直接打字提问，从预置知识库中检索答案（带引用来源）

底层由 **5 个 AI Agent** 协作完成任务，用户无需理解 Agent 概念。

---

## ✨ 功能特性

### 📊 文件分析

| 分析模板 | 适用文件 | 分析内容 |
|---------|---------|---------|
| 📊 数据统计分析 | Excel, CSV | 统计摘要、趋势、异常检测、排名 |
| 📝 文档要点提取 | Word, PDF | 结构提取、关键词、分类整理 |
| 📋 对比分析 | Excel, CSV (2-5个) | 横向差异对比、趋势对比 |
| 💰 财务审计分析 | Excel, CSV | 支出趋势、异常科目、排名 |
| 🎯 绩效评估分析 | Excel, CSV | 目标 vs 实际、达标分析 |
| 📑 综合报告 | 全部类型 (1-5个) | 全部分析方法综合 |

### 🧠 知识库问答

- 语义检索：不是关键词匹配，而是理解问题含义后检索
- 引用溯源：每条答案标注来自哪份文档
- 预置知识库：政策法规、财务制度、使用手册
- 可扩展：开发人员放文档 → 一条命令索引 → 即刻生效

### 📈 报告能力

- Chart.js 交互式图表（折线图、柱状图、雷达图、饼图）
- 响应式 HTML 设计，支持桌面端和移动端
- 摘要卡片、异常表格、趋势图表、建议措施
- 在线查看，可下载

### 🔄 反馈机制

对报告不满意？点击反馈，描述缺了什么 → 系统自动追加分析 → 生成新报告。无需从头重跑。

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- DeepSeek API Key（或其他 OpenAI 兼容 API）

### 安装

```bash
# 1. 克隆项目
git clone <repo-url>
cd mutli-agents

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY=sk-xxx

# 4. （可选）配置知识库
# 将知识文档放入 knowledge_docs/
# 编辑 scripts/index_knowledge.py 配置映射
python scripts/index_knowledge.py

# 5. 启动
python run.py
# 服务启动在 http://localhost:8000
```

### 验证

```bash
# 查看可用模板
curl http://localhost:8000/api/templates

# 查看知识库
curl http://localhost:8000/api/knowledge/collections
```

---

## 💡 使用指南

### 文件分析

```
1. 上传文件 → POST /api/upload
2. 发起分析 → POST /api/analysis/run
   {
     "file_ids": ["上传返回的file_id"],
     "template_id": "financial_audit",
     // 或者用自然语言：
     "nl_query": "帮我找出异常支出和趋势"
   }
3. 查询进度 → GET /api/tasks/{task_id}
4. 查看报告 → GET /api/reports/{task_id}
5. 不满意？ → POST /api/feedback/{task_id}
   {
     "satisfaction": "partial",
     "missing_items": ["结构占比分析"],
     "description": "缺少各科目支出占比的饼图"
   }
```

### 知识库问答

```
POST /api/knowledge/ask
{
  "question": "差旅费报销标准是多少？",
  "collection": ""  // 留空=检索全部知识库
}

返回:
{
  "question": "差旅费报销标准是多少？",
  "answer": "**回答**: 普通人员每人每天不超过350元...\n**依据**: > ...\n**来源**: finance / finance_policies.txt"
}
```

---

## 🏗️ 系统架构

```
用户
 │
 ├── 文件分析 ──→ Coordinator Agent ──→ Fetcher → Analyzer → Visualizer
 │                                     （协调调度）
 │
 └── 知识问答 ──→ Knowledge Agent ──→ ChromaDB 语义检索
                  （独立响应）

数据层: SQLite（元数据） + 本地文件系统（文件/报告） + ChromaDB（向量知识库）
```

### 5 个 Agent 职责

| Agent | 角色比喻 | 职责 |
|-------|---------|------|
| **Coordinator** | 项目经理 | 理解需求 → 拆解任务 → 调度子 Agent → 汇总交付 |
| **Fetcher** | 文件管理员 | 解析 Excel/CSV/Word/PDF，提取结构化数据，识别列类型 |
| **Analyzer** | 数据分析师 | 统计摘要、异常检测、趋势、排名、相关性、文本摘要、对比、分类 |
| **Visualizer** | 报告设计师 | Chart.js 图表渲染、HTML 报告生成、模板填充、质量自检 |
| **Knowledge** | 图书管理员 | 语义检索 ChromaDB、整理答案、引用来源 |

### Agent 协调流程

```
Coordinator 收到 "财务审计分析" 模板
  │
  ├─[1] 调用 Fetcher: 解析 xlsx → 提取表格 → 识别列类型
  │    返回: 数值列=[金额], 日期列=[日期], 分类列=[科目]
  │
  ├─[2] 调用 Analyzer: 执行 [趋势分析, 异常检测, 排名]
  │    返回: 趋势上升, 3个异常点, Top5排名
  │
  ├─[3] 调用 Visualizer: 渲染图表 → 填充模板 → 写入 HTML → 自检
  │    返回: 报告已写入 reports/xxx/report.html
  │
  └─[4] 交付: 创建 Report 记录，标记任务完成
```

---

## 📂 项目结构

```
mutli-agents/
├── main.py                          # FastAPI 入口
├── run.py                           # 启动脚本
├── config.yml                       # 应用配置
├── .env.example                     # 环境变量模板
├── requirements.txt                 # 依赖清单
│
├── app/
│   ├── agents/                      # Agent 定义 (5个)
│   │   ├── coordinator_agent.py     #   协调者
│   │   ├── fetcher_agent.py         #   数据获取
│   │   ├── analyzer_agent.py        #   数据分析
│   │   ├── visualizer_agent.py      #   可视化
│   │   └── knowledge_agent.py       #   知识问答
│   │
│   ├── tools/                       # 工具函数 (29个 @tool)
│   │   ├── file_tools.py            #   文件解析 (5)
│   │   ├── analysis_tools.py        #   数据分析 (8)
│   │   ├── viz_tools.py             #   可视化 (7)
│   │   ├── storage_tools.py         #   文件存储 (5)
│   │   ├── email_tools.py           #   邮件发送 (1)
│   │   └── knowledge_tools.py       #   知识检索 (3)
│   │
│   ├── prompt/                      # System Prompt (5个)
│   ├── models/                      # LLM + SQLite + ChromaDB
│   ├── api/                         # API 端点 (10个)
│   └── config/                      # 配置 + 模板加载器
│
├── templates/                       # 分析模板 (6个 YAML)
├── report_templates/                # 报告 HTML 模板 (2个)
├── knowledge_docs/                  # 知识库源文档
├── scripts/                         # 工具脚本
└── examples/                        # 示例数据
```

---

## 🛠️ 技术栈

- **Agent 框架**: Strands Agents
- **Web 框架**: FastAPI + Uvicorn
- **LLM**: OpenAI 兼容接口（DeepSeek）
- **数据库**: SQLite（元数据）+ ChromaDB（向量知识库）
- **向量化**: ONNX all-MiniLM-L6-v2
- **数据处理**: Pandas, NumPy, scikit-learn
- **文件解析**: openpyxl, python-docx, pypdf
- **报告引擎**: Jinja2 + Chart.js
- **配置管理**: Pydantic + PyYAML

---

## 🔧 定制指南

### 调整 Agent 行为
编辑 `app/prompt/*.py` 中的 System Prompt，改完重启生效。

### 新增分析模板
在 `templates/` 下新建 YAML 文件，重启生效。

### 添加知识库文档
1. 将 .txt/.md 放入 `knowledge_docs/`
2. 编辑 `scripts/index_knowledge.py` 的 `DOCS_MAP`
3. 运行 `python scripts/index_knowledge.py`

### 调整分块参数
编辑 `app/models/knowledge_base.py` 中 `index_document_file()` 的 `chunk_size` 参数。

---

## 📄 许可证

MIT License
