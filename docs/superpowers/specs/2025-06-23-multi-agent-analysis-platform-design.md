# 通用多 Agent 数据分析平台 — 设计规格说明书

**版本**: v1.0
**日期**: 2025-06-23
**状态**: 已审批，待实施

---

## 1. 项目目标

将现有的 IoT 设备监控项目改造为**通用可复用的多 Agent 数据分析平台**。

### 1.1 核心用户

政府文职人员——不懂技术、不熟悉 Agent 概念、日常需要分析文件（Excel/CSV/Word/PDF）。

### 1.2 核心体验

上传文件 → 选分析模板（或说大白话）→ 等几分钟 → 在线查看 HTML 报告。

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端（待开发）                            │
│         文件上传 │ 模板选择 │ 自然语言输入 │ 报告查看               │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP + SSE
┌──────────────────────────▼──────────────────────────────────────┐
│                      FastAPI 服务层                               │
│  POST /api/upload          POST /api/analysis/run               │
│  GET  /api/tasks/{id}      GET  /api/reports/{id}               │
│  GET  /api/templates       GET  /api/history                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                     Agent 执行引擎（4 个 Agent）                   │
│                                                                   │
│  Coordinator Agent（协调者）                                       │
│   输入: 文件元数据 + 模板配置（或 NL 解析结果）                       │
│   职责: 规划执行路径 → 调度子 Agent → 汇总交付                       │
│   工具: [fetcher_agent, analyzer_agent, visualizer_agent]         │
│       │                           │              │                │
│       ▼                           ▼              ▼                │
│  Fetcher Agent              Analyzer Agent   Visualizer Agent     │
│  文件解析/数据提取             统计分析/异常检测  HTML报告生成        │
│  格式转换/结构识别             趋势/相关性/分类  模板填充/自检        │
└──────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    工具层 & 数据层                                 │
│  file_tools.py   analysis_tools.py   viz_tools.py               │
│  storage_tools.py  email_tools.py                                │
│  local_storage/ (文件)  +  SQLite (元数据)                        │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Agent 职责定义

#### Coordinator Agent（协调者）

- **输入**: 上传文件元数据列表 + 分析模板配置（或自然语言描述）
- **职责**: 理解分析意图 → 规划执行路径 → 依次调度 Fetcher / Analyzer / Visualizer → 处理反馈 → 汇总交付
- **工具**: `fetcher_agent`, `analyzer_agent`, `visualizer_agent`

#### Fetcher Agent（数据获取）

- **输入**: 文件路径 + 文件类型
- **职责**: 解析上传文件，提取结构化数据，输出统一格式
- **工具**: `parse_excel`, `parse_csv`, `parse_docx`, `parse_pdf`, `detect_structure`
- **输出格式**:
```json
{
  "type": "tabular | textual",
  "tables": [{"columns": [...], "rows": [...]}],
  "texts": [{"title": "...", "paragraphs": ["..."]}]
}
```

#### Analyzer Agent（数据分析）

- **输入**: Fetcher 输出的统一格式数据 + 分析方法列表
- **职责**: 执行统计分析、异常检测、趋势分析、相关性分析、文本摘要等
- **工具**: `statistical_summary`, `anomaly_detection`, `trend_analysis`, `ranking`, `correlation`, `text_summary`, `comparison`, `classification`
- **输出格式**:
```json
{
  "method": "statistical_summary",
  "result": {...},
  "insights": ["洞察1", "洞察2"],
  "confidence": 0.95
}
```

#### Visualizer Agent（可视化）

- **输入**: 分析结果 JSON + 报告模板 ID
- **职责**: 匹配报告模板、渲染图表表格、填充模板生成最终 HTML、自检报告质量
- **工具**: `render_line_chart`, `render_bar_chart`, `render_radar_chart`, `render_table`, `render_summary_card`, `apply_report_template`, `write_html`, `self_review`

### 2.3 技术栈（不动）

- **Agent 框架**: Strands Agents（Agent、@tool、Agent-as-Tool 模式）
- **Web 框架**: FastAPI + Uvicorn
- **LLM**: OpenAI 兼容接口（DeepSeek），通过环境变量配置
- **配置管理**: Pydantic + PyYAML
- **数据库**: SQLite（元数据，新增）+ 本地文件系统（数据/报告）
- **报告引擎**: Jinja2（HTML 模板）+ Chart.js（图表）

---

## 3. 分析模板系统

### 3.1 模板结构

模板是 YAML 文件，定义一个可复用的分析场景。存放在 `templates/` 目录。

```yaml
id: financial_audit
name: "财务审计分析"
description: "分析财务报表，识别支出趋势、异常科目和排名"
icon: "📊"

applicable:
  file_types: [xlsx, xls, csv]
  keywords: [财务, 支出, 预算, 科目, 审计]
  min_files: 1
  max_files: 5

analysis:
  methods:
    - trend_analysis
    - anomaly_detection
    - ranking
    - composition
  hints:
    time_column: "日期"
    metric_columns: ["金额", "支出"]
    category_column: "科目"

report:
  template: executive_dashboard
  title_template: "{{file_name}} — {{analysis_date}} 财务审计报告"
  sections:
    - summary_cards
    - trend_chart
    - anomaly_table
    - ranking_chart
    - composition_pie
    - recommendations
```

### 3.2 预置模板清单（6 个）

| 模板 ID | 名称 | 适用文件 | 分析方法 |
|---------|------|---------|---------|
| `statistical_summary` | 数据统计分析 | xlsx, csv | statistical_summary, trend, anomaly, ranking, composition |
| `text_extraction` | 文档要点提取 | docx, pdf | text_summary, classification |
| `comparative_analysis` | 对比分析 | xlsx, csv (≥2) | comparison, trend, ranking |
| `financial_audit` | 财务审计 | xlsx, csv | trend, anomaly, ranking, composition |
| `performance_review` | 绩效评估 | xlsx, csv | comparison, ranking, anomaly, trend |
| `comprehensive_report` | 综合报告 | 全部类型 | 全部方法 |

### 3.3 模板生命周期

1. 开发人员编写 YAML 文件放入 `templates/`
2. 系统启动时（或调用 reload API）加载到内存
3. 前端展示模板列表，用户选择
4. Coordinator 根据模板配置生成分析配置对象
5. 用户反馈积累到一定量后，开发人员修改 YAML 优化模板

---

## 4. 执行流程

### 4.1 请求生命周期

```
① 文件上传
  POST /api/upload → 存 local_storage/uploads/{session_id}/
                   → SQLite 记录 uploads 表

② 发起分析
  POST /api/analysis/run {files, template_id | nl_query}
  → 创建 tasks 记录 (status=pending) → 返回 task_id
  → 后台异步启动 Agent 引擎

③ Coordinator 入场
  加载模板 → 融合 NL（如有）→ 生成 analysis_config
  → SSE 推送: status=parsing

④ Fetcher 执行
  逐个文件调用 parse_* 工具 → 统一格式数据
  写 local_storage/data/{task_id}/
  → SSE 推送: status=analyzing

⑤ Analyzer 执行
  接收数据 + analysis.methods → 逐个方法执行
  合并分析结果 JSON
  → SSE 推送: status=visualizing

⑥ Visualizer 执行
  接收分析结果 + report.template → 填充模板 → 生成 HTML
  写 local_storage/reports/{task_id}/report.html
  → SSE 推送: status=done

⑦ 用户查看报告
  GET /api/reports/{task_id} → 返回 HTML
```

### 4.2 多文件处理规则

Coordinator 在规划阶段推断文件间关系（LLM 推理，不写死）：

- **同质表格文件**（2+ xlsx）→ 分别分析 + 跨表对比
- **同质文档文件**（2+ docx）→ 分别摘要 + 综合要点
- **混合文件**（表格+文档）→ 表格走数据统计、文档走文本提取 → 综合报告分享节

### 4.3 自然语言输入处理

用户输入自然语言时，Coordinator 先推理意图 → 构造等效的 analysis_config → 走同一执行引擎。同时也匹配最接近的模板用于报告样式。

---

## 5. 用户反馈机制

### 5.1 反馈入口

报告页面底部提供反馈表单：
- 满意度选择（满足/基本满足/未满足）
- 缺失分析项（多选：趋势/异常/排名/结构/对比/摘要/其他）
- 自由文本描述

### 5.2 反馈处理流程

```
反馈提交 → Coordinator 接收反馈 + 原始 analysis_config
         → Coordinator 推理: 缺少什么？怎么补？
         → 追加 analysis.methods
         → 直接调用 Analyzer（跳过 Fetcher，数据已有）
         → Visualizer 重新填充报告（追加章节）
         → 返回新报告
```

### 5.3 关键设计决策

- 重跑只走 Analyzer → Visualizer，不重新解析文件
- 不引入用户偏好存储层，完全依赖 Coordinator（强 LLM）推理
- 反复出现的同类反馈由开发人员审核后修改模板 YAML

---

## 6. 数据存储

### 6.1 本地文件系统

```
local_storage/
├── uploads/{session_id}/     # 用户上传原始文件
├── data/{task_id}/           # Fetcher 提取的结构化数据
└── reports/{task_id}/        # 生成的 HTML 报告
```

### 6.2 SQLite 元数据表

```sql
CREATE TABLE uploads (
    id          TEXT PRIMARY KEY,
    filename    TEXT NOT NULL,
    file_type   TEXT NOT NULL,     -- xlsx/csv/docx/pdf
    file_size   INTEGER,
    file_path   TEXT NOT NULL,
    session_id  TEXT NOT NULL,
    preview     TEXT,              -- Fetcher 预览 JSON
    created_at  TEXT NOT NULL
);

CREATE TABLE tasks (
    id              TEXT PRIMARY KEY,
    upload_ids      TEXT NOT NULL,     -- JSON 数组
    template_id     TEXT,
    nl_query        TEXT,
    status          TEXT NOT NULL,     -- pending/parsing/analyzing/visualizing/done/failed
    progress        TEXT,
    analysis_config TEXT,              -- Coordinator 生成的配置 JSON
    error_message   TEXT,
    created_at      TEXT NOT NULL,
    completed_at    TEXT
);

CREATE TABLE reports (
    id          TEXT PRIMARY KEY,
    task_id     TEXT NOT NULL,
    file_path   TEXT NOT NULL,
    title       TEXT,
    summary     TEXT,
    created_at  TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
```

---

## 7. 项目结构

### 7.1 改造后目录结构

```
mutli-agents/
├── app/
│   ├── agents/                     # 4 个核心 Agent
│   │   ├── coordinator_agent.py
│   │   ├── fetcher_agent.py
│   │   ├── analyzer_agent.py
│   │   └── visualizer_agent.py
│   ├── tools/                      # 按职责拆分的工具
│   │   ├── file_tools.py           # 文件解析: parse_excel/csv/docx/pdf
│   │   ├── analysis_tools.py       # 分析: statistical/anomaly/trend/ranking/...
│   │   ├── viz_tools.py            # 可视化: render_chart/table/template
│   │   ├── storage_tools.py        # 存储: 文件读写/ZIP（从现有迁移）
│   │   └── email_tools.py          # 邮件（保留）
│   ├── prompt/
│   │   ├── coordinator_prompt.py
│   │   ├── fetcher_prompt.py
│   │   ├── analyzer_prompt.py
│   │   └── visualizer_prompt.py
│   ├── models/
│   │   ├── LLM_model.py            # LLM 实例（已改造）
│   │   └── database.py             # SQLite ORM（新增）
│   ├── api/
│   │   ├── api.py                  # 核心路由
│   │   ├── upload.py               # 文件上传
│   │   ├── tasks.py                # 任务状态
│   │   └── reports.py              # 报告查询
│   ├── config/
│   │   ├── setting_env.py
│   │   └── template_loader.py      # 模板加载器（新增）
│   └── db/mysql/                   # 归档保留，不在核心链路
├── templates/                      # 分析模板 YAML（新增）
│   ├── statistical_summary.yml
│   ├── text_extraction.yml
│   ├── comparative_analysis.yml
│   ├── financial_audit.yml
│   ├── performance_review.yml
│   └── comprehensive_report.yml
├── report_templates/               # HTML 报告模板（新增）
│   ├── executive_dashboard.html
│   └── minimal_report.html
├── examples/                       # 示例数据（新增）
├── config_dev.yml
├── .env.example
├── requirements.txt
├── main.py
└── run.py
```

### 7.2 文件处置清单（零 IoT 残留）

以下逐文件列出处置方式，确保改造后代码中不存在任何 `device_model`、`app_rates`、`firmware_rates`、`连接率`、`帧延迟`、`P2P` 等 IoT 领域术语。

#### 7.2.1 保留不动（5 个基础文件）

| 文件 | 说明 |
|------|------|
| `run.py` | Uvicorn 启动脚本，无需改动 |
| `main.py` | FastAPI 入口，微调路由注册 |
| `.env.example` | 环境变量模板，更新注释去掉 IoT 相关说明 |
| `requirements.txt` | 补充 openpyxl, python-docx, pypdf, jinja2 |
| `app/models/LLM_model.py` | 已是通用 LLM 配置（env 读取），不动 |

#### 7.2.2 保留但拆分重组（1 个文件 → 2 个文件）

| 原文件 | 处置 |
|-------|------|
| `app/tools/strands_agents_tool.py` | **拆分**。保留通用函数（`process_file_key`, `ensure_directory_exists`, `write_local_file`, `write_local_file_html`, `get_local_file_metadata`, `write_local_file_zip`, `read_local_file`, `send_email`）→ 迁至 `storage_tools.py` 和 `email_tools.py`。**删除** 4 个 IoT 专用 tool（`get_and_upload_app_rates`, `get_and_upload_firmware_rates`, `get_and_upload_app_speeds`, `get_and_upload_firmware_speeds`）。原文件整体删除。 |

#### 7.2.3 重写（2 个文件：API + 配置）

| 原文件 | 处置 |
|-------|------|
| `app/api/api.py` | **完全重写**。删除 3 个 IoT 查询端点和 `strands_agents` 端点（含 `device_model` 循环）。替换为 7 个新端点（upload / analysis / tasks / reports / templates / history / feedback）。 |
| `app/config/setting_env.py` | **精简重写**。删除 `prompt` 和 `description` 两个硬编码 dict（含 IoT Agent 描述）。保留 `MysqlProperties`、`ThirdPartyProperties`、`Setting` 的通用配置结构。 |

#### 7.2.4 重命名+重写（4 个 Agent 文件）

| 原文件 | 新文件 | 说明 |
|-------|--------|------|
| `app/agents/lead_agent.py` | `app/agents/coordinator_agent.py` | 角色从"P2P 报告团队负责人"→"数据分析项目协调者"，工具集从 7 个 IoT Agent → 3 个通用 Agent |
| `app/agents/data_query_agent.py` | `app/agents/fetcher_agent.py` | 角色从"IoT 数据查询"→"通用文件解析"，工具从 4 个 MySQL 专用查询 → 5 个文件解析工具 |
| `app/agents/data_analyst_agent.py` | `app/agents/analyzer_agent.py` | 角色从"连接率/帧延迟分析"→"通用数据分析"，工具从文件读写 → 8 个分析工具 |
| `app/agents/web_engineer_agent.py` | `app/agents/visualizer_agent.py` | 角色从"固定 P2P 报告"→"模板化报告生成"，工具新增渲染+自检 |

#### 7.2.5 彻底删除（24 个文件/目录）

| 删除项 | 原因 |
|-------|------|
| `app/agents/html_report_review_agent.py` | 审核能力内化到 Visualizer 的 `self_review` 工具 |
| `app/agents/summary_html_agent.py` | 汇总能力由 Coordinator + Visualizer 处理 |
| `app/agents/zip_file_agent.py` | ZIP 工具保留在 storage_tools，Agent 不再单独存在 |
| `app/agents/send_email_agent.py` | 邮件工具保留在 email_tools，Agent 不再单独存在 |
| `app/prompt/lead_prompt.py` | IoT 专用（"P2P 报告团队"），替换为 `coordinator_prompt.py` |
| `app/prompt/data_query_prompt.py` | IoT 专用（含 "get_and_upload_app_rates" 等），替换为 `fetcher_prompt.py` |
| `app/prompt/data_analyst_prompt.py` | IoT 专用（"连接率/帧延迟"），替换为 `analyzer_prompt.py` |
| `app/prompt/web_engieer_prompt.py` | IoT 专用（固定报告结构），替换为 `visualizer_prompt.py` |
| `app/prompt/html_report_review_prompt.py` | 审核能力内化，不再需要独立 prompt |
| `app/prompt/summary_html_prompt.py` | 不再有独立汇总 Agent |
| `app/prompt/zip_file_prompt.py` | 不再有独立 ZIP Agent |
| `app/prompt/send_email_prompt.py` | 不再有独立邮件 Agent |
| `app/db/mysql/live_connection_log.py` | IoT 专用表模型（`device_model` 主键） |
| `app/db/mysql/live_connection_statistic_rate_5m.py` | IoT 专用表模型（`connection_rate` 等） |
| `app/db/mysql/live_connection_statistics_speed_5m.py` | IoT 专用表模型（`first_frame_time` 等） |
| `app/db/mysql/__init__.py` | 删除后目录为空 |
| `app/db/__init__.py` | 删除后目录为空 |
| `app/servics/get_device_model.py` | IoT 专用（设备型号循环） |
| `app/servics/get_date.py` | 功能迁至 `storage_tools.py` 或内联 |
| `app/servics/mysql_service.py` | IoT 专用（绑定 setting_sql），通用 MySQL 连接逻辑迁至数据源抽象层 |
| `app/servics/__init__.py` | 删除后目录为空 |
| `app/config/setting_sql.py` | IoT 专用配置加载器（与 `setting_env.py` 重复逻辑） |
| `config_dev.yml` | 原有内容为 IoT MySQL 空配置，替换为通用配置文件 |
| `mutli-agents/` (空目录) | 历史残留 |

#### 7.2.6 全新创建

| 新建项 | 说明 |
|-------|------|
| `app/agents/coordinator_agent.py` | 协调者 Agent |
| `app/agents/fetcher_agent.py` | 数据获取 Agent |
| `app/agents/analyzer_agent.py` | 数据分析 Agent |
| `app/agents/visualizer_agent.py` | 可视化 Agent |
| `app/prompt/coordinator_prompt.py` | 通用协调 prompt |
| `app/prompt/fetcher_prompt.py` | 通用文件解析 prompt |
| `app/prompt/analyzer_prompt.py` | 通用数据分析 prompt |
| `app/prompt/visualizer_prompt.py` | 通用可视化 prompt |
| `app/tools/file_tools.py` | parse_excel/csv/docx/pdf + detect_structure |
| `app/tools/analysis_tools.py` | 8 个通用分析 tool |
| `app/tools/viz_tools.py` | 6 个可视化渲染 tool |
| `app/tools/storage_tools.py` | 从原 strands_agents_tool 迁出的通用文件工具 |
| `app/tools/email_tools.py` | 从原 strands_agents_tool 迁出的邮件工具 |
| `app/models/database.py` | SQLite ORM（uploads / tasks / reports 三张表） |
| `app/api/upload.py` | 文件上传端点 |
| `app/api/tasks.py` | 任务状态端点 |
| `app/api/reports.py` | 报告查询端点 |
| `app/config/template_loader.py` | YAML 模板加载器 |
| `templates/` 下 6 个 `.yml` | 预置分析模板 |
| `report_templates/` 下 2 个 `.html` | Jinja2 + Chart.js 报告模板 |
| `examples/` 下 2-3 个示例文件 | 示例 Excel/Word 数据 + 使用说明 |

#### 7.2.7 效果验证标准

改造完成后，在项目根目录执行以下检查应全部返回空：

```bash
# 不应存在任何 IoT 领域术语
grep -r "device_model\|app_rates\|firmware_rates\|app_speeds" app/ --include="*.py"
grep -r "firmware_speeds\|连接率\|帧延迟\|P2P\|p2p" app/ --include="*.py"
grep -r "get_and_upload\|list_connection_statistics\|list_live_connection" app/ --include="*.py"
grep -r "TbLiveConnection\|device_firmware_version" app/ --include="*.py"
```

---

## 8. API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/upload` | 上传文件，返回 file_id + preview |
| `POST` | `/api/analysis/run` | 发起分析，传 files + template_id 或 nl_query，返回 task_id |
| `GET` | `/api/tasks/{id}` | 查询任务状态和进度 |
| `GET` | `/api/reports/{id}` | 获取/下载 HTML 报告 |
| `GET` | `/api/templates` | 获取可用分析模板列表 |
| `GET` | `/api/history` | 历史分析记录分页列表 |
| `POST` | `/api/feedback/{task_id}` | 提交报告反馈，触发重跑 |

---

## 9. 依赖变更

在现有 `requirements.txt` 基础上新增：

```
openpyxl>=3.1.0      # Excel 解析
python-docx>=1.1.0   # Word 解析
pypdf>=4.0.0         # PDF 解析
jinja2>=3.1.0        # HTML 模板引擎
```

---

## 10. 非功能需求

### 10.1 性能
- 单文件分析（5MB 以内）应在 5 分钟内完成
- 多文件分析（3 个文件以内）应在 8 分钟内完成

### 10.2 安全
- 上传文件大小限制：20MB
- 上传文件类型白名单：xlsx, xls, csv, docx, pdf
- 报告仅存储 30 天，超期自动清理
- 不对外暴露文件路径，通过 API 返回

### 10.3 可扩展性
- 新增分析模板：编写 YAML → 放入 templates/ → 重载即可
- 新增分析工具：编写 @tool 函数 → 注册到对应 Agent
- 新增文件格式支持：编写 parse_xxx 工具 → 注册到 Fetcher

---

## 11. 验收标准

1. 上传一个 xlsx 文件，选择"数据统计分析"模板，生成含趋势图+排名表+异常标记的 HTML 报告
2. 上传一个 docx 文件，选择"文档要点提取"模板，生成含结构摘要+关键要点+分类整理的 HTML 报告
3. 上传两个 xlsx 文件，选择"对比分析"模板，生成含差异对比图+趋势对比+综合结论的 HTML 报告
4. 对已生成报告提交反馈"缺少结构分析"，系统自动重跑并在报告中追加该章节
5. 上传混合文件（xlsx + docx），选择"综合报告"模板，生成包含数据图表和文本摘要的综合报告
