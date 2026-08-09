# Decorators

## Purpose

Decorators add functionality to functions without modifying the original function.

---

## Internal behavior

@decorator

def hello():

becomes

hello = decorator(hello)

---

## Common use cases

- FastAPI routes
- Authentication
- Logging
- Validation
- Caching
- Tool registration

---

## Structure

def decorator(func):

    def wrapper():
        ...
        func()
        ...

    return wrapper


    
    @decorator
    def hello():
        print("Hello")

    into:

    def hello():
        print("Hello")


    hello = decorator(hello)

    ### My Understanding

A decorator is a function that receives another function as input and returns a new callable.

Python converts:

@decorator
def hello():
    ...

into:

hello = decorator(hello)

After decoration, the variable name may point to a wrapper function instead of the original function.

This allows us to add behavior before or after executing the original function.