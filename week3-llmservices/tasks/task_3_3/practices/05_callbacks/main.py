import os
import asyncio
from dotenv import load_dotenv
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

class CustomLoggingCallback(AsyncCallbackHandler):
    async def on_llm_start(self, serialized, prompts,  **kwargs):
        print("\n[CALLBACK LOG] Sent prompt to model...")

    async def on_llm_new_token(self, token: str, **kwargs):
        # Triggered on every streaming token chunk
        pass

    async def on_llm_end(self, response, **kwargs):
        print("\n[CALLBACK LOG] Model call finished!")
        token_usage = response.llm_output.get("token_usage", {})
        print(f"[CALLBACK LOG] Total Tokens: {token_usage.get('total_tokens')}")

# Wire the callback into your execution call
handler = CustomLoggingCallback()
model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
)
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a senior PostgreSQL teacher. "
        "Explain concepts clearly and simply."
    ),
    (
        "human",
        "Explain {topic}."
    ),
])
parser = StrOutputParser()

chain = prompt | model | parser

# Pass callbacks via config dictionary
async def run():
    result = await chain.ainvoke(
        {
            "topic":  "PostgreSQL",
        },
        config={
            "callbacks": [handler] ## Callback attached here!
        }
    )
    print(result)

asyncio.run(run())