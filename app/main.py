from fastapi import FastAPI
from pydantic import BaseModel
from app.state import AgentState
from app.graph import graph

app = FastAPI()


class AgentRequest(BaseModel):
    thread_id: str
    task: str


@app.post("/agent")
async def run_agent(request: AgentRequest):

    state = AgentState(
        thread_id=request.thread_id,
        task=request.task
    )
    # graph invocation will go here
    final_response = await graph.ainvoke(state)
    return final_response

