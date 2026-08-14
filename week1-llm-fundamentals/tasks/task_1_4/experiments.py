import json
import time
import os
from pathlib import Path

import tiktoken
import httpx
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "liquid/lfm-2.5-2.6b:free",
)

URL = "https://openrouter.ai/api/v1/chat/completions"

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)


def call_model(
    prompt: str,
    temperature: float,
    max_tokens: int = 200,
    retries: int = 3,
) -> dict | None:
    """Call OpenRouter with retry handling."""

    if not API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set"
        )

    payload = {
        "model": MODEL,
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
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30.0,
            )

            if response.status_code == 429:

                retry_after = response.headers.get(
                    "Retry-After"
                )

                if retry_after is not None:

                    wait_seconds = float(
                        retry_after
                    )

                else:

                    wait_seconds = 2 ** attempt

                print(
                    f"Rate limited (429). "
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

    print(
        "Request failed after retries"
    )
    return None 

def call_model_with_history(
    history: list[dict[str, str]],
) -> dict:
    """Send the complete conversation history."""

    if not API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set"
        )

    payload = {
        "model": MODEL,
        "messages": history,
        "temperature": 0,
        "max_tokens": 50,
    }

    response = httpx.post(
        URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30.0,
    )

    response.raise_for_status()

    return response.json()


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

def run_temperature_experiment(
    prompt: str,
    temperature: float,
    runs: int = 10,
) -> list[dict]:
    """Run the same prompt repeatedly at one temperature."""

    results = []

    for run_number in range(1, runs + 1):

        data = call_model(
            prompt=prompt,
            temperature=temperature,
            max_tokens=200,
        )

        

        text = extract_text(data)

        result = {
            "run": run_number,
            "temperature": temperature,
            "text": text,
        }

        results.append(result)

        print(
            f"\n--- Temperature {temperature} "
            f"Run {run_number} ---"
        )

        print(text)

    return results


def save_results(
    filename: str,
    results: list[dict],
) -> None:
    """Save experiment results as JSON."""

    path = RESULTS_DIR / filename

    path.write_text(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def run_max_tokens_experiment(
    prompt: str,
) -> None:
    """Run a request with an intentionally tiny output limit."""

    data = call_model(
        prompt=prompt,
        temperature=0,
        max_tokens=5,
    )

    print(data)
    text = extract_text(data)

    finish_reason = data["choices"][0][
        "finish_reason"
    ]

    print("\n===== MAX TOKENS EXPERIMENT =====")

    print("Generated text:")
    print(text)

    print()
    print("Finish reason:")
    print(finish_reason)

        
def count_tokens(text: str) -> int:
    """Count tokens using the local tokenizer."""
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def build_history_chunk(
    target_tokens: int,
) -> str:
    """Build one large user-message chunk efficiently."""

    chunk = (
        "This is a context-window experiment. "
        "We are deliberately creating a long "
        "conversation history so that the total "
        "number of tokens eventually exceeds the "
        "model's context capacity. "
    )

    encoding = tiktoken.get_encoding(
        "cl100k_base"
    )

    chunk_token_count = len(
        encoding.encode(chunk)
    )

    repeats = (
        target_tokens // chunk_token_count
    ) + 1

    return chunk * repeats


def run_history_context_experiments() -> None:
    """
    Gradually grow conversation history until the
    provider rejects the request because the
    context window is exceeded.
    """

    # Example:
    # 131072 tokens -> approximately 128K.
    context_limit = 131_072

    # How much new text we add to each user message.
    # This keeps the number of requests reasonable.
    tokens_per_user_message = 10_000

    history: list[dict[str,str]] = []

    print()
    print(
        "===== CONTEXT HISTORY EXPERIMENT ====="
    )

    print(
        f"Target context limit: "
        f"{context_limit}"
    )

    print(
        f"Approximate new tokens per turn: "
        f"{tokens_per_user_message}"
    )

    turn = 1

    while True:

        #Create  the next User message

        user_content = build_history_chunk(
            tokens_per_user_message
        )

        history.append(
            {
                "role": "user",
                "content": user_content,
            }
        )

        print()
        print(
            f"--- Turn {turn} ---"
        )

        print(
            f"Messages in history: "
            f"{len(history)}"
        )

        # 2. Send entire conversation history

        try:

            data = call_model_with_history(
                history
            )

            usage = data.get(
                "usage",
                {}
            )

            provider_prompt_tokens = usage.get(
                "prompt_tokens"
            )

            print(
                "Provider prompt tokens: "
                f"{provider_prompt_tokens}"
            )

            text = extract_text(data)

            print(
                "Assistant response:"
            )

            print(text[:300])

            # Add assistant response to history
            history.append(
                {
                    "role": "assistant",
                    'content': text,
                }
            )

            turn +=1

        except httpx.HTTPStatusError as exc:

            print()
            print(
                "===== CONTEXT WINDOW REACHED ====="
            )

            print(
                f"HTTP status: "
                f"{exc.response.status_code}"
            )

            print()
            print(
                "Provider response:"
            )

            print(
                exc.response.text
            )


            print()
            print(
                f"Conversation stopped at turn "
                f"{turn}."
            )

            print(
                "The application handled the "
                "error without crashing."
            )

            break

        except httpx.TimeoutException:

            print()
            print(
                "Context experiment timed out."
            )

            print(
                "The application stopped safely."
            )

            break

        except httpx.RequestError as exc:

            print()
            print(
                "Network error:"
            )
            print(
                "The application stopped safely."
            )

            break

        except Exception as exc:

            print()
            print(
                "Unexpected error:"
            )

            print(str(exc))

            print(
                "The application stopped safely."
            )

            break

def main() -> None:
    """Run all Task 1.4 experiments."""

    prompt = (
        "Explain why Python is useful for backend "
        "development in five sentences."
    )

    print("===== TEMPERATURE 0 =====")

    temperature_0_results = (
        run_temperature_experiment(
            prompt,
            temperature=0,
            runs=10,
        )
    )

    save_results(
        "temperature_0.json",
        temperature_0_results,
    )

    print("\n===== TEMPERATURE 1.0 =====")

    temperature_1_results = (
        run_temperature_experiment(
            prompt,
            temperature=1.0,
            runs=10,
        )
    )

    save_results(
        "temperature_1.json",
        temperature_1_results,
    )

    run_max_tokens_experiment(
        "Explain how a transformer works in detail."
    )

    run_history_context_experiments()



if __name__ == "__main__":
    main()