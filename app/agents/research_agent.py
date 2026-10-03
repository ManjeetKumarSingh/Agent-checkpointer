from app.llm import llm
from app.state import AgentState

from app.tools.research_tools import (
    search_customer,
    get_customer_transactions,
)


research_llm = llm.bind_tools([
    search_customer,
    get_customer_transactions,
])

'''
    This agent is responsible for gathering customer information.
'''

def research_agent(state: AgentState):
    response = research_llm.invoke([
        {
            "role": "system",
            "content": (
                "You are a research agent. "
                "Analyze the task and gather customer information."
            ),
        },
        {
            "role": "user",
            "content": state["task"],
        },
    ])

    return {
        "research_result": response.content
    }