from strands import Agent, tool
from app.tools.viz_tools import (
    render_line_chart, render_bar_chart, render_radar_chart,
    render_table, render_summary_card, apply_report_template, self_review,
)
from app.tools.storage_tools import write_local_file_html
from app.models.LLM_model import ModelInstances
from app.prompt.visualizer_prompt import visualizer_prompt


@tool
def visualizer_agent(query: str) -> str:
    """
    可视化专家：将分析结果渲染为 HTML 报告，包含交互式图表。

    Args:
        query: 分析结果汇总和报告模板 ID

    Returns:
        报告生成结果
    """
    formatted_query = (
        f"请根据以下分析结果和报告模板，生成完整的 HTML 可视化报告。"
        f"使用图表渲染工具创建图表配置，然后组装完整的 HTML 页面，"
        f"自检后写入本地存储: {query}"
    )

    try:
        print("[Visualizer] 开始生成报告...")
        agent = Agent(
            system_prompt=visualizer_prompt,
            model=ModelInstances.LEADER_MODEL,
            tools=[
                render_line_chart, render_bar_chart, render_radar_chart,
                render_table, render_summary_card, apply_report_template,
                write_local_file_html, self_review,
            ],
        )
        response = agent(formatted_query)
        text_response = str(response)
        return text_response if len(text_response) > 0 else "错误：无法生成报告"
    except Exception as e:
        return f"报告生成出错: {str(e)}"
