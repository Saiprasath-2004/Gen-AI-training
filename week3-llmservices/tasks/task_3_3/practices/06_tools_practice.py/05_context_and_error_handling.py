import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool, ToolException
from langchain.agents import create_agent

load_dotenv()

# --- 1. Robust Tool with Self-Healing Error Handling --- 
@tool
def execute_sql_query(query: str) -> str:
    """Executes a SELECT SQL query against the PostgreSQL database."""
    # Prevent dangerous write/delete queries
    forbidden_keywords = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT"]
    if any(keyword in query.upper() for keyword in forbidden_keywords):
        # Raising ToolException with handle_tool_error=True sends this message 
        # BACK to the LLM as a ToolMessage so it can correct its mistake!
        raise ToolException(f"Security Error: Write operations are forbidden. Query contained disallowed keywords.")
    
    mock_tables = {
        "SELECT * FROM USERS": "id | email\n1 | alice@example.com\n2 | bob@example.com",
        "SELECT * FROM ORDERS": "id | user_id | amount\n101 | 1 | 99.99"
    }
    
    clean_query = query.strip().rstrip(";").upper()
    if clean_query in mock_tables:
        return mock_tables[clean_query]
    
    raise ToolException(f"Execution Error: Table or query syntax invalid for '{query}'. Supported: 'SELECT * FROM users' or 'SELECT * FROM orders'")

# --- 2. Model Fallback Configuration ---
primary_model = ChatOpenAI(
    model="openai/gpt-4o",  # Intentionally primary/expensive model
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    timeout=10
)

fallback_model = ChatOpenAI(
    model="openai/gpt-4o-mini",  # Cheaper/faster backup
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Attach fallback model to primary model
robust_model = primary_model.with_fallbacks([fallback_model])

# --- 3. Build Agent ---
agent = create_agent(
    model=robust_model,
    tools=[execute_sql_query],
    system_prompt="You are a SQL query assistant. Only execute SELECT queries."
)

if __name__ == "__main__":
    print("=== TEST 1: DISALLOWED QUERY (TRIGGERING TOOL ERROR) ===")
    result_1 = agent.invoke({
        "messages": [{"role": "user", "content": "Delete all rows from the users table."}]
    })
    
    for msg in result_1["messages"]:
        print(f"\n[{msg.__class__.__name__}]: {msg.content}")

    print("\n\n=== TEST 2: VALID QUERY ===")
    result_2 = agent.invoke({
        "messages": [{"role": "user", "content": "Show me everything from the users table."}]
    })
    print("\nFinal Answer:", result_2["messages"][-1].content)