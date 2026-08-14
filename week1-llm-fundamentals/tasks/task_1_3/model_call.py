import json
import logging
import os
import time
from pathlib import Path

import httpx
import tiktoken
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "google/gemini-2.5-flash-lite",
)

USD_TO_INR = float(
    os.getenv("USD_TO_INR", "95.00")
)

URL = "https://openrouter.ai/api/v1/chat/completions"



LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | %(message)s"
    ),
    handlers=[
        logging.FileHandler(
            LOG_DIR / "model_metrics.log",
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def count_prompt_tokens(prompt: str) -> int:
    """Estimate prompt token count locally."""
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(prompt))

def calculate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    input_price_per_million: float,
    output_price_per_million: float,
) -> float:
    """Calculating model cost from published token pricing"""

    input_cost = (
        prompt_tokens / 1_000_000
    ) * input_price_per_million

    output_cost = (
        completion_tokens / 1_000_000
    ) * output_price_per_million

    return input_cost + output_cost

def main() -> None:
    """Run one measure OpenRouter model call"""

    if not API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set"
        )

    prompt = (
        "Explain what an API is in three "
        "simple sentences."
    )

    # 1. Count prompt tokens BEFORE sending

    local_prompt_tokens = count_prompt_tokens(
        prompt
    )

    print(
        f"Local prompt token estimate: "
        f"{local_prompt_tokens}"
    )

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "max_tokens": 100,
    }

    headers = {
        "Authorization": (
            f"bearer {API_KEY}"
        ),
        "Content-Type": "application/json"
    }

    # 2. Measure complete request latency

    start = time.perf_counter()

    response = httpx.post(
        URL,
        headers=headers,
        json=payload,
        timeout=30.0,
    )

    elapsed_ms = (
        time.perf_counter() - start
    ) * 1000

    response.raise_for_status()

    data = response.json()


    # 3. Extract provider usage

    usage = data["usage"]

    provider_prompt_tokens = usage[
        "prompt_tokens"
    ]

    completion_tokens = usage[
        "completion_tokens"
    ]

    total_tokens = usage[
        "total_tokens"
    ]

    provider_cost_usd = float(
        usage.get("cost",0)
    )

    # 4. Calculate cost 
    
    # Gemini 2.5 Flash Lite:
    # Input  = $0.10 / 1M
    # Output = $0.40 / 1M


    calculated_cost_usd = calculate_cost(
        provider_prompt_tokens,
        completion_tokens,
        0.10,
        0.40,
    )

    cost_inr = (
        calculated_cost_usd * USD_TO_INR
    )


    # 5. Extract generated text

    generate_text = (
        data["choices"][0]["message"]["content"]
    )

    # 6. Print human-readable report

    print()
    print("===== MODEL METRICS =====")
    print(f"Model: {data['model']}")

    print(
        f"Local Prompt Tokens: "
        f"{local_prompt_tokens} "
    )

    print(
        f"Provider Prompt Tokens: "
        f"{provider_prompt_tokens}"
    )

    print(
        f"Completion Tokens: "
        f"{completion_tokens}"
    )

    print(
        f"Total Tokens: "
        f"{total_tokens}"
    )

    print(
        f"Latency: "
        f"{elapsed_ms:.2f} ms"
    )

    print(
        f"Calculated Cost USD: "
        f"${calculated_cost_usd:.10f}"
    )

    print(
        f"Calculated Cost INR: "
        f"₹{cost_inr:.6f}"
    )

    print(
        f"OpenRouter Reported Cost USD: "
        f"${provider_cost_usd:.10f}"
    )

    # 7. Structured log line

    metrics = {
        "model": data["model"],
        "prompt_tokens": provider_prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "latency_ms": round(elapsed_ms, 2),
        "cost_usd": calculated_cost_usd,
        "cost_inr": cost_inr,
    }

    logger.info(
        "model_call %s",
        json.dumps(metrics),
    )

    # 8. Cost verification


    difference = (
        calculated_cost_usd
        - provider_cost_usd
    )

    print()

    print(
        "Cost difference: "
        f"${difference:.10f}"
    )


if __name__ == "__main__":
    main()