# Prompt Iteration Log — Incident Extraction

## Experiment Setup

- Model: google/gemini-3.5-flash-lite
- Same incident input for all versions
- Temperature: 0
- Max tokens: 500
- Only the prompt was changed between versions

---

## V1 — Baseline

### Change
Initial prompt with role, extraction task, and incident text.

### Expected
Extract the six requested fields.

### Actual
The model extracted all requested information, but returned prose and inferred severity as "High / Critical".

### Result
Usable for human reading, but not reliable for machine processing.

- Latency: 2165.28 ms
- Tokens: 234
- Cost: $0.00032540

---

## V2 — Explicit JSON Contract

### Change
Added an explicit requirement to return a JSON object with exactly six fields.

### Expected
Improve machine-readable output.

### Actual
The model returned the requested JSON structure, but wrapped it in Markdown code fences.

### Result
Better than V1, but still requires response cleanup before parsing.

- Latency: 3619.18 ms
- Tokens: 229
- Cost: $0.00028210

---

## V3 — Delimiters

### Change
Wrapped the incident data inside `<incident>` tags.

### Expected
Create a clearer boundary between instructions and source data.

### Actual
The model returned a clean JSON structure and correctly separated the incident data from the instructions.

### Result
Best result so far for this experiment.

- Latency: 1121.60 ms
- Tokens: 225
- Cost: $0.00026330

---

## V4 — Few-shot Example

### Change
Added one input/output example before the actual incident.

### Expected
Improve consistency by showing the model the desired behavior.

### Actual
The model returned a clean JSON object with the expected fields.

### Result
Successful, but the example increased token usage compared with V3.

- Latency: 1053.41 ms
- Tokens: 315
- Cost: $0.00029250

---

## V5 — Over-restrictive Constraint

### Change
Added:

"Only use information explicitly stated word-for-word in the incident. Do not infer anything."

### Expected
Make the extraction more conservative.

### Actual
The model returned `severity: null`, because the incident never explicitly stated a severity level.

### Result
The prompt became worse for this workload because the restriction prevented useful interpretation.

- Latency: 1438.47 ms
- Tokens: 337
- Cost: $0.00030350

### Why this version was intentionally retained

This demonstrates that adding more constraints does not automatically improve a prompt. An overly restrictive instruction can reduce the usefulness of otherwise reasonable model inference.

