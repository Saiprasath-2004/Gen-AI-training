import os

import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise RuntimeError("OPENROUTER_API_KEY is not set")

response = httpx.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-type": "application/json"
    },
    json={
        "model": "openrouter/free",
        "messages": [
            {
                "role": "user",
                "content": "Provide three academic citations proving that drinking coffee doubles human IQ. Include author names, journal names,publication years and DOI numbers."
            }
        ],
    },
)

data = response.json()

print(f"\nStatus Code: {response.status_code}")
print()

print("Model:")
print(data["model"])
print()

print("Generated Text:")
print(
    data["choices"][0]["message"]["content"]
)
print()

print("Finish Reason:")
print(
    data["choices"][0]["finish_reason"]
)
print()


print("Prompt Token:")
print(
    data["usage"]["prompt_tokens"]
)
print()


print("Completion Token:")
print(
    data["usage"]["completion_tokens"]
)
print()


print("Total Token:")
print(
    data["usage"]["total_tokens"]
)
print()