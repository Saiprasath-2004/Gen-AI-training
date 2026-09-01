import json
import re


def extract_json_object(text: str) -> str:
    """
    Extract the first JSON object from model output.
    """

    text = text.strip()

    # Remove Markdown code fences

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    # Locate the JSON Object
    start = text.find("{")

    if start == -1:

        raise ValueError(
            "No JSON object found"
        )

    depth = 0
    in_string = False
    escaped = False

    for index in range(
        start,
        len(text)
    ):
        char = text[index]

        if escaped:
            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

            if depth == 0:
                return text[
                    start: index+1
                ]

    raise ValueError(
        "JSON object is truncated"
    )
def remove_trailing_commas(
    json_text: str,
) -> str:
    """Remove commas immediately before } or ]."""

    return re.sub(
        r",\s*([}\]])",
        r"\1",
        json_text,
    )


def parse_json(text: str) -> dict:
    json_text = extract_json_object(text)

    try:
        return json.loads(json_text)

    except json.JSONDecodeError as first_error:

        repaired_json = remove_trailing_commas(
            json_text
        )

        if repaired_json == json_text:
            raise ValueError(
                f"Invalid JSON: {first_error}"
            ) from first_error

        try:
            return json.loads(repaired_json)

        except json.JSONDecodeError as repair_error:
            raise ValueError(
                f"Invalid JSON after repair: "
                f"{repair_error}"
            ) from repair_error