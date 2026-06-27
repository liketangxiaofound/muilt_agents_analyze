from strands import Agent, tool
from app.agents.fetcher_agent import fetcher_agent
from app.agents.analyzer_agent import analyzer_agent
from app.agents.visualizer_agent import visualizer_agent
from app.models.LLM_model import ModelInstances
from app.prompt.coordinator_prompt import coordinator_prompt


coordinator = Agent(
    system_prompt=coordinator_prompt,
    model=ModelInstances.LEADER_MODEL,
    tools=[
        fetcher_agent,
        analyzer_agent,
        visualizer_agent,
    ],
)
