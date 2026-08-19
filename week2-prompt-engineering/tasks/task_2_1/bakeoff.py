import os
import json
from pathlib import Path
import time
import re
import httpx

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise RuntimeError("OPENROUTER_API_KEY is not set")

URL = "https://openrouter.ai/api/v1/chat/completions"
OLLAMA_URL = "http://localhost:11434/api/chat"


RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)


def load_prompts(
    filename: str = "prompts.txt",
) -> dict[str, str]:
    """Load benchmark prompts from a tagged text file."""

    path = Path(filename)

    if not path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {path}"
        )

    text = path.read_text(
        encoding="utf-8"
    ).strip()

    pattern = r"\[(P\d+)\]\s*(.*?)(?=\n\[P\d+\]|\Z)"

    matches = re.findall(
        pattern,
        text,
        flags=re.DOTALL,
    )

    prompts = {
        prompt_id: prompt.strip()
        for prompt_id, prompt in matches
    }

    if not prompts:
        raise ValueError(
            "No prompts found in prompts.txt"
        )

    return prompts

def load_models(filename: str = "models.json") -> list[str]:

    """Load hosted model and local model IDs from the benchmark configurations."""

    path = Path(filename)

    if not path.exists():
        raise FileNotFoundError(
            f"Model configuration not found: {path}"
        )

    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    hosted_models = data.get("hosted_models")
    local_models = data.get("local_models")

    if not isinstance(hosted_models, list) :
        raise ValueError(
            "'hosted_models' must be a list"
        )

    if not isinstance(local_models, list) :
            raise ValueError(
                "'local_models' must be a list"
            )

    return {
        "hosted_models": hosted_models,
        "local_models": local_models,
    }


def call_model(
    model: str,
    prompt: str,
    temperature: float = 0,
    max_tokens: int = 500,
    retries: int = 3,
) -> dict | None:
    """Call OpenRouter and return the raw response"""

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set"
        )

   
    payload = {
        "model" : model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens, 
    }


    for attempt in range(retries):
        try:
            response = httpx.post(
                URL,
                headers = {
                    "Authorization" : f"Bearer {api_key}",
                    "Content-Type" : "application/json",
                },
                json = payload,
                timeout = 30.0,
            )

            if response.status_code == 429:
                retry_after = response.headers.get(
                    "Retry-After"
                )

                if retry_after is not None:
                    wait_seconds = float(retry_after)
                else:
                    wait_seconds = 2 ** attempt

                print(
                    f"Rate limited(429). "
                    f"Waiting {wait_seconds:.1f}s..."
                )

                time.sleep(wait_seconds)
                continue
            response.raise_for_status()

            return response.json()

        except httpx.TimeoutException:
            print(
                f"Timeout on attempt "
                f"{attempt + 1}/{retries}"
            )

            if attempt < retries - 1:
                time.sleep(2 ** attempt)

        except httpx.HTTPStatusError as exc:
            print(
                f"HTTP error "
                f"{exc.response.status_code}: "
                f"{exc.response.text}"
            )


            return None

    print("Request failed after retries")
    return None 

def call_ollama_model(
    model: str,
    prompt: str,
    temperature: float = 0, 
) -> dict | None:
    """Call a locally running  ollama model."""

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream" : False,
        "options" : {
            "temperature": temperature,
        },
    }

    try: 

        response = httpx.post(
            OLLAMA_URL,
            json=payload,
            timeout= 120.0
        )

        response.raise_for_status()
        return response.json()

    except httpx.TimeoutException:
        print(
            f"ollama timeout for model: {model}"
        )

    except httpx.HTTPStatusError as exc:
        print(
            f"Ollama HTTP error "
            f"{exc.response.status_code}: "
            f"{exc.response.text}"
        )

    except httpx.RequestError as exc:
        print(
            f"Ollama connection error: {exc}"
        )

    return None

def extract_text(data: dict) -> str:
    """Extract generated content from an OpenRouter response."""

    choice = data.get(
        "choices",
        [{}]
    )[0]

    message = choice.get(
        "message",
        {},
    )

    content = message.get(
        "content"
    )

    if content:
        return content

    reasoning = message.get(
        "reasoning",
        
    )

    if reasoning:
        return reasoning

    return ""

def extract_ollama_result(
    data: dict,
    model: str,
    prompt_id: str,
    latency_ms: float,
) -> dict:
    """Convert an Ollama response to our benchmark format."""

    prompt_tokens = data.get(
        "prompt_eval_count",
        0,
    )

    completion_tokens = data.get(
        "eval_count",
        0,
    )

    total_tokens = (
        prompt_tokens + completion_tokens
    )

    return {
        "model": model,
        "provider": "ollama",
        "deployment": "local",
        "prompt_id": prompt_id,
        "success": True,
        "latency_ms": round(
            latency_ms,
            2,
        ),
        "response": data.get(
            "message",
            {},
        ).get(
            "content",
            "",
        ),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cost_usd": 0.0,
        "finish_reason": data.get(
            "done_reason"
        ),
        "ollama_metrics": {
            "total_duration_ms": round(
                data.get(
                    "total_duration",
                    0,
                ) / 1_000_000,
                2,
            ),
            "load_duration_ms": round(
                data.get(
                    "load_duration",
                    0,
                ) / 1_000_000,
                2,
            ),
            "prompt_eval_duration_ms": round(
                data.get(
                    "prompt_eval_duration",
                    0,
                ) / 1_000_000,
                2,
            ),
            "eval_duration_ms": round(
                data.get(
                    "eval_duration",
                    0,
                ) / 1_000_000,
                2,
            ),
        },
    }

def run_benchmarks(
    models: list[str],
    prompts: dict[str, str],
) -> list[dict]:

    """Run every benchmark prompt against every model."""

    results = []

    for model in models:
        print()
        print("=" * 70)
        print(f"MODEL: {model}")
        print("=" * 70)

        for prompt_id , prompt in prompts.items():
            print()
            print(
                f"Running {prompt_id}..."
            )

            start = time.perf_counter()

            data = call_model(
                model = model,
                prompt= prompt
            )

            latency_ms = (
                time.perf_counter() - start
            ) * 1000

            if data is None:
                results.append(
                    {
                        "model": model,
                        "prompt_id": prompt_id,
                        "success": False,
                        "latency_ms": round(
                            latency_ms,
                            2
                        ),
                        "response": None,
                    }
                )

                print(
                    f"{prompt_id}: FAILED"
                )

                continue

            usage = data.get("usage", {})

            result = {
                "model": model,
                "provider": "openrouter",
                "deployment": "hosted",
                "prompt_id": prompt_id,
                "success": True,
                "latency_ms": round(
                    latency_ms,
                    2,
                ),
                "response": extract_text(data),
                "prompt_tokens": usage.get(
                    "prompt_tokens"
                ),
                "completion_tokens": usage.get(
                    "completion_tokens"
                ),
                "total_tokens": usage.get(
                    "total_tokens"
                ),
                "cost_usd": usage.get(
                    "cost"
                ),
                "finish_reason": (
                    data["choices"][0]
                    .get("finish_reason")
                ),

            }

            results.append(result)

            print(
                f"{prompt_id}: "
                f"{latency_ms:.2f} ms |"
                f"{usage.get('total_tokens')} tokens | "
                f"${usage.get('cost', 0):.8f}"
            )

    return results

def run_local_benchmarks(
    models: list[str],
    prompts: dict[str, str],
) -> list[dict]:
    """Run benchmark prompts against local Ollama models."""

    results = []

    for model in models:
        print()
        print("=" * 70)
        print(f"LOCAL MODEL: {model}")
        print("=" * 70)

        for prompt_id, prompt in prompts.items():
            print()
            print(
                f"Running {prompt_id}..."
            )

            start = time.perf_counter()

            data = call_ollama_model(
                model=model,
                prompt=prompt,
            )

            latency_ms = (
                time.perf_counter() - start
            ) * 1000

            if data is None:
                results.append(
                    {
                        "model": model,
                        "provider": "ollama",
                        "deployment": "local",
                        "prompt_id": prompt_id,
                        "success": False,
                        "latency_ms": round(
                            latency_ms,
                            2,
                        ),
                        "response": None,
                    }
                )

                print(
                    f"{prompt_id}: FAILED"
                )

                continue

            result = extract_ollama_result(
                data=data,
                model=model,
                prompt_id=prompt_id,
                latency_ms=latency_ms,
            )

            results.append(result)

            print(
                f"{prompt_id}: "
                f"{latency_ms:.2f} ms | "
                f"{result['total_tokens']} tokens"
            )

    return results

def save_results(
    filename: str,
    results: list[dict],
) -> None:

    """Save experiments results as json"""

    path = RESULTS_DIR / filename

    path.write_text(
            json.dumps(
                results,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

def main() -> None:
    """Run the Task 2.1 model bake-off."""

    models = load_models()
    prompts = load_prompts()

    hosted_models = models["hosted_models"]
    local_models = models["local_models"]

    print(
        f"Hosted models: {len(hosted_models)}"
    )

    print(
        f"Local models: {len(local_models)}"
    )

    print(
        f"Prompts: {len(prompts)}"
    )

    print(
        f"Total evaluations: "
        f"{(
            len(hosted_models)
            + len(local_models)
        ) * len(prompts)}"
    )

    hosted_results = run_benchmarks(
        models=hosted_models,
        prompts=prompts,
    )

    local_results = run_local_benchmarks(
        models=local_models,
        prompts=prompts,
    )

    results = (
        hosted_results
        + local_results
    )

    save_results(
        "all_model_results.json",
        results,
    )

    print()
    print(
        f"Completed {len(results)} evaluations."
    )


if __name__ == "__main__":
    main()