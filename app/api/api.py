"""核心 API 端点：发起分析、反馈、模板管理"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.models.database import LocalSession, Upload, Task, Report
from app.config.template_loader import get_template, list_templates

router = APIRouter()


class AnalysisRequest(BaseModel):
    file_ids: List[str]
    template_id: Optional[str] = None
    nl_query: Optional[str] = None


class FeedbackRequest(BaseModel):
    satisfaction: str = "partial"
    missing_items: List[str] = []
    description: Optional[str] = None


@router.get("/api")
async def root():
    return {"message": "Multi-Agent Data Analysis Platform", "version": "1.0.0"}


@router.get("/api/templates")
async def get_templates():
    return {"templates": list_templates()}


@router.post("/api/analysis/run")
async def run_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    if not request.file_ids:
        raise HTTPException(400, "至少需要上传一个文件")
    if not request.template_id and not request.nl_query:
        raise HTTPException(400, "请选择分析模板或输入分析需求")

    with LocalSession() as db:
        uploads = db.query(Upload).filter(Upload.id.in_(request.file_ids)).all()
        if len(uploads) != len(request.file_ids):
            raise HTTPException(404, "部分文件未找到")
        file_paths = [u.file_path for u in uploads]
        file_names = [u.filename for u in uploads]

        import uuid
        task_id = uuid.uuid4().hex[:12]
        task = Task(
            id=task_id, upload_ids=json.dumps(request.file_ids),
            template_id=request.template_id, nl_query=request.nl_query,
            status="pending", progress="任务已创建",
        )
        db.add(task)
        db.commit()

    background_tasks.add_task(
        _execute_analysis, task_id=task_id,
        file_paths=file_paths, file_names=file_names,
        template_id=request.template_id, nl_query=request.nl_query,
    )
    return {"task_id": task_id, "status": "pending"}


@router.post("/api/feedback/{task_id}")
async def submit_feedback(task_id: str, request: FeedbackRequest):
    with LocalSession() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(404, "任务不存在")
        analysis_config = json.loads(task.analysis_config or "{}")
        upload_ids = json.loads(task.upload_ids or "[]")
        uploads = db.query(Upload).filter(Upload.id.in_(upload_ids)).all()
        file_paths = [u.file_path for u in uploads]
        file_names = [u.filename for u in uploads]

    import uuid
    new_task_id = uuid.uuid4().hex[:12]
    with LocalSession() as db:
        new_task = Task(
            id=new_task_id, upload_ids=json.dumps(upload_ids),
            template_id=task.template_id,
            nl_query=f"用户反馈: {request.description or ''}，缺失: {request.missing_items}",
            status="pending", progress="基于反馈重新分析",
        )
        db.add(new_task)
        db.commit()

    import asyncio
    asyncio.create_task(_execute_analysis_with_feedback(
        task_id=new_task_id, file_paths=file_paths, file_names=file_names,
        original_config=analysis_config, feedback=request,
    ))
    return {"task_id": new_task_id, "status": "pending", "message": "已基于反馈创建新任务"}


async def _execute_analysis(task_id, file_paths, file_names, template_id, nl_query):
    """代码驱动分析流程 — 不经过 LLM 调度，直接调用工具。"""

    def update_status(status, progress):
        with LocalSession() as db:
            t = db.query(Task).filter(Task.id == task_id).first()
            if t:
                t.status = status
                t.progress = progress
                if status in ("done", "failed"):
                    t.completed_at = datetime.now().isoformat(timespec="seconds")
                db.commit()

    try:
        update_status("parsing", "正在解析文件...")
        from app.tools.storage_tools import process_file_key, ensure_directory_exists
        abs_paths = [os.path.abspath(process_file_key(p)) for p in file_paths]

        # ── 1. 解析文件 ──
        update_status("parsing", "解析文件中...")
        parsed_files = []
        for i, (name, path) in enumerate(zip(file_names, abs_paths)):
            ext = os.path.splitext(name)[1].lower()
            try:
                if ext in ('.xlsx', '.xls'):
                    from app.tools.file_tools import parse_excel
                    raw = parse_excel(path)
                elif ext == '.csv':
                    from app.tools.file_tools import parse_csv
                    raw = parse_csv(path)
                elif ext == '.docx':
                    from app.tools.file_tools import parse_docx
                    raw = parse_docx(path)
                elif ext == '.pdf':
                    from app.tools.file_tools import parse_pdf
                    raw = parse_pdf(path)
                else:
                    parsed_files.append({"filename": name, "error": f"不支持的文件类型: {ext}"})
                    continue

                data = json.loads(raw)
                if "error" in data:
                    parsed_files.append({"filename": name, "error": data["error"]})
                else:
                    parsed_files.append({"filename": name, "path": path, "data": data, "type": data.get("type")})
            except Exception as e:
                parsed_files.append({"filename": name, "error": str(e)})

        # 检查是否有可用数据
        valid = [f for f in parsed_files if "error" not in f]
        if not valid:
            msg = "所有文件都无法解析：" + "; ".join(f"{f['filename']}: {f.get('error','未知')}" for f in parsed_files)
            update_status("failed", msg)
            return

        # ── 2. 执行分析 ──
        update_status("analyzing", "执行分析中...")
        template = get_template(template_id) if template_id else None
        methods = template["analysis"]["methods"] if template else ["statistical_summary"]
        report_template_id = template["report"]["template"] if template else "executive_dashboard"

        from app.tools.analysis_tools import (
            statistical_summary, anomaly_detection, trend_analysis,
            ranking, correlation, text_summary, comparison, classification,
        )

        all_results = []
        for pf in valid:
            file_path = pf["path"]
            file_data = pf["data"]
            file_type = pf["type"]

            for method in methods:
                try:
                    if method == "statistical_summary" and file_type == "tabular":
                        r = json.loads(statistical_summary(data_json="", file_path=file_path))
                    elif method == "anomaly_detection" and file_type == "tabular":
                        # 对每个数值列做异常检测
                        sheet = file_data.get("sheets", [{}])[0]
                        num_cols = [c for c in sheet.get("columns", []) if c not in ("date", "序号")]
                        anomalies = {}
                        for col in num_cols[:3]:  # 最多 3 列
                            r = json.loads(anomaly_detection(data_json="", file_path=file_path, column=col))
                            if "error" not in r:
                                anomalies[col] = r
                        r = {"method": "anomaly_detection", "columns": anomalies,
                             "anomaly_count": sum(a.get("anomaly_count", 0) for a in anomalies.values())}
                    elif method == "trend_analysis" and file_type == "tabular":
                        sheet = file_data.get("sheets", [{}])[0]
                        cols = sheet.get("columns", [])
                        time_col = next((c for c in cols if c in ("date", "日期", "月份", "时间")), cols[0])
                        num_cols = [c for c in cols if c not in (time_col, "序号")]
                        value_col = num_cols[0] if num_cols else cols[-1]
                        r = json.loads(trend_analysis(data_json="", file_path=file_path, time_col=time_col, value_col=value_col))
                    elif method == "ranking" and file_type == "tabular":
                        sheet = file_data.get("sheets", [{}])[0]
                        num_col = next((c for c in sheet.get("columns", []) if c not in ("date", "序号")), sheet.get("columns", [])[-1])
                        r = json.loads(ranking(data_json="", file_path=file_path, column=num_col, top_n=10))
                    elif method == "correlation" and file_type == "tabular":
                        sheet = file_data.get("sheets", [{}])[0]
                        num_cols = [c for c in sheet.get("columns", []) if c not in ("date", "序号")]
                        if len(num_cols) >= 2:
                            r = json.loads(correlation(data_json="", file_path=file_path, col_a=num_cols[0], col_b=num_cols[-1]))
                        else:
                            r = {"method": "correlation", "error": "需要至少两列数值数据"}
                    elif method == "text_summary":
                        r = json.loads(text_summary(text_json=json.dumps(file_data, ensure_ascii=False, default=str)))
                    elif method == "classification":
                        r = json.loads(classification(text_json=json.dumps(file_data, ensure_ascii=False, default=str)))
                    else:
                        r = {"method": method, "error": "不支持的分析方法或文件类型不匹配"}
                except Exception as e:
                    r = {"method": method, "error": str(e)}

                r.setdefault("method", method)
                all_results.append(r)

        # ── 3. 生成报告 ──
        update_status("analyzing", "生成报告中...")
        report_path = f"reports/{task_id}/report.html"
        abs_report = os.path.abspath(process_file_key(report_path))

        # 构建摘要卡片数据
        summary_metrics = _build_summary_metrics(all_results, parsed_files)

        # 构建图表数据
        charts_html, chart_scripts = _build_charts(all_results)

        # 组装 HTML
        html = _render_report_html(
            title=f"{file_names[0] if file_names else '报告'} — 分析报告",
            template_id=report_template_id,
            summary_metrics=summary_metrics,
            all_results=all_results,
            parsed_files=parsed_files,
            charts_html=charts_html,
            chart_scripts=chart_scripts,
        )

        ensure_directory_exists(abs_report)
        with open(abs_report, "w", encoding="utf-8") as f:
            f.write(html)

        # ── 4. 记录 ──
        with LocalSession() as db:
            import uuid as _uuid
            report = Report(
                id=_uuid.uuid4().hex[:12],
                task_id=task_id,
                file_path=report_path,
                title=f"{file_names[0] if file_names else '报告'} — 分析报告",
                summary=f"成功分析 {len(valid)}/{len(parsed_files)} 个文件，执行 {len(all_results)} 项分析",
            )
            db.add(report)
            db.commit()

        update_status("done", "分析完成")
    except Exception as e:
        logging.error(f"分析任务失败: {e}", exc_info=True)
        update_status("failed", str(e))


def _build_summary_metrics(all_results, parsed_files):
    """从分析结果提取摘要指标"""
    metrics = []
    metrics.append({"label": "分析文件", "value": len(parsed_files)})

    total_rows = 0
    for pf in parsed_files:
        if "data" in pf:
            for s in pf["data"].get("sheets", []):
                total_rows += s.get("row_count", 0)
    if total_rows:
        metrics.append({"label": "数据总量", "value": f"{total_rows:,} 行"})

    for r in all_results:
        m = r.get("method", "")
        result = r.get("result", {})
        if isinstance(result, dict):
            for col, val in result.items():
                if isinstance(val, dict) and "mean" in val:
                    metrics.append({"label": f"{col} 均值", "value": f"{val['mean']:.2f}"})
                    break
            break

    anomaly_total = sum(r.get("anomaly_count", 0) for r in all_results if "anomaly_count" in r)
    if anomaly_total:
        metrics.append({"label": "异常值", "value": anomaly_total, "trend": "up"})

    return metrics


def _build_charts(all_results):
    """从分析结果构建图表 HTML 和 JS"""
    charts = []
    scripts = []

    for i, r in enumerate(all_results):
        m = r.get("method", "")
        if m == "trend_analysis" and "first_value" in r:
            cid = f"chart_trend_{i}"
            charts.append(f'<div class="chart-container"><canvas id="{cid}"></canvas></div>')
            scripts.append(f'''
            new Chart(document.getElementById("{cid}"), {{
                type: 'line',
                data: {{ labels: ["起始","结束"], datasets: [{{
                    label: '{r.get("value_column","趋势")}',
                    data: [{r.get("first_value",0)}, {r.get("last_value",0)}],
                    borderColor: '#4f46e5', tension: 0.3
                }}] }},
                options: {{ responsive: true, plugins: {{ title: {{ display: true, text: '趋势: {r.get("direction","")}' }} }} }}
            }});''')

        elif m == "ranking" and "top" in r:
            cid = f"chart_rank_{i}"
            labels = [item.get("context", {}).get("date", item.get("context", {}).get("月份", f"#{item['rank']}")) for item in r.get("top", [])]
            values = [item["value"] for item in r.get("top", [])]
            charts.append(f'<div class="chart-container"><canvas id="{cid}"></canvas></div>')
            scripts.append(f'''
            new Chart(document.getElementById("{cid}"), {{
                type: 'bar',
                data: {{ labels: {json.dumps(labels, ensure_ascii=False)}, datasets: [{{
                    label: '{r.get("column","排名")}',
                    data: {json.dumps(values)},
                    backgroundColor: '#4f46e5'
                }}] }},
                options: {{ responsive: true, plugins: {{ title: {{ display: true, text: 'Top {len(r.get("top",[]))} 排名' }} }} }}
            }});''')

    return "\n".join(charts), "\n".join(scripts)


def _render_report_html(title, template_id, summary_metrics, all_results, parsed_files, charts_html, chart_scripts):
    """渲染最终 HTML 报告"""
    from datetime import datetime

    # 摘要卡片
    cards_html = ""
    for m in summary_metrics:
        cards_html += f'<div style="flex:1;min-width:140px;padding:16px;background:#fff;border:1px solid #e5e7eb;border-radius:8px;text-align:center;"><div style="font-size:12px;color:#6b7280;">{m["label"]}</div><div style="font-size:24px;font-weight:700;color:#1a1a2e;margin-top:4px;">{m["value"]}</div></div>'

    # 结果表格
    result_rows = ""
    for r in all_results:
        m = r.get("method", "")
        if "error" in r:
            result_rows += f'<tr><td>{m}</td><td><span style="color:#ef4444">失败</span></td><td>{r["error"]}</td></tr>'
        else:
            result_rows += f'<tr><td>{m}</td><td><span style="color:#22c55e">成功</span></td><td>{_extract_insight(r)}</td></tr>'

    file_info = "".join(
        f'<tr><td>{f["filename"]}</td><td>{"成功" if "error" not in f else "失败: "+f.get("error","")}</td></tr>'
        for f in parsed_files
    )

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:#fafafa;color:#1a1a2e;line-height:1.6}}
.container{{max-width:1100px;margin:0 auto;padding:32px 20px}}
.header{{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;padding:40px 32px;border-radius:12px;margin-bottom:28px}}
.header h1{{font-size:24px;margin-bottom:6px}}
.header p{{opacity:.8;font-size:14px}}
.cards{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:28px}}
.section{{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:24px;margin-bottom:20px}}
.section h3{{font-size:16px;font-weight:600;margin-bottom:16px}}
.chart-container{{background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:20px;margin:12px 0}}
.chart-container canvas{{max-height:300px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{text-align:left;padding:8px 12px;border-bottom:1px solid #e5e7eb;color:#6b7280;font-weight:500;font-size:11px;text-transform:uppercase}}
td{{padding:8px 12px;border-bottom:1px solid #f3f4f6}}
.insight{{background:#eef2ff;border-left:3px solid #4f46e5;padding:12px 16px;margin:8px 0;border-radius:0 6px 6px 0;font-size:14px}}
.footer{{text-align:center;padding:24px;color:#9ca3af;font-size:12px}}
</style>
</head>
<body>
<div class="container">
<div class="header"><h1>{title}</h1><p>由 Multi-Agent 平台自动生成 · {datetime.now().strftime("%Y-%m-%d %H:%M")}</p></div>

<div class="section"><h3>摘要</h3><div class="cards">{cards_html}</div></div>

<div class="section"><h3>文件解析</h3><table><thead><tr><th>文件名</th><th>状态</th></tr></thead><tbody>{file_info}</tbody></table></div>

<div class="section"><h3>分析结果</h3><table><thead><tr><th>方法</th><th>状态</th><th>摘要</th></tr></thead><tbody>{result_rows}</tbody></table></div>

<div class="section"><h3>图表</h3>{charts_html or '<p style="color:#9ca3af;text-align:center;padding:20px;">暂无图表数据</p>'}</div>

<div class="footer"><p>Multi-Agent Data Analysis Platform</p></div>
</div>
<script>document.addEventListener("DOMContentLoaded",function(){{{chart_scripts}}});</script>
</body></html>'''


def _extract_insight(r):
    """从分析结果提取一句话摘要"""
    if "insights" in r and r["insights"]:
        return r["insights"][0][:100]
    if "direction" in r:
        return f"趋势: {r['direction']}，共 {r.get('data_points','?')} 个数据点"
    result = r.get("result", {})
    if isinstance(result, dict):
        keys = list(result.keys())
        if keys:
            v = result[keys[0]]
            if isinstance(v, dict) and "mean" in v:
                return f"{keys[0]}: 均值={v['mean']}, 标准差={v['std']}, N={v['count']}"
    return "分析完成"


async def _execute_analysis_with_feedback(task_id, file_paths, file_names, original_config, feedback):
    """基于用户反馈重新分析 — 直接复用代码驱动的分析流程。"""
    # 反馈信息附加到 nl_query，让分析流程知道用户的补充需求
    missing = ", ".join(feedback.missing_items) if feedback.missing_items else ""
    nl_query = f"用户反馈: {feedback.description or ''}。缺失内容: {missing}"
    await _execute_analysis(task_id, file_paths, file_names,
                            template_id=original_config.get("template_id", ""),
                            nl_query=nl_query)
