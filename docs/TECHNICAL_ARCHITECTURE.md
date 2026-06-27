# 多 Agent 数据分析平台 — 技术架构与实现方案

**版本**: v1.0
**日期**: 2025-06-23

---

## 1. 系统架构

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI 服务层                             │
│                                                                   │
│  POST /api/upload          POST /api/analysis/run               │
│  GET  /api/tasks/{id}      GET  /api/reports/{id}               │
│  GET  /api/templates       GET  /api/history                    │
│  POST /api/feedback/{id}   POST /api/knowledge/ask              │
│  GET  /api/knowledge/collections                                │
└──────────────┬──────────────────────────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌───────────────┐   ┌───────────────────────────────┐
│ Knowledge     │   │ Coordinator Agent              │
│ Agent         │   │ (Agent-as-Tool 编排)           │
│ (独立 Agent)   │   │                                │
│               │   │  tools: [fetcher_agent,        │
│ ChromaDB ←──→ │   │          analyzer_agent,       │
│ 语义检索       │   │          visualizer_agent]     │
└───────────────┘   └───────────┬───────────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
        ┌──────────┐    ┌──────────────┐   ┌──────────────┐
        │ Fetcher  │    │ Analyzer     │   │ Visualizer   │
        │ Agent    │    │ Agent        │   │ Agent        │
        │          │    │              │   │              │
        │ 5 tools  │    │ 8 tools      │   │ 9 tools      │
        └────┬─────┘    └──────┬───────┘   └──────┬───────┘
             │                 │                   │
    ┌────────┴────────┬────────┴────────┬──────────┴────────┐
    ▼                 ▼                 ▼                    ▼
┌────────┐    ┌──────────────┐   ┌──────────┐    ┌────────────────┐
│本地文件 │    │ SQLite        │   │ ChromaDB │    │ DeepSeek API   │
│系统     │    │ (元数据)       │   │ (向量库)  │    │ (LLM 推理)     │
└────────┘    └──────────────┘   └──────────┘    └────────────────┘
```

### 1.2 核心设计模式：Agent-as-Tool

每个子 Agent 被封装为 `@tool` 函数，Coordinator 将子 Agent 视为可调用的"专家工具"。

```python
# coordinator_agent.py — 顶层 Agent
coordinator = Agent(
    system_prompt=coordinator_prompt,
    model=ModelInstances.LEADER_MODEL,
    tools=[fetcher_agent, analyzer_agent, visualizer_agent],
)

# fetcher_agent.py — 作为 Tool 的子 Agent
@tool
def fetcher_agent(query: str) -> str:
    agent = Agent(
        system_prompt=fetcher_prompt,
        model=ModelInstances.LEADER_MODEL,
        tools=[parse_excel, parse_csv, parse_docx, parse_pdf, detect_structure],
    )
    return agent(formatted_query)
```

**设计意图**：
- Coordinator 自主决策调用时机和参数，而非硬编码 pipeline
- 每个子 Agent 有独立的 system prompt 和工具集，职责隔离
- Agent 间通过 Coordinator 传递结构化数据，不直接通信

### 1.3 数据流

```
HTTP Request → FastAPI
  │
  ├─ 文件分析链路:
  │   POST /api/upload → 文件存 local_storage/uploads/
  │                    → Upload 记录写入 SQLite
  │   POST /api/analysis/run → Task 记录 → BackgroundTasks
  │                          → Coordinator.invoke_async()
  │                          → Fetcher 解析文件 → JSON 数据
  │                          → Analyzer 执行分析 → 分析结果
  │                          → Visualizer 生成 HTML → 写入磁盘
  │                          → Report 记录写入 SQLite
  │   GET /api/reports/{id} → 查询 Report → 读取 HTML → 返回
  │
  └─ 知识问答链路:
      POST /api/knowledge/ask → Knowledge.invoke_async()
                              → search_knowledge → ChromaDB.query()
                              → 整理答案 → 返回
```

---

## 2. Agent 详细设计

### 2.1 Coordinator Agent

| 属性 | 值 |
|------|-----|
| 文件 | `app/agents/coordinator_agent.py` |
| 类型 | 模块级 `Agent` 实例（顶层） |
| Prompt | `coordinator_prompt` |
| 工具 | `fetcher_agent`, `analyzer_agent`, `visualizer_agent` |
| 调用方式 | `coordinator.invoke_async(query)` |

**核心推理逻辑**：

```
输入 → 解析模板配置（或 NL） → 确定 methods 列表
     → 构造 Fetcher 调用（文件路径 + 类型）
     → 接收结构化数据 → 匹配列到分析方法
     → 构造 Analyzer 调用（数据 + methods + hints）
     → 接收分析结果 → 构造 Visualizer 调用（结果 + 模板ID + 输出路径）
     → 确认报告写入 → 返回完成
```

### 2.2 Fetcher Agent

| 属性 | 值 |
|------|-----|
| 文件 | `app/agents/fetcher_agent.py` |
| 类型 | `@tool` 函数内嵌 `Agent` |
| Prompt | `fetcher_prompt` |
| 工具 | `parse_excel`, `parse_csv`, `parse_docx`, `parse_pdf`, `detect_structure` |

**输出统一格式**：

```json
{
  "files": [{
    "filename": "6月支出.xlsx",
    "file_type": "xlsx",
    "parsed": {
      "type": "tabular",
      "sheets": [{
        "columns": ["日期", "科目", "金额"],
        "rows": [["2025-06-01", "办公", 12500], ...]
      }]
    },
    "structure": {
      "column_types": {"日期": "date", "科目": "category", "金额": "numeric"}
    }
  }]
}
```

### 2.3 Analyzer Agent

| 属性 | 值 |
|------|-----|
| 文件 | `app/agents/analyzer_agent.py` |
| 类型 | `@tool` 函数内嵌 `Agent` |
| Prompt | `analyzer_prompt` |
| 工具 | `statistical_summary`, `anomaly_detection`, `trend_analysis`, `ranking`, `correlation`, `text_summary`, `comparison`, `classification` |

**分析方法选择逻辑**：

| 方法 | 需要列类型 | 产出 |
|------|-----------|------|
| `statistical_summary` | numeric | 均值/中位数/标准差/四分位数 |
| `anomaly_detection` | numeric | Z-score 异常列表 |
| `trend_analysis` | date + numeric | 趋势方向/变化率/拐点 |
| `ranking` | numeric | Top N + Bottom N |
| `correlation` | numeric × 2 | 皮尔逊相关系数 |
| `text_summary` | 文本数据 | 关键词频率/文本统计 |
| `comparison` | 两数据集 + key | 差异项 |
| `classification` | 文本段落 | 分类分段 |

### 2.4 Visualizer Agent

| 属性 | 值 |
|------|-----|
| 文件 | `app/agents/visualizer_agent.py` |
| 类型 | `@tool` 函数内嵌 `Agent` |
| Prompt | `visualizer_prompt` |
| 工具 | `render_line_chart`, `render_bar_chart`, `render_radar_chart`, `render_table`, `render_summary_card`, `apply_report_template`, `write_local_file_html`, `read_local_file`, `self_review` |

**分析类型到图表的映射**：

| 分析类型 | 图表 | 组件 |
|---------|------|------|
| statistical_summary | — | summary_card + table |
| anomaly_detection | — | table（高亮异常行） |
| trend_analysis | line_chart | — |
| ranking | bar_chart | table |
| correlation | — | summary_card |
| text_summary | — | 文本块 |
| comparison | bar_chart | table |
| classification | — | 列表 |

### 2.5 Knowledge Agent

| 属性 | 值 |
|------|-----|
| 文件 | `app/agents/knowledge_agent.py` |
| 类型 | 模块级 `Agent` 实例（独立） |
| Prompt | `knowledge_prompt` |
| 工具 | `search_knowledge`, `list_collections`, `get_document_content` |
| 调用方式 | `knowledge.invoke_async(query)` |

**与 Coordinator 的关系**：完全独立。Coordinator 的 tools 中**不包含** knowledge_agent。Knowledge Agent 通过独立的 `/api/knowledge/ask` 端点触发。

---

## 3. 工具系统设计

### 3.1 文件解析工具 (`file_tools.py`)

| 工具 | 输入 | 输出 | 依赖 |
|------|------|------|------|
| `parse_excel` | file_path, sheet_name? | 统一格式 JSON | openpyxl |
| `parse_csv` | file_path, delimiter, has_header | 统一格式 JSON | csv (stdlib) |
| `parse_docx` | file_path | 段落+表格 JSON | python-docx |
| `parse_pdf` | file_path | 页面文本 JSON | pypdf |
| `detect_structure` | parsed JSON | 列类型分析 JSON | — |

**所有解析工具输出统一格式**：
```json
{
  "type": "tabular | textual",
  "source": "原文件名",
  "sheets": [...] | "paragraphs": [...] | "pages": [...]
}
```

### 3.2 分析工具 (`analysis_tools.py`)

所有分析工具遵循统一接口：`(data_json: str, ...) -> result_json: str`。

每个结果包含：
- `method`: 分析方法名
- `result`: 结构化分析数据
- `insights`: 自然语言洞察列表

### 3.3 可视化工具 (`viz_tools.py`)

| 工具 | 输出 |
|------|------|
| `render_line_chart` / `render_bar_chart` / `render_radar_chart` | Chart.js 配置 JSON |
| `render_table` / `render_summary_card` | HTML 片段 |
| `apply_report_template` | 模板选择建议 + 使用说明 |
| `self_review` | 审核结果 JSON（pass / needs_fix + 检查项） |

### 3.4 存储工具 (`storage_tools.py`)

从原始 `strands_agents_tool.py` 中提取的通用文件操作函数：

| 函数 | 类型 |
|------|------|
| `process_file_key` | 辅助函数（路径标准化） |
| `ensure_directory_exists` | 辅助函数（目录创建） |
| `write_local_file` | @tool |
| `write_local_file_html` | @tool |
| `get_local_file_metadata` | @tool |
| `read_local_file` | @tool |
| `write_local_file_zip` | @tool |

### 3.5 知识库工具 (`knowledge_tools.py`)

| 工具 | 后端 |
|------|------|
| `search_knowledge` | ChromaDB `collection.query()` |
| `list_collections` | ChromaDB `client.list_collections()` |
| `get_document_content` | ChromaDB `collection.get(ids=[...])` |

---

## 4. 知识库系统

### 4.1 ChromaDB 架构

```
ChromaDB PersistentClient
├── path: local_storage/chromadb/
├── embedding: ONNX all-MiniLM-L6-v2 (384维)
│
├── Collection: policies
│   └── documents: 政府政策法规文本块
│
├── Collection: finance
│   └── documents: 财务制度文本块
│
├── Collection: manual
│   └── documents: 平台使用手册文本块
│
└── Collection: custom (可扩展)
```

### 4.2 文档索引流程

```
knowledge_docs/*.txt
  │
  ▼
index_document_file(collection_name, file_path)
  │
  ├─ 读取文件内容
  ├─ 按段落分块（chunk_size=500，段落合并策略）
  ├─ 生成 metadata（source, chunk_index, file_path）
  │
  ▼
add_documents(collection_name, chunks, metadatas)
  │
  ├─ get_or_create_collection() → ChromaDB Collection
  ├─ col.add(documents, metadatas, ids)
  │   └─ ONNX Embedding → 向量 → 存储
  │
  ▼
立即可检索
```

### 4.3 Embedding 方案

**当前**：ChromaDB 默认 ONNX 模型 `all-MiniLM-L6-v2`（384维）
- 优点：本地运行，无需 API 调用
- 模型大小：~80MB（首次自动缓存到 `~/.cache/chroma/`）
- 中文支持：通过多语言训练数据覆盖

**升级路径**：
```python
# 方案 1: SentenceTransformer 中文模型
_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="shibing624/text2vec-base-chinese"
)

# 方案 2: OpenAI 兼容 API
_embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
    api_key="sk-xxx",
    api_base="https://api.openai.com/v1",
    model_name="text-embedding-3-small",
)
```

**切换后需重建索引**：
```bash
rm -rf local_storage/chromadb
python scripts/index_knowledge.py
```

### 4.4 分块策略

```python
def index_document_file(collection_name, file_path, chunk_size=500):
    # 1. 读取全文
    # 2. 按 \n\n 拆分为段落
    # 3. 段落合并：当前块 < chunk_size 时继续追加
    # 4. 超限时切分为新块
    # 5. 每个块附 metadata（来源文件、块序号）
```

定制方式：修改 `app/models/knowledge_base.py` 中 `index_document_file()` 的分块逻辑。

---

## 5. 分析模板系统

### 5.1 模板配置结构

```yaml
# templates/financial_audit.yml
id: financial_audit
name: "财务审计分析"
applicable:
  file_types: [xlsx, xls, csv]
  keywords: [财务, 支出, 预算, 审计]
  min_files: 1
  max_files: 1
analysis:
  methods: [trend_analysis, anomaly_detection, ranking]
  hints:
    time_column: "日期"
    metric_columns: ["金额"]
report:
  template: executive_dashboard
  title_template: "{{file_name}} — 财务审计分析报告"
  sections: [summary_cards, trend_chart, anomaly_table, ranking_chart]
```

### 5.2 模板加载

```python
# app/config/template_loader.py
# 启动时加载 templates/*.yml 到内存缓存
# 提供 get_template(id) 和 list_templates() 接口
```

### 5.3 Coordinator 如何使用模板

```
模板 methods → 映射到 Analyzer 的分析工具调用
模板 report.template → 传递给 Visualizer 选择 HTML 模板
模板 hints → 提示 Coordinator 优先关注哪些列
模板 sections → Visualizer 按顺序生成报告章节
```

---

## 6. API 层设计

### 6.1 端点全表

| 方法 | 路径 | 请求体 | 响应 | Agent 链路 |
|------|------|--------|------|-----------|
| POST | `/api/upload` | multipart file | `{file_id, filename, ...}` | — |
| POST | `/api/analysis/run` | `{file_ids, template_id?, nl_query?}` | `{task_id, status}` | Coordinator→3 Agent |
| GET | `/api/tasks/{id}` | — | `{task_id, status, progress}` | — |
| GET | `/api/reports/{id}` | — | HTML | — |
| GET | `/api/reports/{id}/download` | — | File | — |
| GET | `/api/templates` | — | `{templates: [...]}` | — |
| GET | `/api/history` | `?page=1&size=20` | `{total, items}` | — |
| POST | `/api/feedback/{id}` | `{satisfaction, missing_items, description}` | `{task_id, status}` | Coordinator→Analyzer→Visualizer |
| POST | `/api/knowledge/ask` | `{question, collection?}` | `{question, answer}` | Knowledge Agent |
| GET | `/api/knowledge/collections` | — | `{collections: [...]}` | — |

### 6.2 异步执行模型

```
POST /api/analysis/run
  → 同步: 创建 Task (status=pending) + 验证文件 + 返回 task_id
  → 异步: BackgroundTasks.add_task(_execute_analysis, ...)
           └─ status: pending → parsing → analyzing → visualizing → done/failed

POST /api/feedback/{id}
  → 同步: 创建新 Task + 返回 new_task_id
  → 异步: asyncio.create_task(_execute_analysis_with_feedback, ...)
           └─ 跳过 Fetcher，直接 Analyzer → Visualizer
```

### 6.3 错误处理

- 文件不存在 → 404
- 参数校验失败 → 400
- Agent 执行失败 → Task status = "failed"，error_message 记录原因
- Agent 内部工具调用失败 → 返回错误描述，不崩溃

---

## 7. 数据存储设计

### 7.1 三层存储

| 存储层 | 技术 | 内容 |
|--------|------|------|
| 文件系统 | `local_storage/` | 上传原始文件、提取数据、HTML 报告 |
| 关系型 | SQLite (`metadata.db`) | uploads / tasks / reports 表 |
| 向量库 | ChromaDB | 知识文档文本块 + Embedding 向量 |

### 7.2 SQLite 表结构

```sql
-- 文件记录
uploads (id, filename, file_type, file_size, file_path, session_id, preview, created_at)

-- 任务记录
tasks (id, upload_ids, template_id, nl_query, status, progress, analysis_config, error_message, created_at, completed_at)

-- 报告记录
reports (id, task_id, file_path, title, summary, created_at)
```

### 7.3 文件路径规范

```
local_storage/
├── uploads/{session_id}/{upload_id}_{filename}     # 上传文件
├── data/{task_id}/                                  # Fetcher 提取的数据（预留）
├── reports/{task_id}/report.html                    # 生成的 HTML 报告
├── chromadb/                                        # ChromaDB 持久化数据
├── knowledge_docs/                                  # 知识库源文档
└── metadata.db                                      # SQLite 元数据
```

---

## 8. 配置系统

### 8.1 配置层次

```
命令行参数 > 环境变量 > config.yml
```

### 8.2 config.yml

```yaml
port: 8000
storage_dir: "./local_storage"
report_retention_days: 30
max_upload_size_mb: 20
allowed_file_types: [xlsx, xls, csv, docx, pdf]
```

### 8.3 环境变量 (.env)

```bash
# LLM
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL_ID=deepseek-chat

# 存储
APP_STORAGE_DIR=./local_storage

# 设备列表（可选，用于多设备场景）
DEVICE_MODELS=

# 邮件（可选）
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SENDER_EMAIL=
```

---

## 9. 用户反馈机制

### 9.1 反馈处理流程

```
用户提交反馈
  │
  ▼
Coordinator 接收: 反馈描述 + 原始 analysis_config
  │
  ├─ 推理: 缺少什么？原因是 methods 不足还是 visualization 缺陷？
  │
  ├─ 如果缺少分析方法:
  │    追加 analysis.methods
  │    直接调用 Analyzer（跳过 Fetcher，数据已有）
  │    → Visualizer 追加章节
  │
  ├─ 如果是呈现问题:
  │    调整 report.sections 或图表类型
  │    直接调用 Visualizer 重新生成
  │
  └─ 创建新 Report，不覆盖原报告
```

### 9.2 设计决策

- **不存储用户偏好**：每次反馈独立处理，完全依赖 Coordinator（LLM）实时推理
- **保留原始报告**：反馈创建新任务和新报告，原报告不受影响
- **跳过 Fetcher**：数据不变时只重跑 Analyzer + Visualizer，节省时间

---

## 10. 依赖清单

```
# Agent 框架
strands-agents

# Web 框架
fastapi, uvicorn, python-multipart

# 数据库
sqlalchemy

# 向量数据库
chromadb

# 配置
pydantic, pydantic-settings, pyyaml, python-dotenv

# 文件解析
openpyxl, python-docx, pypdf

# 报告模板
jinja2

# 邮件（可选）
certifi
```

---

## 11. 扩展指南

### 11.1 新增 Agent

```python
# 1. app/prompt/new_agent_prompt.py
new_agent_prompt = """你是 xxx..."""

# 2. app/tools/new_tools.py
@tool
def new_tool(...): ...

# 3. app/agents/new_agent.py
@tool
def new_agent(query: str) -> str:
    agent = Agent(...)
    return agent(query)

# 4. 注册到 Coordinator (如需参与分析流程)
# coordinator_agent.py 的 tools 列表中加入 new_agent
```

### 11.2 新增分析模板

```yaml
# templates/my_template.yml
id: my_template
name: "我的分析模板"
applicable:
  file_types: [xlsx, csv]
  keywords: [关键词1, 关键词2]
analysis:
  methods: [statistical_summary, ranking]
report:
  template: executive_dashboard
  sections: [summary_cards, ranking_chart]
```

### 11.3 新增文件格式支持

```python
# app/tools/file_tools.py
@tool
def parse_json(file_path: str) -> str:
    # 解析 JSON 文件
    ...

# 注册到 fetcher_agent.py 的 tools 列表
```

### 11.4 升级向量数据库

```python
# 从 ChromaDB 迁移到 Milvus
# 1. 实现新的 search/collection 接口
# 2. 替换 app/models/knowledge_base.py 中的函数
# 3. 迁移向量数据
```

---

## 12. 技术指标

| 指标 | 数值 |
|------|------|
| Agent 数量 | 5 |
| @tool 工具数量 | 29 |
| API 端点数量 | 10 |
| Python 源文件 | 37 |
| 分析模板 | 6 个 YAML |
| 报告模板 | 2 个 HTML (Jinja2 + Chart.js) |
| 知识库 | 3 个 ChromaDB Collection |
| Embedding 维度 | 384 (ONNX all-MiniLM-L6-v2) |
| 最大上传 | 20 MB |
| 报告保留 | 30 天 |
| 单文件分析预期 | < 5 分钟 |
| 多文件分析预期 | < 8 分钟 |
