from parser import parse_json

VALID_JSON = """
    {
        "severity": "high",
        "service": "payment service",
        "duration_minutes": 23,
        "customer_impact": "Approximately 18% of payment requests failed",
        "root_cause": "Database connection pool exhaustion",
        "recommended_action": "Review connection pool limits before redeploying"
    }
"""

MARKDOWN_JSON = """
    ```json
    {
        "severity": "high",
        "service": "payment service",
        "duration_minutes": 23,
        "customer_impact": "Approximately 18% of payment requests failed",
        "root_cause": "Database connection pool exhaustion",
        "recommended_action": "Review connection pool limits before redeploying"
    }

"""

PROSE_BEFORE_JSON = """
    Here is the extracted incident information:

    {
    "severity": "high",
    "service": "payment service",
    "duration_minutes": 23,
    "customer_impact": "Approximately 18% of payment requests failed",
    "root_cause": "Database connection pool exhaustion",
    "recommended_action": "Review connection pool limits before redeploying"
    }
"""


TRAILING_COMMA_JSON = """
    {
    "severity": "high",
    "service": "payment service",
    "duration_minutes": 23,
    "customer_impact": "Approximately 18% of payment requests failed",
    "root_cause": "Database connection pool exhaustion",
    "recommended_action": "Review connection pool limits before redeploying",
    }
"""

TRUNCATED_JSON = """
{
"severity": "high",
"service": "payment service",
"duration_minutes": 23,
"customer_impact": "Approximately 18% of payment requests failed",
"root_cause": "Database connection pool exhaustion",
"recommended_action": "Review connection pool limits before
"""

def run_test(
name: str,
raw_response: str,
should_succeed: bool,
) -> None:
        print()
        print("=" * 60)
        print(name)
        print("=" * 60)

        try:
            result = parse_json(raw_response)

            if should_succeed:
                print("PASS")
                print("Parsed successfully:")
                print(result)
            else:
                print("FAIL")
                print(
                    "Expected parser to reject malformed JSON, "
                    "but it accepted it."
                )

        except Exception as exc:
            if should_succeed:
                print("FAIL")
                print(f"Expected parsing to succeed, but got: {exc}")
            else:
                print("PASS")
                print("Parser correctly rejected malformed response:")
                print(exc)

def main() -> None:
    run_test(
    name="VALID JSON",
    raw_response=VALID_JSON,
    should_succeed=True,
    )

    run_test(
        name="MARKDOWN FENCES",
        raw_response=MARKDOWN_JSON,
        should_succeed=True,
    )

    run_test(
        name="PROSE BEFORE JSON",
        raw_response=PROSE_BEFORE_JSON,
        should_succeed=True,
    )

    run_test(
        name="TRAILING COMMA",
        raw_response=TRAILING_COMMA_JSON,
        should_succeed=True,
    )

    run_test(
        name="TRUNCATED MID-OBJECT",
        raw_response=TRUNCATED_JSON,
        should_succeed=False,
    )

if __name__ == "__main__":
    main()