# Exceptions

## Purpose

Exceptions handle unexpected situations during program execution.

---

## Best Practice

Catch specific exceptions whenever possible.

Avoid:

except Exception:

Prefer:

except ValueError:

except KeyError:

except FileNotFoundError:

---

## Rule

Catch only the exceptions you can handle.

---

## Benefits

- Better debugging
- Better logs
- Easier maintenance
- More meaningful API responses


## Engineering Rule

A rule many senior developers follow:

    Catch only the exceptions you can handle.

If you don't know how to handle it:

    raise

or let it propagate.

try:
    save_booking()
except DatabaseError as e:
    logger.error(e)
    raise

Now:

    Error is logged
    Error is visible
    Error can be debugged