Before sending this to GPT, Claude, Gemini, etc., the company wants to:

Validate the data
Remove sensitive information
Count tokens
Calculate cost
Generate reports
Skip bad records
Log failures

This is exactly what our project is doing.



messages.json
      │
      ▼
┌───────────────┐
│  loader.py    │
└───────────────┘
      │
      ▼
list[dict]
      │
      ▼
┌───────────────┐
│ Pydantic      │
│ Validation    │
└───────────────┘
      │
      ▼
list[Message]
      │
      ▼
┌───────────────┐
│ redactor.py   │
└───────────────┘
      │
      ▼
Phone numbers removed
      │
      ▼
┌───────────────┐
│ cost.py       │
└───────────────┘
      │
      ▼
Token Cost
      │
      ▼
┌───────────────┐
│ reporting     │
└───────────────┘
      │
      ▼
Per-role summary



The Mental Model I Want You To Have

Don't think:

Today we learned Pydantic.
Tomorrow we learn Regex.

Think:

We are building a data processing pipeline.

Every concept exists because the pipeline needs it.

Concept	Why We Need It

pathlib	    Read files
JSON	    Input data
Pydantic	Validate data
Enum	    Controlled values
Regex	    Remove phone numbers
Decimal	    Accurate money
UUID	    Tracking
Logging	    Debugging
Counter	    Reporting
Async	    Scale
Tests	    Reliability

Everything is serving the pipeline.

That's why Week 0 exists. It is not a Python course. It is teaching you the building blocks needed before Week 1 (LLMs), Week 2 (Prompting), Week 3 (RAG), and later Agentic AI systems.



Why default_factory?

Because:

uuid4()

must execute for every new object.

Not once when the class loads.

Same for:

datetime.now(...)