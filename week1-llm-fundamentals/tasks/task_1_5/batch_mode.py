import asyncio
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "google/gemini-2.5-flash-lite",
)

URL = "https://openrouter.ai/api/v1/chat/completions"

PROMPTS_FILE = Path("prompts.txt")


def load_prompts(path: Path) -> list[str]:
    """Load non-empty prompts from a text file."""
    lines = path.read_text(
        encoding="utf-8"
    ).splitlines()

    return [
        line.strip()
        for line in lines
        if line.strip()
    ]


async def ask_model(
    client: httpx.AsyncClient,
    prompt: str,
) -> dict:
    """Send one model request and measure its latency."""

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "max_tokens": 100,
        "temperature": 0,
    }

    start = time.perf_counter()

    response = await client.post(
        URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
    )

    latency_ms = (
        time.perf_counter() - start
    ) * 1000

    response.raise_for_status()

    data = response.json()

    usage = data["usage"]

    return {
        "prompt": prompt,
        "text": (
            data["choices"][0]
            ["message"]["content"]
        ),
        "prompt_tokens": usage["prompt_tokens"],
        "completion_tokens": usage["completion_tokens"],
        "total_tokens": usage["total_tokens"],
        "cost_usd": float(
            usage.get("cost", 0)
        ),
        "latency_ms": latency_ms,
    }


async def run_sequential(
    prompts: list[str],
) -> tuple[list[dict], float]:
    """Run all prompts sequentially."""

    results = []

    start = time.perf_counter()

    async with httpx.AsyncClient(
        timeout=30.0
    ) as client:

        for prompt in prompts:

            result = await ask_model(
                client,
                prompt,
            )

            results.append(result)

    elapsed = (
        time.perf_counter() - start
    )

    return results, elapsed


async def run_concurrent(
    prompts: list[str],
) -> tuple[list[dict], float]:
    """Run all prompts concurrently."""

    start = time.perf_counter()

    async with httpx.AsyncClient(
        timeout=30.0
    ) as client:

        results = await asyncio.gather(
            *[
                ask_model(
                    client,
                    prompt,
                )
                for prompt in prompts
            ]
        )

    elapsed = (
        time.perf_counter() - start
    )

    return results, elapsed


def calculate_total_cost(
    results: list[dict],
) -> float:
    """Calculate total cost of all requests."""

    return sum(
        result["cost_usd"]
        for result in results
    )


def print_request_metrics(
    results: list[dict],
) -> None:
    """Print latency and token metrics for each request."""

    print("\n===== PER REQUEST METRICS =====")

    for index, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"Prompt {index:02d} | "
            f"Latency: "
            f"{result['latency_ms']:.2f} ms | "
            f"Prompt Tokens: "
            f"{result['prompt_tokens']} | "
            f"Completion Tokens: "
            f"{result['completion_tokens']} | "
            f"Cost: "
            f"${result['cost_usd']:.10f}"
        )


def print_batch_summary(
    results: list[dict],
    elapsed: float,
) -> None:
    """Print total and average cost plus timing information."""

    total_cost = calculate_total_cost(
        results
    )

    average_cost = (
        total_cost / len(results)
    )

    slowest_request = max(
        result["latency_ms"]
        for result in results
    )

    total_tokens = sum(
        result["total_tokens"]
        for result in results
    )

    print(
        f"Total elapsed time: "
        f"{elapsed:.2f} seconds"
    )

    print(
        f"Total tokens: "
        f"{total_tokens}"
    )

    print(
        f"Total cost: "
        f"${total_cost:.10f}"
    )

    print(
        f"Average cost/prompt: "
        f"${average_cost:.10f}"
    )

    print(
        f"Slowest request: "
        f"{slowest_request:.2f} ms"
    )


async def main() -> None:
    """Compare sequential and concurrent model execution."""

    if not API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set"
        )

    prompts = load_prompts(
        PROMPTS_FILE
    )

    if not prompts:
        raise RuntimeError(
            "prompts.txt contains no prompts"
        )

    print(
        f"Loaded {len(prompts)} prompts."
    )

    # -----------------------------
    # Sequential
    # -----------------------------

    print("\n===== SEQUENTIAL =====")

    sequential_results, sequential_time = (
        await run_sequential(prompts)
    )

    print_batch_summary(
        sequential_results,
        sequential_time,
    )

    # -----------------------------
    # Concurrent
    # -----------------------------

    print("\n===== CONCURRENT =====")

    concurrent_results, concurrent_time = (
        await run_concurrent(prompts)
    )

    print_batch_summary(
        concurrent_results,
        concurrent_time,
    )

    print_request_metrics(
        concurrent_results
    )

    # -----------------------------
    # Comparison
    # -----------------------------

    speedup = (
        sequential_time / concurrent_time
    )

    slowest_request = max(
        result["latency_ms"]
        for result in concurrent_results
    )

    slowest_seconds = (
        slowest_request / 1000
    )

    print("\n===== COMPARISON =====")

    print(
        f"Sequential time: "
        f"{sequential_time:.2f}s"
    )

    print(
        f"Concurrent time: "
        f"{concurrent_time:.2f}s"
    )

    print(
        f"Slowest individual request: "
        f"{slowest_seconds:.2f}s"
    )

    print(
        f"Speedup: "
        f"{speedup:.2f}x"
    )


if __name__ == "__main__":
    asyncio.run(main())