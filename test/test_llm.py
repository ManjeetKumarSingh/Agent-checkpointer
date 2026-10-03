from app.llm import llm

response = llm.invoke(
    "Explain LangGraph StateGraph in three sentences."
)

print(response.content)