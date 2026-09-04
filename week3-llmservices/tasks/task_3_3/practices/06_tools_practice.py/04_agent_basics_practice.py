import os
from dotenv import load_dotenv
from langchain_openai  import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()

@tool
def get_table_schema(table_name: str) -> str:
    """Returns the SQL CREATE TABLE schema for a given database table name."""
    mock_db = {
        "users": "CREATE TABLE users (id SERIAL PRIMARY KEY, email VARCHAR(255) UNIQUE);",
        "orders": "CREATE TABLE orders (id SERIAL PRIMARY KEY, user_id INT, amount NUMERIC(10,2));"
    }
    return mock_db.get(table_name.lower(), f"Table '{table_name}' does not exist.")

@tool
def query_postgres_logs(severity: str, limit: int = 2) -> str:
    """Retrieves recent PostgreSQL system log entries filtered by severity level."""
    mock_logs = [
        "[ERROR] deadlock detected: Process 14022 waits for ExclusiveLock",
        "[ERROR] relation 'invalid_table' does not exist at character 15",
        "[WARNING] autovacuum transaction wraparound limit near for database 'app'"
    ]
    filtered = [log for log in mock_logs if severity.upper() in log]
    return "\n".join(filtered[:limit]) if filtered else "No matching logs found."

# 1. Instantiate model
model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
)


agent = create_agent(
    model=model,
    tools=[get_table_schema, query_postgres_logs],
    system_prompt="You are a senior PostgreSQL DBA assistant."
)

if __name__ == "__main__":
    # 3. Execute the agent with a complex query requiring multiple tools
    result = agent.invoke(
        {
            "messages":  [
                {
                    "role": "user", 
                    "content": "Check the recent ERROR logs and give me the schema for the orders table."
                }
            ]
        }
    )


    print("=== FULL CONVERSATION HISTORY PRODUCED BY AGENT ===")
    for msg in result["messages"]:
        print(f"\n[{msg.__class__.__name__}]: {msg.content}")
        if getattr(msg, "tool_calls",None):
            print(f" -> Tool Calls: {msg.tool_calls}")