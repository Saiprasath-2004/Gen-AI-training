SYSTEM_PROMPT = """You are a production incident extraction system.

Extract information from the incident report.

Return ONLY a JSON object with these exact fields:
- severity
- service
- duration_minutes
- customer_impact
- root_cause
- recommended_actions

Rules:
1. Determine 'severity' as 'high', 'medium', or 'low' based on impact (e.g., active service outages, high error rates, or payment failures are 'high').
2. Use null ONLY when a field's value cannot be determined or inferred from the text.
3. Ensure duration_minutes is an integer or null.
"""

def built_extraction_prompt(text: str) -> str:
    return f"""
        {SYSTEM_PROMPT}

        <incident>
        {text}
        </incident>
    """