import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Load corpus
with open("corpus.json", "r") as f:
    sentences = json.load(f)

# Use a lightweight model
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(sentences)

# Save embeddings and sentences together
data = {
    "sentences": sentences,
    "embeddings": embeddings.tolist()
}

with open("embeddings.json", "w") as f:
    json.dump(data, f)

print(f"Embedded {len(sentences)} sentences.")
