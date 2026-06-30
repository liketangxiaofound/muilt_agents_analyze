"""
可视化工具

提供图表配置生成、HTML 表格渲染、报告模板填充、质量自检等能力。
"""
import json
from strands import tool


@tool
def render_line_chart(data_json: str, title: str, x_label: str, y_label: str) -> str:
    """生成 Chart.js 折线图配置 JSON。"""
    try:
        chart_data = json.loads(data_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "data_json 不是有效 JSON"})
    config = {"type": "line", "data": chart_data, "options": {"responsive": True, "maintainAspectRatio": False, "plugins": {"title": {"display": True, "text": title, "font": {"size": 16}}, "tooltip": {"mode": "index", "intersect": False}}, "scales": {"x": {"title": {"display": True, "text": x_label}}, "y": {"title": {"display": True, "text": y_label}, "beginAtZero": False}}}}
    return json.dumps(config, ensure_ascii=False)


@tool
def render_bar_chart(data_json: str, title: str, x_label: str, y_label: str) -> str:
    """生成 Chart.js 柱状图配置 JSON。"""
    try:
        chart_data = json.loads(data_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "data_json 不是有效 JSON"})
    config = {"type": "bar", "data": chart_data, "options": {"responsive": True, "maintainAspectRatio": False, "plugins": {"title": {"display": True, "text": title, "font": {"size": 16}}, "tooltip": {"mode": "index", "intersect": False}}, "scales": {"x": {"title": {"display": True, "text": x_label}}, "y": {"title": {"display": True, "text": y_label}, "beginAtZero": True}}}}
    return json.dumps(config, ensure_ascii=False)


@tool
def render_radar_chart(data_json: str, title: str) -> str:
    """生成 Chart.js 雷达图配置 JSON。"""
    try:
        chart_data = json.loads(data_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "data_json 不是有效 JSON"})
    config = {"type": "radar", "data": chart_data, "options": {"responsive": True, "maintainAspectRatio": False, "plugins": {"title": {"display": True, "text": title, "font": {"size": 16}}}}}
    return json.dumps(config, ensure_ascii=False)


@tool
def render_table(data_json: str, title: str) -> str:
    """生成 HTML 表格片段。"""
    try:
        table_data = json.loads(data_json)
    except json.JSONDecodeError:
        return "<p style='color:red;'>错误：data_json 不是有效 JSON</p>"
    columns = table_data.get("columns", [])
    rows = table_data.get("rows", [])
    html = f"<h3>{title}</h3>\n<table style='width:100%;border-collapse:collapse;margin:16px 0;'>\n<thead><tr>"
    for col in columns:
        html += f"<th style='border:1px solid #ddd;padding:8px;background:#f5f5f5;text-align:left;'>{col}</th>"
    html += "</tr></thead>\n<tbody>"
    for i, row in enumerate(rows):
        bg = "#fafafa" if i % 2 == 0 else "#fff"
        html += f"<tr style='background:{bg};'>"
        for cell in row:
            val = str(cell) if cell is not None else ""
            html += f"<td style='border:1px solid #ddd;padding:8px;'>{val}</td>"
        html += "</tr>\n"
    html += "</tbody></table>"
    return html


@tool
def render_summary_card(metrics_json: str) -> str:
    """生成数据摘要卡片 HTML 片段。"""
    try:
        metrics = json.loads(metrics_json)
    except json.JSONDecodeError:
        return "<p style='color:red;'>错误：metrics_json 不是有效 JSON</p>"
    trend_icons = {"up": "▲", "down": "▼", "flat": "—"}
    trend_colors = {"up": "#22c55e", "down": "#ef4444", "flat": "#6b7280"}
    cards = ""
    for m in metrics:
        trend = m.get("trend", "flat")
        icon = trend_icons.get(trend, "")
        color = trend_colors.get(trend, "#6b7280")
        cards += f"<div style='flex:1;min-width:180px;padding:20px;background:#fff;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.1);text-align:center;'><div style='font-size:14px;color:#6b7280;margin-bottom:8px;'>{m.get('label', '')}</div><div style='font-size:28px;font-weight:bold;color:#1f2937;'>{m.get('value', '')}<span style='font-size:16px;color:{color};'>{icon}</span></div></div>"
    return f"<div style='display:flex;gap:16px;flex-wrap:wrap;margin:24px 0;'>{cards}</div>"


@tool
def apply_report_template(template_id: str, analysis_results_json: str) -> str:
    """读取报告模板并返回模板 HTML 内容。Agent 直接将分析结果填入模板的 {{ content }} 和 {{ chart_scripts }} 区域即可，不需要再单独读取模板文件。"""
    import os
    if template_id == "executive_dashboard":
        name = "executive_dashboard"
    else:
        name = "minimal_report"

    # 模板在项目根目录的 report_templates/ 下
    template_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "report_templates", f"{name}.html")
    template_path = os.path.normpath(template_path)

    if not os.path.exists(template_path):
        return json.dumps({"error": f"模板文件不存在: {template_path}", "fallback": "请直接构建完整的 HTML 报告，包含 Chart.js CDN、响应式设计、摘要卡片、图表和表格。"}, ensure_ascii=False)

    with open(template_path, "r", encoding="utf-8") as f:
        template_html = f.read()

    return json.dumps({
        "template": name,
        "html": template_html,
        "usage": "将分析结果填入模板的 {{ content }} 区域（HTML片段）和 {{ chart_scripts }} 区域（Chart.js初始化脚本）。使用 render_line_chart、render_bar_chart、render_table、render_summary_card 等工具生成内容填充。",
    }, ensure_ascii=False)


@tool
def self_review(html_content: str) -> str:
    """对生成的 HTML 报告进行质量自检。"""
    checks = [
        {"check": "DOCTYPE", "pass": "<!DOCTYPE html>" in html_content[:100]},
        {"check": "charset", "pass": "charset" in html_content.lower()},
        {"check": "viewport", "pass": "viewport" in html_content.lower()},
        {"check": "chartjs_cdn", "pass": "chart.js" in html_content.lower()},
        {"check": "body_tag", "pass": "<body" in html_content.lower() and "</body>" in html_content.lower()},
    ]
    placeholders = ["{{", "}}", "TODO", "FIXME"]
    issues = [f"发现未替换的占位符: {ph}" for ph in placeholders if ph in html_content]
    all_pass = all(c["pass"] for c in checks) and len(issues) == 0
    return json.dumps({"overall": "pass" if all_pass else "needs_fix", "checks": checks, "issues": issues}, ensure_ascii=False)
