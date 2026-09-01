from extractor import extract_incident


INCIDENT_TEXT = """
At 10:32 AM the payment service started returning HTTP 500 errors.
Approximately 18% of payment requests failed for 23 minutes.
The issue was caused by a database connection pool exhaustion
after a deployment increased concurrent requests.
Rolling back the deployment restored normal operation.
The team should review connection pool limits before redeploying.
"""


def main() -> None:

    print("=" * 60)
    print("STRUCTURED INCIDENT EXTRACTION")
    print("=" * 60)

    try:
        incident = extract_incident(
            INCIDENT_TEXT
        )

        print()
        print("Extraction successful")
        print()
        print(incident)

        print()
        print("As dictionary:")
        print(
            incident.model_dump()
        )

    except RuntimeError as exc:

        print()
        print("Extraction failed")
        print(exc)


if __name__ == "__main__":
    main()