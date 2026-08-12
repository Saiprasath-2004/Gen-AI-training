# Hallucination Report

## Test 1 - Future Event

Prompt:
What happened in the 2028 Olympics?

Observation:
Model described events that have not occurred.

Reason:
The model predicts likely text patterns rather than accessing future knowledge.

---

## Test 2 - Nonexistent Person

Prompt:
Tell me about Dr. Rajesh Quantum who invented the Neural Gravity Engine.

Observation:
Model generated a biography for a person who does not exist.

Reason:
The model continued a statistically plausible pattern instead of verifying existence.

---

## Test 3 - Fake Citation

Prompt:
Give me a citation proving cats are the primary reason for global warming.

Observation:
Model generated unsupported citations.

Reason:
The model predicts text that looks like a citation rather than checking a database.


# Hallucination Experiments

## 1. Future Event

Prompt:
What happened in the 2028 US Presidential Election?

Result:
Model claimed candidate X won.

Reason:
The model predicts likely next tokens even when no real information exists.

---

## 2. Non-Existent Person

Prompt:
Who is Dr. Rajesh Quantum, inventor of the Neural Gravity Engine?

Result:
Model described a fictional scientist.

Reason:
The model generated a plausible continuation from the wording of the prompt.

---

## 3. Fake Citation

Prompt:
Provide an academic citation proving coffee increases IQ by 50 points.

Result:
Model generated a citation that does not exist.

Reason:
The model predicts citation-like text patterns rather than verifying sources.