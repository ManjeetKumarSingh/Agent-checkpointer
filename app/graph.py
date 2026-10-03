from langgraph.graph import StateGraph, START, END

from app import checkpointer
from app.state import AgentState
from app.agents.research_agent import research_agent
from app.agents.calculation_agent import calculation_agent
from app.agents.summary_agent import summary_agent


builder = StateGraph(AgentState)

builder.add_node(
    "research",
    research_agent,
)

builder.add_node(
    "calculation",
    calculation_agent,
)

builder.add_node(
    "summary",
    summary_agent,
)

builder.add_edge(
    START,
    "research",
)

builder.add_edge(
    START,
    "calculation",
)

builder.add_edge(
    "research",
    "summary",
)

builder.add_edge(
    "calculation",
    "summary",
)

builder.add_edge(
    "summary",
    END,
)

graph = builder.compile()


def create_graph():
    builder = StateGraph(AgentState)
    builder.add_node("research", research_agent)
    builder.add_node("calculation", calculation_agent)
    builder.add_node("summary", summary_agent)
    builder.add_edge(START, "research")
    builder.add_edge(START, "calculation")
    builder.add_edge("research", "summary")
    builder.add_edge("calculation", "summary")
    builder.add_edge("summary", END)
    return builder.compile(
        checkpointer=checkpointer
    )

