import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks import AsyncCallbackHandler

load_dotenv()

# Callback hook for Week 6 observability
class Week6TracingCallback(AsyncCallbackHandler):
    async def on_llm_start(self, serialized, prompts, **kwargs):
        pass  # Week 6: Hook into Langfuse trace logging

    async def on_llm_end(self, response, **kwargs):
        pass  # Week 6: Extract token usage, latency, and costs for dashboard analytics

# 1. Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a senior PostgreSQL teacher. Explain concepts clearly and simply."),
    ("human", "Explain {topic}.")
])

# 2. Chat Model Provider Abstraction
model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.7,
)

# 3. Output Parser
parser = StrOutputParser()

# 4. LCEL Pipeline
chain = prompt | model | parser

async def run_pipeline(topic: str) -> str:
    # Pointing at callback hook via config
    return await chain.ainvoke(
        {"topic": topic},
        config={"callbacks": [Week6TracingCallback()]}
    )

if __name__ == "__main__":
    print(asyncio.run(run_pipeline("PostgreSQL indexing")))