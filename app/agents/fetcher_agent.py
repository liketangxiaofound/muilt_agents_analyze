from strands import Agent, tool
from app.tools.file_tools import (
    parse_excel, parse_csv, parse_docx, parse_pdf, detect_structure,
)
from app.models.LLM_model import ModelInstances
from app.prompt.fetcher_prompt import fetcher_prompt


@tool
def fetcher_agent(query: str) -> str:
    """
    数据获取专家：解析用户上传的文件（Excel / CSV / Word / PDF），
    提取结构化数据并识别数据类型。

    Args:
        query: 文件路径列表和解析指令

    Returns:
        统一格式的结构化数据 JSON
    """
    formatted_query = (
        f"请解析以下文件，调用对应的 parse_* 工具提取结构化数据，"
        f"然后调用 detect_structure 分析每列的数据类型: {query}"
    )

    try:
        print("[Fetcher] 开始解析文件...")
        agent = Agent(
            system_prompt=fetcher_prompt,
            model=ModelInstances.LEADER_MODEL,
            tools=[parse_excel, parse_csv, parse_docx, parse_pdf, detect_structure],
        )
        response = agent(formatted_query)
        text_response = str(response)
        return text_response if len(text_response) > 0 else "错误：无法解析文件，请确认文件格式正确"
    except Exception as e:
        return f"数据获取出错: {str(e)}"
