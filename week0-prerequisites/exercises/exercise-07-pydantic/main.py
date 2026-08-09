from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    age: int


user = UserCreate(
    name="Sai",
    age="22"
)

print(user)
print(type(user.age))