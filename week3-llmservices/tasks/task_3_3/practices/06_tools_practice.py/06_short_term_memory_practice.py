import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()

@tool
def get_user_balance(account_id: str) -> str:
    """Retrieves current account balance for a given account ID."""
    balances = {
        "ACC-101": "$1,250.50 USD",
        "ACC-202": "$8,400.00 USD"
    }
    return balances.get(account_id.upper(), "Account ID not found.")

model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
)

agent = create_agent(
    model=model,
    tools=[get_user_balance],
    system_prompt="You are a helpful banking support assistant."
)

if __name__ == "__main__":
    conversation_history = []
    
    # --- Turn 1 ---
    print("=== TURN 1 ===")
    user_input_1 = "Hi, my account ID is ACC-101."
    conversation_history.append({"role": "user", "content": user_input_1})
    
    result_1 = agent.invoke({"messages": conversation_history})
    conversation_history = result_1["messages"]
    print("Agent:", conversation_history[-1].content)
    
    # --- Turn 2 ---
    print("\n=== TURN 2 ===")
    # Follow-up query without explicitly repeating the account ID
    user_input_2 = "What is my current balance?"
    conversation_history.append({"role": "user", "content": user_input_2})
    
    result_2 = agent.invoke({"messages": conversation_history})
    conversation_history = result_2["messages"]
    print("Agent:", conversation_history[-1].content)