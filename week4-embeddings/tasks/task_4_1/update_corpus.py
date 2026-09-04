import json

# Load existing corpus
with open("corpus.json", "r") as f:
    sentences = json.load(f)

# Add a very specific identifier for Keyword > Semantic
sentences.append("The system error code is ERR_999_Xyz.")
sentences.append("User ID 12345-abc belongs to the admin group.")

# Add a phrase that is semantically similar but has no keyword overlap
# Semantic search should find "Scaling the cloud" for "Increasing infrastructure capacity"
sentences.append("Kubernetes is used for scaling the cloud.")

with open("corpus.json", "w") as f:
    json.dump(sentences, f, indent=2)

print(f"Updated corpus. Total sentences: {len(sentences)}")
