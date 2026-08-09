from dataclasses import dataclass

@dataclass
class Person:

    name : str
    age : int

user1 = Person("Alice", 30)

print(user1)