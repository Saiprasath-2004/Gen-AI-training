# Task 2.1 — Model Bake-off

## Objective

Compare hosted and local LLMs using the same five realistic prompts and select a model based on measured quality, latency, cost, and reliability.

## Models Tested

### Hosted — OpenRouter

- google/gemini-3.5-flash-lite
- openai/gpt-oss-20b
- meta-llama/llama-3.3-70b-instruct
- nvidia/nemotron-3-nano-30b-a3b

### Local — Ollama

- gemma3:4b
- qwen3:4b

## Benchmark

5 prompts were tested covering:

- Information extraction
- Expense classification
- Budget reasoning
- Summarization
- Structured JSON extraction

Total evaluations:

30

## Results

| Model | Quality | Avg Latency | Total Cost | Decision |
|---|---:|---:|---:|---|
| Gemini 3.5 Flash Lite | 5/5 | 1711.98 ms | $0.00171730 | Recommended |
| Llama 3.3 70B | 5/5 | 5149.80 ms | $0.00037394 | Alternative |
| GPT-OSS 20B | 5/5 | 5375.38 ms | $0.00024287 | Cost alternative |
| Nemotron 30B | 4/5 | 1658.15 ms | $0.00036960 | Rejected |
| Gemma 3 4B | 2/5 | 18131.06 ms | $0 | Rejected |
| Qwen 3 4B | 3/5 | 84309.53 ms | $0 | Rejected |

## Failed / Problematic Prompts

- Gemini: None
- Llama: None
- GPT-OSS: P3/P4 grounding issues
- Nemotron: P1 truncation; P3/P4 grounding issues
- Gemma: P2, P4 and P5 issues
- Qwen: P1 and P5 timeouts; P4 grounding issue

## Recommendation

For the five workloads tested, Gemini 3.5 Flash Lite is the recommended model because it achieved 5/5 usable outputs with 0% request failure while averaging 1.71 seconds per request. Llama 3.3 70B also achieved 5/5 quality but averaged 5.15 seconds, while GPT-OSS 20B achieved the same 5/5 quality at the lowest hosted cost of $0.000243 for the five-call benchmark but averaged 5.38 seconds. Nemotron was faster at 1.66 seconds but achieved only 4/5 usable outputs and therefore failed the reliability requirement. The local Gemma 3 4B and Qwen 3 4B models incurred no direct API cost, but achieved only 2/5 and 3/5 usable outputs respectively, with Qwen also experiencing a 40% request failure rate. Therefore, Gemini provides the strongest quality-latency trade-off for this benchmark, while GPT-OSS is the stronger alternative when minimizing API cost is more important than latency.

## Conclusion

Task 2.1 is complete.

The benchmark demonstrates that model selection should be based on measured workload-specific quality, latency, cost, and reliability rather than model reputation alone.