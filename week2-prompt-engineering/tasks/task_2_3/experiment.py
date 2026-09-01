import json
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("OPENROUTER_API_KEY")


if not API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is not set"
    )

URL =  "https://openrouter.ai/api/v1/chat/completions"

MODEL = "google/gemini-3.5-flash-lite"

PROMPTS_DIR = Path("prompts")
RESULTS_DIR = Path("results")

RESULTS_DIR.mkdir(exist_ok=True)

def load_prompts() -> dict[str, str]:
    prompts = {}

    for path in sorted(
        PROMPTS_DIR.glob(
            "incident_extraction.v*.txt"
        )
    ):
        version = path.stem.split(".")[-1]
        prompts[version] = path.read_text(
            encoding="utf-8"
        ).strip()

    if len(prompts) != 5:
        raise ValueError(
            "Expected exactly five prompt versions"
        )

    return prompts


def call_model(
    prompt: str,
) -> dict:

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0,
        "max_tokens": 500,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    start = time.perf_counter()

    response = httpx.post(
        URL,
        headers=headers,
        json=payload,
        timeout=60.0,
    )

    latency_ms = (time.perf_counter() - start) * 1000

    response.raise_for_status()

    data = response.json()

    usage = data.get("usage",{})

    content = (
        data["choices"][0]
        ["message"]
        .get("content","")
    )

    return {
        "response": content,
        "latency_ms":round(
            latency_ms,
            2,
        ),
        "prompt_tokens": usage.get(
            "prompt_tokens"
        ),
        "completion_tokens": usage.get(
            "completion_tokens"
        ),
        "total_tokens" : usage.get(
            "total_tokens"
        ),
        "cost_usd": usage.get(
            "cost"
        ),
    }

def main() -> None:

    prompts = load_prompts()

    results = []

    print(
        f"Running {len(prompts)} prompt versions"
    )

    for version, prompt in prompts.items():

        print()
        print("=" * 60)
        print(f"VERSION: {version}")
        print("=" * 60)

        result = call_model(prompt)

        result["version"] = version
        result["model"] = MODEL

        results.append(result)


        print(
            f"Latency: "
            f"{result['latency_ms']} ms"
        )

        print(
            f"Tokens: "
            f"{result['total_tokens']}"
        )

        print(
            f"Cost: "
            f"${result['cost_usd'] or 0:.8f}"
        )

        print()
        print(result["response"])


    output_path = (
        RESULTS_DIR
        / "prompt_iterations.json"
    )

    output_path.write_text(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8"
    )

    print()
    print(
        f"Saved: {output_path}"
    )

if __name__ == "__main__":
    main()