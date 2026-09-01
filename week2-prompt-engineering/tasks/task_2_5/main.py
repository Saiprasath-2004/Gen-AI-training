from pathlib import Path

from agent import run_agent


PROMPTS_DIR = Path("prompts")


def load_prompt(filename: str) -> str:
    """Load a user scenario from the prompts directory."""

    path = PROMPTS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {path}"
        )

    return path.read_text(
        encoding="utf-8"
    ).strip()


def run_scenario(
    title: str,
    filename: str,
) -> None:

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    prompt = load_prompt(filename)

    print()
    print("USER:")
    print(prompt)

    try:
        answer = run_agent(prompt)

        print()
        print("ASSISTANT:")
        print(answer)

    except Exception as exc:
        print()
        print(
            f"ERROR: {type(exc).__name__}: {exc}"
        )


def main() -> None:

    run_scenario(
        "TEST 1 — DRONE FILMING",
        "drone_filming.txt",
    )

    run_scenario(
        "TEST 2 — CRICKET",
        "cricket.txt",
    )

    run_scenario(
        "TEST 3 — MOUNTAIN BIKING",
        "mountain_biking.txt",
    )

    run_scenario(
        "TEST 4 — NO WEATHER REQUIRED",
        "general_question.txt",
    )


if __name__ == "__main__":
    main()