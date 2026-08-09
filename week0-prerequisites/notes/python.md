Dataclass
    ↓
Stores data

Enum
    ↓
Restricts valid values

Decorator
    ↓
Modifies behavior

Exceptions
    ↓
Handles failures

Type Hints
    ↓
Describe data contracts

Pydantic
    ↓
Enforces and validates data contracts

# Dataclasses

## Purpose

Dataclasses reduce boilerplate code.

---

## Advantages

- Cleaner code
- Automatic constructor creation
- Better readability
- Easier maintenance

---

## Decorator

@dataclass

---

## Common use cases

- User objects
- Database objects
- Prompt objects
- Agent state objects
- API response objects

### My Understanding

Dataclasses are used when a class mainly stores data.

Instead of manually writing constructors and other boilerplate methods, Python generates them automatically.

In AI systems they are commonly used for:

- Messages
- Prompts
- Documents
- Agent state
- Tool results



# Enums

## Purpose

Enums provide a fixed set of valid values.

---

## Benefits

- Prevent typos
- Improve readability
- Improve type safety
- Easier validation

---

## Common usage

- User roles
- Booking status
- Expense status
- Agent state
- Workflow status

---

## Example

class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"

# Type Hints

## Purpose

Type hints describe expected input and output types.

---

## Benefits

- Better readability
- IDE support
- Easier maintenance
- Framework integration

---

## Example

def create_user(
    name: str,
    age: int
) -> dict:

---

## Important

Type hints are not enforced by Python runtime.

They are mainly used by tools, IDEs, and frameworks.


### My Understanding

Python itself does not enforce type hints at runtime.

Type hints are primarily used by:

- IDEs (VS Code, PyCharm)
- Static analysis tools
- Linters
- Type checkers
- Frameworks like FastAPI and Pydantic

Type hints act as a contract that describes the expected input and output types.

Frameworks and tools can read these type hints and enforce validation, generate schemas, provide autocomplete, and improve developer experience.