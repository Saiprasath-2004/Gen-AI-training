# Logging

## Purpose

Logging records events that occur while the application runs.

---

## Why not print()?

print() is useful during development.

Logging provides:

- Severity levels
- Better debugging
- Production monitoring
- Persistent records

---

## Levels

DEBUG

INFO

WARNING

ERROR

CRITICAL

---

## Common usage

logger.info()

logger.warning()

logger.error()

logger.exception()



## DEBUG

Developer information.

logger.debug("User payload received")
INFO

## Normal application events.

logger.info("User logged in")

## WARNING

## Something unusual but not broken.

logger.warning("Rate limit almost reached")

## ERROR

## Something failed.

logger.error("Database unavailable")

## CRITICAL

## Application may stop functioning.

logger.critical("Payment service unavailable")

## AI Engineering Example

logger.info("Embedding generation started")

logger.info("Vector search completed")

logger.error("OpenAI API timeout")

When building agents later, logs become your best friend.