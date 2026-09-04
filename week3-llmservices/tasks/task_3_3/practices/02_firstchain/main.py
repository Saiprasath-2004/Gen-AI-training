import sys
import types


# Create a dummy module to intercept tiktoken before langchain_openai imports it
dummy_tiktoken = types.ModuleType("tiktoken")
dummy_tiktoken.encoding_for_model = lambda name: None
dummy_tiktoken.get_encoding = lambda name: None
sys.modules["tiktoken"] = dummy_tiktoken

import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import  ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()

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

def prepare_topic(input_dict):
    clean_topic = input_dict["topic"].strip()

    return{
        "topic": clean_topic
    }
        
    

prepare_topic_runnable = RunnableLambda(prepare_topic)

chain = ( prepare_topic_runnable | prompt | model | parser)

async def main():

    topic = input("What should i learn?:  ")
    print("\nAnswer: ")
    async for chunk in chain.astream(
        {
            "topic": topic
        }
    ):
        print(chunk, end="", flush=True)
    print()

if __name__ == "__main__":
    #Run the async entry point using asyncio

    asyncio.run(main())

# messages = prompt.invoke({
#     "topic": "PostgreSQL indexing"
# })

# print("PROMPT OUTPUT:")
# print(type(messages))
# print(messages)


# model_response = model.invoke(messages)

# print("\nMODEL OUTPUT:")
# print(type(model_response))
# print(model_response)


# parsed = parser.invoke(model_response)

# print("\nPARSER OUTPUT:")
# print(type(parsed))
# print(parsed)