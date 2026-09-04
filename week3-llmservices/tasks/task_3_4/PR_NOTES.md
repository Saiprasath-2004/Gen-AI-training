# PR: System Prompt Guardrail & Routing Improvements

## Evaluation Evidence

We evaluated the system prompt changes against our 25-case Golden Dataset (`golden_dataset.json`).

| Metric | Prompt v1 (Baseline) | Prompt v2 (Improved) |
| :--- | :--- | :--- |
| **Pass Rate** | **68.0%** (17/25) | **96.0%** (24/25) |
| **Refusal Compliance (3 cases)** | 33.3% (1/3) | 100.0% (3/3) |
| **Tool Routing Accuracy** | 70.0% (7/10) | 100.0% (10/10) |

### Key Improvements in Prompt v2:
1. **Refusal Guardrails**: Prompt v1 attempted to answer or suggest commands for destructive queries (`DROP TABLE`). Prompt v2 explicitly denies write operations.
2. **Tool Selection**: Prompt v2 explicitly instructs the model when to invoke `get_table_schema` vs `query_postgres_logs`, eliminating false-negative tool skips.

### Unit Tests Benchmark:
- Ran `pytest test_mocked_chain.py`
- Result: **4 passed in 0.18s** (No network calls, fully mocked).