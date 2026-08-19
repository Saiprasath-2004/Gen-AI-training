import json
from pathlib import Path
from collections import defaultdict


RESULTS_FILE = Path(
    "results/all_model_results.json"
)

EVALUATION_FILE = Path(
    "evaluation.json"
)

OUTPUT_FILE = Path(
    "results/decision_report.json"
)


def load_json(path: Path) -> dict | list:
    """Load JSON data from a file."""

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def calculate_metrics(
    results: list[dict],
    evaluations: list[dict],
) -> dict:
    """Calculate per-model benchmark metrics."""

    grouped_results = defaultdict(list)
    grouped_evaluations = defaultdict(list)

    for result in results:
        grouped_results[
            result["model"]
        ].append(result)

    for evaluation in evaluations:
        grouped_evaluations[
            evaluation["model"]
        ].append(evaluation)

    report = {}

    for model, model_results in grouped_results.items():

        successful_results = [
            result
            for result in model_results
            if result["success"]
        ]

        model_evaluations = (
            grouped_evaluations.get(
                model,
                []
            )
        )

        usable_count = sum(
            evaluation["usable"]
            for evaluation in model_evaluations
        )

        total_evaluations = len(
            model_evaluations
        )

        latency_values = [
            result["latency_ms"]
            for result in successful_results
        ]

        total_cost = sum(
            result.get("cost_usd") or 0
            for result in successful_results
        )

        total_tokens = sum(
            result.get("total_tokens") or 0
            for result in successful_results
        )

        report[model] = {
            "provider": model_results[0][
                "provider"
            ],
            "deployment": model_results[0][
                "deployment"
            ],
            "total_prompts": len(
                model_results
            ),
            "successful_calls": len(
                successful_results
            ),
            "failed_calls": (
                len(model_results)
                - len(successful_results)
            ),
            "failure_rate": round(
                (
                    len(model_results)
                    - len(successful_results)
                )
                / len(model_results),
                4,
            ),
            "avg_latency_ms": round(
                sum(latency_values)
                / len(latency_values),
                2,
            ) if latency_values else None,
            "total_cost_usd": round(
                total_cost,
                8,
            ),
            "avg_cost_usd": round(
                total_cost
                / len(successful_results),
                8,
            ) if successful_results else None,
            "total_tokens": total_tokens,
            "usable_outputs": usable_count,
            "quality_score": round(
                usable_count
                / total_evaluations,
                4,
            ) if total_evaluations else 0,
        }

    return report


def save_report(
    report: dict,
    path: Path,
) -> None:
    """Save the benchmark decision report."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def main() -> None:
    """Analyze the completed model bake-off."""

    results = load_json(
        RESULTS_FILE
    )

    evaluations_data = load_json(
        EVALUATION_FILE
    )

    evaluations = evaluations_data[
        "evaluations"
    ]

    report = calculate_metrics(
        results,
        evaluations,
    )

    save_report(
        report,
        OUTPUT_FILE,
    )

    print(
        "Analysis completed."
    )

    for model, metrics in report.items():
        print()
        print("=" * 70)
        print(model)
        print("=" * 70)
        print(
            f"Quality: "
            f"{metrics['usable_outputs']}/"
            f"{metrics['total_prompts']}"
        )
        print(
            f"Failure rate: "
            f"{metrics['failure_rate']:.1%}"
        )
        print(
            f"Average latency: "
            f"{metrics['avg_latency_ms']} ms"
        )
        print(
            f"Total cost: "
            f"${metrics['total_cost_usd']:.8f}"
        )


if __name__ == "__main__":
    main()