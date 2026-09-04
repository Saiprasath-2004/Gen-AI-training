import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

load_dotenv()

@tool
def get_table_schema(table_name: str) -> str:
    """Returns the SQL CREATE TABLE schema for a given database table name."""

    mock_db = {
        "users": "CREATE TABLE users (id SERIAL PRIMARY KEY, email VARCHAR(255) UNIQUE);",
        "orders": "CREATE TABLE orders (id SERIAL PRIMARY KEY, user_id INT, amount NUMERIC(10,2));"
    }
    return mock_db.get(table_name.lower(), f"Table '{table_name}' does not exist.")

model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
).bind_tools([get_table_schema])

if __name__ == "__main__":

    # 1. Initialize conversation history
    messages = [
       SystemMessage(content="You are a senior PostgreSQL teacher. Explain answers clearly."),
       HumanMessage(content="What columns are in the orders and users table?")
    ]

    # 2. First call to the model
    ai_response = model.invoke(messages)
    messages.append(ai_response  ) # IMPORTANT: Append AIMessage to history!

    print("=== STEP 1: MODEL DECISION ===")
    print("Tool requested:", ai_response.tool_calls)
    # 3. Process tool calls

    if ai_response.tool_calls:
        count = 1 
        for call in ai_response.tool_calls:
            tool_name = call["name"]
            tool_args = call["args"]
            tool_id = call["id"]
            
            # Execute the matching tool
            if tool_name  == "get_table_schema":
                print(f"\n=== STEP 2.{count}: EXECUTING TOOL '{tool_name}' ===")
                tool_result = get_table_schema.invoke(tool_args)
                print("Tool execution result:", tool_result)
                
                # Create ToolMessage linked via tool_call_id

                tool_message = ToolMessage(
                    content = tool_result,
                    tool_call_id = tool_id
                )
                messages.append(tool_message)  # IMPORTANT: Append ToolMessage to history!
                count = count+1 #Count the number of tool calls 

    # 4. Final call to model with full conversation history
    final_response = model.invoke(messages)


    print("\n=== STEP 3: FINAL SYNTHESIZED ANSWER ===")
    print(final_response.content)

    print(messages)