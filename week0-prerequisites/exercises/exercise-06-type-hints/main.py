def create_user(
    name: str,
    age: int
) -> dict:
    return {
        "name": name,
        "age": age
    }


user = create_user(
    "Sai",
    22
)

print(user)