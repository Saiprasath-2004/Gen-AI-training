import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def format_prompt(topic: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": "You are a senior PostgreSQL teacher. Explain concepts clearly and simply."
        },
        {
            "role": "user",
            "content": f"Explain {topic}."
        }
    ]

def call_model(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content

def parse_output(text: str) -> str:
    # Custom cleaning/stripping logic
    return text.strip()

def run_pipeline(topic: str) -> str:
    messages = format_prompt(topic)
    raw_response = call_model(messages)
    return parse_output(raw_response)

if __name__ == "__main__":
    result = run_pipeline("PostgreSQL indexing")
    print(result)