from typing import TypedDict


class AgentState(TypedDict, total=False): # total=False allows for additional keys
    task: str
    research_result: str
    calculation_result: str
    summary_result: str
    final_result: str