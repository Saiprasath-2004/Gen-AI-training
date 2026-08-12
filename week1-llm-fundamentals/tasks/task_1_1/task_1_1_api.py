import httpx

response = httpx.get(
    "https://api.github.com/this-does-not-exist"
)

print("Status Code:")
print(response.status_code)

print()

print("Headers:")
print(response.headers)

print()

print("JSON Response:")
print(response.json())