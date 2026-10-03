from app.llm import llm
from app.state import AgentState
from app.tools.calculation_tools import calculate_risk


calculation_llm = llm.bind_tools([
    calculate_risk
])


def calculation_agent(state: AgentState):
    response = calculation_llm.invoke([
        {
            "role": "system",
            "content": (
                "You are a calculation agent. "
                "Perform numerical analysis."
            ),
        },
        {
            "role": "user",
            "content": state["task"],
        },
    ])

    return {
        "calculation_result": response.content
    }