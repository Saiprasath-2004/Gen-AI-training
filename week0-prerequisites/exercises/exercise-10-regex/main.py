import re

email = "sai@gmail.com"

pattern = r"^\w+@\w+\.\w+$"

match = re.match(pattern, email)

if match:
    print("Valid Email")
else:
    print("Invalid Email")