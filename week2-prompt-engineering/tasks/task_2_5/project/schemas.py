from typing import Any

from pydantic import BaseModel, Field


## Tools arguement Models

class FetchDomainHeadersArgs(BaseModel):
    """Arguments accepted by fetch_domain_headers."""

    domain: str = Field(
        ...,
        description=(
            "Public domain name to inspect, for example "
            "'google.com'. Do not include a path."
        ),
    )


class CalculateAvailabilityScoreArgs(BaseModel):
    """Arguments accepted by calculate_availability_score."""


    status_code: int = Field(
        ...,
        description="HTTP status code returned by the endpoint"
    )

    latency_ms: float = Field(
        ...,
        description="Measured HTTP round-trip latency in milliseconds.",
    )

    has_ssl: bool = Field(
        ...,
        description = "Whether the endpoint is using HTTPS/TLS"
    )


### Tool result models

class FetchDomainHeadersResult(BaseModel):
    """Structured result returned by the network diagnostic tool."""

    domain: str
    status_code: int | None
    latency_ms: float | None
    has_ssl: bool
    server_headers: dict[str, str]
    success: bool
    error: str | None = None

class AvailabilityScoreResult(BaseModel):
    """Structured result returned by the deterministic scoring tool."""

    status_code: int
    latency_ms: float
    has_ssl: bool
    score: float
    status: str
    deductions: list[str]


## JSON schemas exposed to the LLM

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "fetch_domain_headers",
            "description": (
                "Fetch a public HTTP/HTTPS domain and return its HTTP "
                "status code, measured round-trip latency, SSL usage, "
                "and response server headers. Use this when live "
                "network information about a domain is required."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": (
                            "Public domain name such as "
                            "'google.com'"
                        )
                    }
                },
                "required": ["domain"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_availability_score",
            "description": (
                "Calculate a deterministic availability health score "
                "from an HTTP status code, measured latency, and SSL "
                "presence. Use this only after diagnostic values are "
                "available. Do not invent measurements."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "status_code": {
                        "type": "integer",
                        "description": "HTTP response status code.",
                    },
                    "latency_ms": {
                        "type": "number",
                        "description": "Measured latency in milliseconds.",
                    },
                    "has_ssl": {
                        "type": "boolean",
                        "description": "Whether HTTPS/TLS is enabled.",
                    },
                },
                "required": [
                    "status_code",
                    "latency_ms",
                    "has_ssl",
                ],
                "additionalProperties": False,
            },
        },
    },
]