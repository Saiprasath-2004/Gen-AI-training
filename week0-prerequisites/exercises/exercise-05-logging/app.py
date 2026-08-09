import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def divide(a,b):
    logger.info(f"Dividing {a} by {b}")
    try: 
        return a/b
    except ZeroDivisionError:
        logger.error("Attempted to divide by zero")
        return 0

result = divide(10, 0)
result = divide(10, 2)
print(result)