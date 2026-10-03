from app.llm import llm
from app.state import AgentState


def summary_agent(state: AgentState):

    prompt = f"""
You are a senior analyst.

Original task:
{state["task"]}

Research result:
{state.get("research_result", "")}

Calculation result:
{state.get("calculation_result", "")}

Create a concise final answer.
"""

    response = llm.invoke(prompt)

    return {
        "final_result": response.content
    }