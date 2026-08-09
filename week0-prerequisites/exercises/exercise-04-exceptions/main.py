def divide(a: int, b: int) -> float:
    try:
        return a / b

    except ZeroDivisionError:
        print("Cannot divide by zero")
        return 0


result = divide(10, 0)

print(result)