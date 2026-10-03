import os

from dotenv import load_dotenv
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


pool = AsyncConnectionPool(
    conninfo=DATABASE_URL,
    max_size=10,
)


checkpointer = AsyncPostgresSaver(pool)

async def initialize_checkpointer():
    await pool.open()
    await checkpointer.setup()

# checkpointer.save_checkpoint("test", 1) 