from agent_loop import run_agent
from tools import diagnose_domain_without_llm

def run_normal_agent_test() -> None:

    print("=" * 70)
    print("TEST RUN 1 — LIVE DOMAIN DIAGNOSTIC")
    print("=" * 70)

    request = """
    Diagnose google.com.

    Fetch its live HTTP status, latency, SSL status,
    and server headers. Then calculate its availability
    score and explain the result.
    """

    result = run_agent(
        user_request=request,
        max_iterations=5,
    )

    print()
    print("FINAL AGENT RESPONSE: ")
    print(result)

def run_iterations_cap_test() -> None:

    print()
    print("=" * 70)
    print("TEST RUN 2 — ITERATION SAFETY CAP")
    print("=" * 70)

    try:

        run_agent(
            user_request=(
                "Diagnose google.com and calculate "
                "its availability score."
            ),
            max_iterations=1,
        )

    except RuntimeError as exc:

        print()
        print("SAFETY CAP TRIGGERED:")
        print(exc)

def run_non_llm_test() -> None:

    print()
    print("=" * 70)
    print("TEST RUN 3 — NO LLM PIPELINE")
    print("=" * 70)

    result = diagnose_domain_without_llm(
        "google.com"
    )

    print()
    print("DETERMINISTIC PIPELINE RESULT:")
    print(result)

def main() -> None:

    run_normal_agent_test()
    run_iterations_cap_test()
    run_non_llm_test()

if __name__ == "__main__":
    main()