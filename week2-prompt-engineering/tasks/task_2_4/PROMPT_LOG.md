# Task 2.4 — Structured Extraction Notes

## Experiment 1 — Conservative Severity

### Model

`meta-llama/llama-3.3-70b-instruct`

### Purpose

Test whether the model can extract an incident into a validated structured object when severity is not explicitly stated.

---

### Prompt

```text
You are a production incident extraction system.

Extract information from the incident report.

Return ONLY a JSON object with these exact fields:
- severity
- service
- duration_minutes
- customer_impact
- root_cause
- recommended_actions

Rules:
1. Use null when a field's value cannot be determined or inferred from the text.
2. Ensure duration_minutes is an integer or null.

<incident>
At 10:32 AM the payment service started returning HTTP 500 errors.
Approximately 18% of payment requests failed for 23 minutes.
The issue was caused by a database connection pool exhaustion
after a deployment increased concurrent requests.
Rolling back the deployment restored normal operation.
The team should review connection pool limits before redeploying.
</incident>
```

### Actual LLM Response

```TEXT
{
  "severity": null,
  "service": "payment service",
  "duration_minutes": 23,
  "customer_impact": "18% of payment requests failed",
  "root_cause": "database connection pool exhaustion",
  "recommended_actions": "review connection pool limits before redeploying"
}
```

### Parsed / Validated Result

```TEXT
severity=None
service='payment service'
duration_minutes=23
customer_impact='18% of payment requests failed'
root_cause='database connection pool exhaustion'
recommended_actions='review connection pool limits before redeploying'

```

### Observation

The model returned severity = null.

This happened because the incident did not explicitly state a severity level and the prompt instructed the model to use null when the value could not be determined or inferred.

## Experiment 2 — Explicit Severity Decision Rule
Model

`meta-llama/llama-3.3-70b-instruct`

###Prompt

```TEXT
You are a production incident extraction system.


Extract information from the incident report.


Return ONLY a JSON object with these exact fields:
- severity
- service
- duration_minutes
- customer_impact
- root_cause
- recommended_actions


Rules:
1. Determine 'severity' as 'high', 'medium', or 'low' based on impact.
   Active service outages, high error rates, or payment failures are 'high'.
2. Use null ONLY when a field's value cannot be determined or inferred from the text.
3. Ensure duration_minutes is an integer or null.


<incident>
At 10:32 AM the payment service started returning HTTP 500 errors.
Approximately 18% of payment requests failed for 23 minutes.
The issue was caused by a database connection pool exhaustion
after a deployment increased concurrent requests.
Rolling back the deployment restored normal operation.
The team should review connection pool limits before redeploying.
</incident>

```


### Actual LLM Response
``` TEXT
{
  "severity": "high",
  "service": "payment",
  "duration_minutes": 23,
  "customer_impact": "18% of payment requests failed",
  "root_cause": "database connection pool exhaustion",
  "recommended_actions": "review connection pool limits before redeploying"
}

```

### Parsed / Validated Result
```TEXT
severity='high'
service='payment'
duration_minutes=23
customer_impact='18% of payment requests failed'
root_cause='database connection pool exhaustion'
recommended_actions='review connection pool limits before redeploying'
```
### Observation

The model classified the incident as high.

The important change was the addition of an explicit severity decision rule.

The same incident therefore produced:

```TEXT
Experiment 1 → severity = null


Experiment 2 → severity = high

```


```TEXT 
    Extraction successful

    severity=None service='payment service' duration_minutes=23 customer_impact='18% of payment requests failed' root_cause='database connection pool exhaustion' recommended_actions='review connection pool limits before redeploying'

    As dictionary:
    {'severity': None, 'service': 'payment service', 'duration_minutes': 23, 'customer_impact': '18% of payment requests failed', 'root_cause': 'database connection pool exhaustion', 'recommended_actions': 'review connection pool limits before redeploying'}
    (tasks) PS C:\Users\User\Desktop\genai-engineer-roadmap\week2-prompt-engineering\tasks\task_2_4> uv run python run_extraction.py
============================================================
STRUCTURED INCIDENT EXTRACTION
============================================================

    Extraction successful

    severity='high' service='payment' duration_minutes=23 customer_impact='18% of payment requests failed' root_cause='database connection pool exhaustion' recommended_actions='review connection pool limits before redeploying'

    As dictionary:
    {'severity': 'high', 'service': 'payment', 'duration_minutes': 23, 'customer_impact': '18% of payment requests failed', 'root_cause': 'database connection pool exhaustion', 'recommended_actions': 'review connection pool limits before redeploying'}
```