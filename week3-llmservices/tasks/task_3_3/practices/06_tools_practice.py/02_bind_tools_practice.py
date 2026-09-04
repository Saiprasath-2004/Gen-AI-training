import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

load_dotenv()

@tool
def get_table_schema(table_name: str) -> str:
    """Returns the SQL CREATE TABLE schema for a given database table name."""
    mock_db = {
        "users": "CREATE TABLE users (id SERIAL PRIMARY KEY, email VARCHAR(255) UNIQUE);",
        "orders": "CREATE TABLE orders (id SERIAL PRIMARY KEY, user_id INT, amount NUMERIC);"
    }
    return mock_db.get(table_name.lower(), f"Table '{table_name}' does not exist.")

model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
)

# 1. Bind tools to the model
model_with_tools = model.bind_tools([get_table_schema])

if __name__ == "__main__":
    print("=== TEST 1: Question requiring a tool ===")
    response_1 = model_with_tools.invoke("What columns are in the orders table?")
    
    print("Text content:", response_1.content) # Usually empty or brief when tool_calls exist
    print("Tool calls:", response_1.tool_calls)
    
    print("\n=== TEST 2: General question NOT requiring a tool ===")
    response_2 = model_with_tools.invoke("What is 2 + 2?")
    
    print("Text content:", response_2.content)
    print("Tool calls:", response_2.tool_calls)