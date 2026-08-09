# Async Programming

## Purpose

Allows programs to perform other work while waiting for slow operations.

---

## Common Waiting Operations

- Database queries
- API calls
- File operations
- Network requests
- Vector database searches

---

## Keywords

async

await

---

## Important

Async does not make code faster.

Async makes waiting more efficient.

---

## Common Usage

FastAPI

OpenAI API

Anthropic API

LangGraph

Agent Workflows


# Concurrency vs Parallelism

## Concurrency

Handling multiple tasks by switching between them.

Best for:

- API calls
- Database queries
- File I/O
- Network operations

Uses:

- async
- await

---

## Parallelism

Executing multiple tasks simultaneously using multiple workers.

Best for:

- Image processing
- ML training
- Heavy computations
- Data processing

---

## Rule

Waiting → Concurrency

Computing → Parallelism