```python
                         User Request
                              │
                              ▼
                     ┌─────────────────┐
                     │   LangGraph     │
                     │   Supervisor    │
                     └────────┬────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
          ┌──────────┐  ┌──────────┐  ┌──────────┐
          │ Research │  │   Data   │  │  Coding  │
          │  Agent   │  │  Agent   │  │  Agent   │
          └────┬─────┘  └────┬─────┘  └────┬─────┘
               │             │             │
               ▼             ▼             ▼
          Internal Tools  Internal Tools  Internal Tools
               │             │             │
               └─────────────┼─────────────┘
                             ▼
                    ┌─────────────────┐
                    │    Synthesizer  │
                    │      Agent      │
                    └────────┬────────┘
                             │
                             ▼
                           Result

```

```
Agent-checkpointer/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── graph.py
│   ├── state.py
│   ├── llm.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── research_agent.py
│   │   ├── calculation_agent.py
│   │   └── summary_agent.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── research_tools.py
│       └── calculation_tools.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```


```requirements.txt 

fastapi
uvicorn[standard]

langgraph
langchain
langchain-core

langchain-groq

langgraph-checkpoint-postgres
psycopg[binary,pool]

python-dotenv
pydantic

black

```


### For running the api endpoints :

`uvicorn app.main:app --reload`