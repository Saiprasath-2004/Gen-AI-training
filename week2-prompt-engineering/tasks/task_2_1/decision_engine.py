import json
from pathlib import Path


REPORT_FILE = Path(
    "results/decision_report.json"
)

POLICY_FILE = Path(
    "decision_policy.json"
)

OUTPUT_FILE = Path(
    "results/final_decision.json"
)


def load_json(path: Path) -> dict:
    """Load JSON configuration or report."""

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def filter_models(
    report: dict,
    policy: dict,
) -> tuple[dict, dict]:
    """Separate eligible and rejected models."""

    minimum_quality = policy[
        "minimum_quality"
    ]

    maximum_failure_rate = policy[
        "maximum_failure_rate"
    ]

    eligible = {}
    rejected = {}

    for model, metrics in report.items():

        quality = metrics[
            "quality_score"
        ]

        failure_rate = metrics[
            "failure_rate"
        ]

        if (
            quality >= minimum_quality
            and failure_rate <= maximum_failure_rate
        ):
            eligible[model] = metrics
        else:
            rejected[model] = {
                **metrics,
                "rejection_reason": (
                    "Failed minimum quality "
                    "or maximum failure-rate "
                    "requirement."
                ),
            }

    return eligible, rejected

def normalize(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """Normalize a value to the range 0..1."""

    if maximum == minimum:
        return 1.0

    return (
        (value - minimum)
        / (maximum - minimum)
    )


def calculate_scores(
    eligible: dict,
    weights: dict,
) -> dict:
    """Calculate weighted decision scores."""

    if not eligible:
        return {}

    latencies = [
        metrics["avg_latency_ms"]
        for metrics in eligible.values()
    ]

    costs = [
        metrics["avg_cost_usd"] or 0
        for metrics in eligible.values()
    ]

    min_latency = min(latencies)
    max_latency = max(latencies)

    min_cost = min(costs)
    max_cost = max(costs)

    scored = {}

    for model, metrics in eligible.items():

        latency_normalized = normalize(
            metrics["avg_latency_ms"],
            min_latency,
            max_latency,
        )

        cost_normalized = normalize(
            metrics["avg_cost_usd"] or 0,
            min_cost,
            max_cost,
        )

        latency_score = (
            1 - latency_normalized
        )

        cost_score = (
            1 - cost_normalized
        )

        quality_score = metrics[
            "quality_score"
        ]

        final_score = (
            quality_score
            * weights["quality"]
            + latency_score
            * weights["latency"]
            + cost_score
            * weights["cost"]
        )

        scored[model] = {
            **metrics,
            "quality_component": round(
                quality_score
                * weights["quality"],
                4,
            ),
            "latency_score": round(
                latency_score,
                4,
            ),
            "latency_component": round(
                latency_score
                * weights["latency"],
                4,
            ),
            "cost_score": round(
                cost_score,
                4,
            ),
            "cost_component": round(
                cost_score
                * weights["cost"],
                4,
            ),
            "final_score": round(
                final_score,
                4,
            ),
        }

    return scored
def build_decision(
    scored: dict,
    rejected: dict,
) -> dict:
    """Build the final benchmark decision."""

    ranked_models = sorted(
        scored.items(),
        key=lambda item: item[1][
            "final_score"
        ],
        reverse=True,
    )

    ranking = []

    for rank, (model, metrics) in enumerate(
        ranked_models,
        start=1,
    ):
        ranking.append(
            {
                "rank": rank,
                "model": model,
                "provider": metrics[
                    "provider"
                ],
                "deployment": metrics[
                    "deployment"
                ],
                "final_score": metrics[
                    "final_score"
                ],
                "quality": metrics[
                    "quality_score"
                ],
                "failure_rate": metrics[
                    "failure_rate"
                ],
                "avg_latency_ms": metrics[
                    "avg_latency_ms"
                ],
                "avg_cost_usd": metrics[
                    "avg_cost_usd"
                ],
            }
        )

    winner = (
        ranking[0]
        if ranking
        else None
    )

    hosted = [
        item
        for item in ranking
        if item["deployment"] == "hosted"
    ]

    local = [
        item
        for item in ranking
        if item["deployment"] == "local"
    ]

    return {
        "overall_winner": winner,
        "best_hosted": (
            hosted[0]
            if hosted
            else None
        ),
        "best_local": (
            local[0]
            if local
            else None
        ),
        "ranking": ranking,
        "rejected_models": rejected,
    }

def main() -> None:
    """Run the model decision engine."""

    report = load_json(
        REPORT_FILE
    )

    policy = load_json(
        POLICY_FILE
    )

    eligible, rejected = filter_models(
        report,
        policy,
    )

    scored = calculate_scores(
        eligible,
        policy["weights"],
    )

    decision = build_decision(
        scored,
        rejected,
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            decision,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 70)
    print("MODEL DECISION")
    print("=" * 70)

    if decision["overall_winner"]:
        winner = decision[
            "overall_winner"
        ]

        print(
            f"Overall winner: "
            f"{winner['model']}"
        )

        print(
            f"Score: "
            f"{winner['final_score']}"
        )

    print()
    print("Ranking:")

    for item in decision["ranking"]:
        print(
            f"{item['rank']}. "
            f"{item['model']} "
            f"→ {item['final_score']}"
        )

    print()
    print(
        "Rejected models:"
    )

    for model in rejected:
        print(
            f"- {model}"
        )

    print()
    print(
        f"Saved: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()