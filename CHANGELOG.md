# 改动记录

## RAG 知识库

### 分块策略优化 (`app/models/knowledge_base.py`)

- 相邻 chunk 共享 100 字符 overlap，避免关键信息在边界处被切断
- 超长段落按句子边界（中英文标点）切分，保持语义完整性
- chunk 元数据标注 `has_prev` / `has_next`，支持上下文追溯

### 关键词重排序 (`app/models/knowledge_base.py`)

新增 `rerank_by_keyword_overlap()`，搜索流程改为：向量召回 2x 候选 → 关键词命中率加权（0.7 向量 + 0.3 关键词）→ 截取 top N。中文用 bigram、英文用单词作为关键词。

### 嵌入模型切换 (`app/models/knowledge_base.py`)

去掉 ChromaDB 内置的 ONNX all-MiniLM-L6-v2（首次使用需下载 80MB，网络差时极慢），改用 sklearn TfidfVectorizer（字符级 1-2 gram，384 维），零下载、秒级就绪。

同时所有 `get_collection` / `get_or_create_collection` 调用显式传入 TF-IDF embedding function，防止 ChromaDB 内部回退到 ONNX 模型触发下载。

### 截断长度调整 (`app/tools/knowledge_tools.py`)

- 单条结果截断上限 400 → 800 字符
- `search_knowledge` 新增 `max_chars` 参数，Agent 可按需控制

### 知识文档扩充 (`knowledge_docs/`)

新增 3 份知识文档，从 3 个知识库扩展到 6 个：

| 知识库 | 文档 | 内容 |
|--------|------|------|
| it_policies | 信息化管理制度 | 网络安全、数据安全、软件采购、终端管理 |
| hr_policies | 人事管理制度 | 考勤、请假、绩效考核、薪酬福利、培训 |
| procurement | 采购管理制度 | 采购方式与限额、流程、供应商管理、验收 |

`scripts/index_knowledge.py` 同步更新 DOCS_MAP。

### Prompt 优化 (`app/prompt/knowledge_prompt.py`)

- 增加多知识库路由指引（涉及 IT → it_policies，涉及人事 → hr_policies，涉及采购 → procurement）
- 增加"不确定时先检索全部知识库"策略
- 增加检索结果不足时换关键词重试的指令

---

## 文件分析流程

### 路径解析修复

**问题**：文件上传后路径在 `api.py` 和 `file_tools.py` 中被 `process_file_key` 解析两次，导致 `local_storage/` 前缀叠加（`./local_storage/./local_storage/uploads/...`），Agent 找不到文件反复重试。

**修复** (`app/api/api.py`):
- 传给 Coordinator 之前用 `os.path.abspath(process_file_key(p))` 转为真正的绝对路径
- Agent 收到的路径形如 `/mnt/d/.../local_storage/uploads/xxx/file.pdf`，tool 层二次解析时 `os.path.isabs` 为 True，直接返回

**防御** (`app/tools/storage_tools.py`):
- `process_file_key` 检测路径已含 `local_storage/` 前缀时改用 `os.path.abspath` 不拼接

### Agent 重试控制

**Coordinator** (`app/prompt/coordinator_prompt.py`):
- 新增硬闸门：Fetcher 后如果全部文件都无法解析（零可用数据），立即终止流程直接报告用户，不进入 Analyzer/Visualizer 阶段
- 数据审核增加判定：全失败 → 终止，部分失败 → 用可用数据继续

**Fetcher** (`app/prompt/fetcher_prompt.py`):
- 文件路径必须原样传递，禁止拼接前缀或猜测路径
- 每个文件最多解析 2 次，失败即报错
- 扫描件 PDF 检测到 `full_text` 和 `pages` 均为空时直接报告，不反复重试

**Analyzer** (`app/prompt/analyzer_prompt.py`):
- 每个工具最多调用 2 次，失败就跳过并记录原因
- 工具输入（text_json / data_json）直接传 Fetcher 的原始输出，不修改格式

### 分析工具容错 (`app/tools/analysis_tools.py`)

`_parse_input()` 重写：兼容 dict、list（取首元素）、JSON 字符串、纯文本字符串四种输入格式。

`text_summary` 和 `classification` 对 paragraphs 的处理兼容两种格式：
- dict 列表：`{"text": "...", "style": "..."}`（Fetcher 原始输出）
- 纯字符串列表（Agent 可能重新格式化后的输出）

修复 `classification` 在非 dict 格式时的 `AttributeError`。

---

## 样例数据

### 生成脚本 (`scripts/generate_sample_data.py`)

一键生成 6 个固定格式测试文件到 `examples/`：

| 文件 | 内容 | 适用模板 |
|------|------|---------|
| 财务支出_2025.xlsx | 12 个月 × 8 科目，含 3 个异常值 | financial_audit |
| 部门绩效_2025H1.xlsx | 6 部门 × 4 KPI，目标 vs 实际 | performance_review |
| 销售数据_2025Q1.csv | Q1 销售数据 | comparative_analysis |
| 销售数据_2025Q2.csv | Q2 销售数据（Q1+5%~25%增长） | comparative_analysis |
| 统计分析_样本.csv | 60 行 × 5 列数值，含 3 个异常点 | statistical_summary |
| 年度统计报告.docx | 结构化文档含表格 | text_extraction |

所有数据使用固定随机种子（`random.seed(42)`），每次生成结果一致。异常值位置和数值固定，分析结果可预期。

### 初始化脚本 (`scripts/setup.sh`)

```bash
bash scripts/setup.sh
```

依次执行：生成样例数据 → 索引知识文档到 ChromaDB。

---

## Vue 3 前端（新增）

### 技术栈

| 层 | 选型 |
|----|------|
| 构建 | Vite 5 |
| 框架 | Vue 3 + Composition API |
| 类型 | TypeScript |
| 路由 | Vue Router 4 |
| HTTP | 原生 fetch |
| 样式 | 纯 CSS（indigo 单色调，简洁风格） |

### 页面结构

| 路由 | 视图 | 功能 |
|------|------|------|
| `/` | HomeView | 模式选择入口（文件分析 / 知识问答） |
| `/analysis` | AnalysisView | 上传 → 选模板 → 提交 → 进度 → 报告预览 → 反馈 |
| `/report/:id` | ReportView | 历史任务列表 / 单报告查看 |
| `/knowledge` | KnowledgeView | 对话式知识库问答 |

### 组件

| 组件 | 职责 |
|------|------|
| NavBar | 顶部导航，白色背景+底部细线 |
| FileUploader | 拖拽上传，多文件管理，上传状态 |
| TemplateSelector | 分析模板卡片选择 |
| TaskProgress | 3 秒轮询任务状态，进度条 |
| ReportFrame | iframe 渲染 HTML 报告 |
| ChatPanel | 知识问答对话面板，Markdown 渲染 |

### 开发与部署

- 开发模式：`cd frontend && npm run dev`（Vite proxy `/api` → `localhost:8000`）
- 生产构建：`npm run build` → 输出到 `app/static/`
- FastAPI 集成：`/static` 挂载静态文件，SPA fallback 非 `/api` 路由返回 `index.html`

---

## API 变更

- `GET /api/tasks` — 新增任务列表接口（按创建时间倒序，上限 50 条）
- `GET /api/knowledge/collections` — 知识库列表（已有，未改）

---

## 其他

- `.gitignore` — 排除 `.env`、`local_storage/`、`node_modules/`、`__pycache__/`、`.idea/`
- `requirements.txt` 需额外安装 `scikit-learn`
