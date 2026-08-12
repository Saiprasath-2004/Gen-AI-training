import tiktoken

text = "Hello chatgpt,how r u ?"

encoding = tiktoken.get_encoding("cl100k_base")

token_ids = encoding.encode(text)

print(token_ids)

print()

for token in token_ids:
    print(
        token,
        "->",
        encoding.decode([token])
    )