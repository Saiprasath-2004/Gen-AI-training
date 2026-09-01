import time
from urllib.parse import urlparse

import httpx

from schemas import(
    AvailabilityScoreResult,
    FetchDomainHeadersResult,
)

HTTP_TIMEOUT = httpx.Timeout(
    connect=5.0,
    read=10.0,
    write=10.0,
    pool=5.0,
)

def normalize_domain(domain: str) -> str:

    """
    Normalize a user/model-provided domain into a safe hostname.

    Examples:
        google.com       -> google.com
        https://google.com -> google.com
    """

    domain = domain.strip()

    if not domain: 
        raise ValueError(
            "Domain cannot be empty."
        )

    if "://" not in domain:
        domain = f"https://{domain}"

    parsed = urlparse(domain)

    if not parsed.hostname:
        raise ValueError(
            "Invalid domain."
        )

    if parsed.path not in ("","/"):
        raise ValueError(
            "Only a domain is allowed; paths are not supported."
        )

    return parsed.hostname

def fetch_domain_headers(
    domain: str,
) -> FetchDomainHeadersResult:

    """
    Perform a live HTTP request and collect diagnostic information.

    The latency measurement covers the actual HTTP request execution.
    """

    hostname = normalize_domain(domain)

    url = f"https://{hostname}"

    start = time.perf_counter()

    try:

        with httpx.Client(
            timeout=HTTP_TIMEOUT,
            follow_redirects=True,
        ) as client:

            response = client.get(url)

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        server_headers ={
            key: value
            for key, value in response.headers.items()
            if key.lower() == "server"
        }

        return FetchDomainHeadersResult(
            domain=hostname,
            status_code=response.status_code,
            latency_ms=round(
                latency_ms,
                2,
            ),
            has_ssl=response.url.scheme.lower() == "https",
            server_headers=server_headers,
            success=True,
        )

    except httpx.HTTPError as exc:

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        return FetchDomainHeadersResult(
            domain=hostname,
            status_code=None,
            latency_ms=round(
                latency_ms,
                2
            ),
            has_ssl=True,
            server_headers={},
            error=str(exc),
        )


def calculate_availability_score(
    status_code: int,
    latency_ms: float,
    has_ssl: bool,
) -> AvailabilityScoreResult:

    """
    Calculate a deterministic availability score.

    Scoring policy:

    Start at 100.

    HTTP status:
        200       -> 0 deduction
        2xx/3xx   -> 5 deduction
        4xx       -> 25 deduction
        5xx       -> 50 deduction
        other     -> 30 deduction

    Latency:
        <= 300ms  -> 0
        <= 1000ms -> 10
        > 1000ms  -> 25

    SSL:
        HTTPS     -> 0
        HTTP      -> 20

    Final score is clamped to [0, 100].
    """

    if latency_ms < 0:
        raise ValueError(
            "latency_ms cannot be negative."
        )

    score = 100.0
    deductions: list[str] = []

    # HTTP status deductions
    if status_code == 200:
        pass

    elif 200 <= status_code < 400:
        score -= 5
        deductions.append(
            "Non-200 successful/redirect status: -5"
        )

    elif 400 <= status_code < 500:
        score -= 25
        deductions.append(
            "4xx client error: -25"
        )   

    elif 500 <= status_code < 600:
        score -= 50
        deductions.append(
            "5xx server error: -50"
        )

    else:
        score -= 30
        deductions.append(
            "Unexpected HTTP status: -30"
        )

    # Latency deduction.
    if latency_ms > 1000:
        score -= 25
        deductions.append(
            "Latency above 1000ms: -25"
        )

    elif latency_ms > 300:
        score -= 10
        deductions.append(
            "Latency above 300ms: -10"
        )

    # SSL deduction.
    if not has_ssl:
        score -= 20
        deductions.append(
            "SSL/TLS not enabled: -20"
        )

    score = max(
        0.0,
        min(100.0, score),
    )

    if score >= 90:
        status = "healthy"

    elif score >= 70:
        status = "degraded"

    elif score >= 40:
        status = "unhealthy"

    else:
        status = "critical"

    return AvailabilityScoreResult(
        status_code=status_code,
        latency_ms=latency_ms,
        has_ssl=has_ssl,
        score=score,
        status=status,
        deductions=deductions,
    )

# Non-LLM production pipeline

def diagnose_domain_without_llm(
    domain: str,
) -> dict:
    """
    Run the diagnostic workflow without an LLM.

    This is intentionally deterministic.
    """

    diagnostics = fetch_domain_headers(
        domain
    )

    if not diagnostics.success:
        return {
            "domain": domain,
            "success": False,
            "error": diagnostics.error,
        }

    score = calculate_availability_score(
        status_code=diagnostics.status_code,
        latency_ms=diagnostics.latency_ms,
        has_ssl=diagnostics.has_ssl,
    )

    return {
        "diagnostics": diagnostics.model_dump(),
        "availability": score.model_dump(),
    }