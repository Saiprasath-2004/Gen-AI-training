from models import Incident
from llm_client import call_model
from parser import parse_json
from prompts import built_extraction_prompt

MAX_RETRIES = 1

def validate_response(
    raw_response: str,
) -> Incident:

    data = parse_json(raw_response)
    return Incident.model_validate(data)

def build_retry_prompt(
    original_text: str,
    validation_error: str,
) -> str:

    return f"""

        Your previous response failed validation.

        Validation error:
        <error>
        {validation_error}
        </error>

        Extract the incident information again.

        Return ONLY a valid JSON object with exactly
        these fields:

        severity
        service
        duration_minutes
        customer_impact
        root_cause
        recommended_action

        Use null when a value cannot be determined.

        <incident>
        {original_text}
        </incident>
    """


def extract_incident(
    text: str,
) -> Incident:

    prompt = built_extraction_prompt(text)

    raw_response = call_model(prompt)

    try:

        return validate_response(
            raw_response
        )

    except Exception as  first_error:

        if MAX_RETRIES == 0:
            raise RuntimeError(
                "Extraction failed"
            ) from first_error

        retry_prompt = build_retry_prompt(
            text,
            str(first_error),
        )

        retry_response = call_model(
            retry_prompt
        )

        try:
            return validate_response(
                retry_response
            )

        except Exception as retry_error:
            print(
                f"\n[Attempt 2 Failed]: {retry_error}\nRaw retry response:\n{retry_response}\n"
            )
            raise RuntimeError(
                "Extraction failed after retry"
            ) from retry_error