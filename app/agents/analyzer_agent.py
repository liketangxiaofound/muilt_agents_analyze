from strands import Agent, tool
from app.tools.analysis_tools import (
    statistical_summary, anomaly_detection, trend_analysis,
    ranking, correlation, text_summary, comparison, classification,
)
from app.models.LLM_model import ModelInstances
from app.prompt.analyzer_prompt import analyzer_prompt


@tool
def analyzer_agent(query: str) -> str:
    """
    数据分析专家：对结构化数据执行统计分析、异常检测、趋势分析等。

    Args:
        query: 结构化数据和分析方法列表

    Returns:
        分析结果 JSON
    """
    formatted_query = (
        f"请对以下数据执行分析。使用提供的工具逐项完成分析方法列表中的每一项，"
        f"最后汇总所有分析结果和综合洞察: {query}"
    )

    try:
        print("[Analyzer] 开始数据分析...")
        agent = Agent(
            system_prompt=analyzer_prompt,
            model=ModelInstances.LEADER_MODEL,
            tools=[
                statistical_summary, anomaly_detection, trend_analysis,
                ranking, correlation, text_summary, comparison, classification,
            ],
        )
        response = agent(formatted_query)
        text_response = str(response)
        return text_response if len(text_response) > 0 else "错误：无法完成数据分析"
    except Exception as e:
        return f"数据分析出错: {str(e)}"
