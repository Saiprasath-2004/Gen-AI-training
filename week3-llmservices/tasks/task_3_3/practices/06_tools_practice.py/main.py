import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool

load_dotenv()

# --- Tool 1: Docstring & Type Hint Schema ---
@tool
def get_table_schema(table_name: str) -> str:
    """
        Returns the SQL CREATE TABLE schema for a given database table name.
        
        Use this when you need to inspect column names, types, or primary keys.
    """
    mock_db = {
        "users": "CREATE TABLE users (id SERIAL PRIMARY KEY, email VARCHAR(255) UNIQUE, created_at TIMESTAMP);",
        "orders": "CREATE TABLE orders (id SERIAL PRIMARY KEY, user_id INT REFERENCES users(id), amount NUMERIC(10,2));"
    }

    return mock_db.get(table_name.lower(), f"Table '{table_name}' does not exist.")

# --- Tool 2: Pydantic Schema for Complex Inputs ---
class LogQueryInput(BaseModel):
    severity: str = Field(
        description="Log severity filter: 'ERROR', 'WARNING', or 'INFO'."
    )
    limit: int = Field(
        default=3,
        description="Maximum number of log entries to retrieve."
    )
    
@tool("query_postgres_logs", args_schema=LogQueryInput)
def query_postgres_logs(severity: str, limit: int = 3) -> str:
    """Retrieves recent PostgreSQL system log entries filtered by severity level."""
    mock_logs = [
        "[ERROR] deadlock detected: Process 14022 waits for ExclusiveLock",
        "[ERROR] relation 'invalid_table' does not exist at character 15",
        "[WARNING] autovacuum transaction wraparound limit near for database 'app'",
        "[INFO] database system was shut down at 2026-09-02 10:00:00 UTC"
    ]

    filtered = [ log for log in mock_logs if severity.upper() in log]
    return "\n".join(filtered[:limit]) if filtered else "No matching logs found."

if __name__ == "__main__":
    # --- Inspecting what LangChain generates under the hood ---
    print("=== TOOL 1 METADATA ===")
    print(f"Name: {get_table_schema.name}")
    print(f"Description: {get_table_schema.description}")
    print(f"Args Schema: {get_table_schema.args}")
    
    print("\n=== TOOL 2 METADATA ===")
    print(f"Name: {query_postgres_logs.name}")
    print(f"Description: {query_postgres_logs.description}")
    print(f"Args Schema: {query_postgres_logs.args}")

    print("\n=== EXECUTING TOOLS DIRECTLY ===")
    # Tools are Runnables! You call them with .invoke()
    print("Schema Output:", get_table_schema.invoke({"table_name": "users"}))
    print("Logs Output:\n", query_postgres_logs.invoke({"severity": "ERROR", "limit": 1}))