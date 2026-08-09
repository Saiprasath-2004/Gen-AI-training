# P.4 — Debugger and Breakpoints

## Definition

A debugger is a tool that allows us to pause a program while it is running so that we can inspect variables, function calls, and execution flow.

---

## Why do we need it?

Without a debugger:

- Add print statements.
- Execute the program.
- Observe the output.
- Repeat the process.

With a debugger:

- Pause execution.
- Inspect variables.
- Execute code line by line.
- Identify the problem.

---

## Important terms

### Breakpoint

A marker that tells the debugger to stop execution at a specific line.

### Step Over (F10)

Executes the current line and moves to the next line.

### Step Into (F11)

Moves inside the function being called.

### Step Out (Shift + F11)

Exits the current function.

### Continue (F5)

Continues execution.

---

## Debugging workflow

1. Create the file.
2. Open the Run and Debug section.
3. Add a breakpoint.
4. Start debugging.
5. Inspect the variables.
6. Move through the code.

---

## Example

def calculate_total(price, quantity, discount):
    subtotal = price * quantity
    tax = subtotal * 0.18
    total = subtotal + tax - discount
    return total

result = calculate_total(1000, 2, 50)

print(result)

---

## Expected values

price = 1000

quantity = 2

discount = 50

subtotal = 2000

tax = 360

total = 2310


# P.5 — Virtual Environments

## Definition

A virtual environment is an isolated Python environment used by a single project.

---

## Why do we use it?

- Avoid dependency conflicts.
- Keep projects isolated.
- Improve reproducibility.
- Make deployment easier.

---

## Common commands

uv init

uv venv

.venv\Scripts\activate

uv add package_name

uv sync

uv lock

---

## Important files

pyproject.toml

uv.lock

# P.6 — pyproject.toml

## Purpose

Stores project configuration and dependency information.

---

## Contents

- Project name
- Version
- Dependencies
- Python version
- Build configuration

---

## Common commands

uv add package_name

uv remove package_name

uv sync

uv lock

---

## Related files

pyproject.toml

uv.lock