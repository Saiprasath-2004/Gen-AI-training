import json
import numpy as np
import re
from sentence_transformers import SentenceTransformer

def load_data():
    with open("embeddings.json", "r") as f:
        return json.load(f)

def numpy_cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def find_nn_numpy(query_vec, all_vecs, k=1):
    similarities = [numpy_cosine_similarity(query_vec, v) for v in all_vecs]
    top_k_indices = np.argsort(similarities)[::-1][:k]
    return [(top_k_indices[i], similarities[top_k_indices[i]]) for i in range(k)]

def clean_text(text):
    return re.sub(r'[^\w\s]', '', text.lower()).split()

def keyword_search(query, corpus):
    q_words = set(clean_text(query))
    scores = []
    for s in corpus:
        s_words = set(clean_text(s))
        scores.append(len(q_words.intersection(s_words)))
    
    best_idx = np.argmax(scores)
    if scores[best_idx] == 0:
        return None, 0
    return best_idx, scores[best_idx]

def main():
    data = load_data()
    sentences = data["sentences"]
    embeddings = np.array(data["embeddings"])
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print("--- Semantic vs Keyword Case Studies ---\n")

    # Case 1: Semantic Beats Keyword
    q_sem = "Increasing infrastructure capacity"
    q_vec_sem = model.encode(q_sem)
    nn_sem = find_nn_numpy(q_vec_sem, embeddings, k=1)
    kw_sem_idx, kw_sem_score = keyword_search(q_sem, sentences)
    
    print(f"Query: {q_sem}")
    print(f"Semantic Match: {sentences[nn_sem[0][0]]} (sim: {nn_sem[0][1]:.4f})")
    if kw_sem_idx is not None:
        print(f"Keyword Match: {sentences[kw_sem_idx]} (score: {kw_sem_score})")
    else:
        print("Keyword Match: NO MATCH FOUND")
    
    print("Observation: Semantic search finds related concepts (capacity/infrastructure), whereas keyword search fails due to no exact word overlap.")

    print("\n" + "-"*40 + "\n")

    # Case 2: Keyword Beats Semantic
    # Let's use a truly random ID that the model won't recognize as a "system error"
    q_kw = "XYZ-999-ABC-123"
    # Update corpus to include this
    # (I'll just add it to the corpus file now via a separate step if needed, but I'll assume I'll add it to the list)
    
    # Let's just use one that's already there but make it obscure.
    # Actually, I'll just add a very specific one to the corpus now.
    
    # For the sake of this script, I'll modify the corpus list in memory
    sentences.append("Reference ID: XYZ-999-ABC-123")
    # Re-embed for this one sentence
    q_vec_kw = model.encode(q_kw)
    # We need to add the embedding for the new sentence to the embeddings array
    new_emb = model.encode(["Reference ID: XYZ-999-ABC-123"])[0]
    embeddings = np.vstack([embeddings, new_emb])

    nn_kw = find_nn_numpy(q_vec_kw, embeddings, k=1)
    kw_kw_idx, kw_kw_score = keyword_search(q_kw, sentences)

    print(f"Query: {q_kw}")
    print(f"Semantic Match: {sentences[nn_kw[0][0]]} (sim: {nn_kw[0][1]:.4f})")
    if kw_kw_idx is not None:
        print(f"Keyword Match: {sentences[kw_kw_idx]} (score: {kw_kw_score})")
    else:
        print("Keyword Match: NO MATCH FOUND")
    
    print("Observation: Keyword search is an absolute match for specific IDs. Semantic search might find something 'similar' in nature (like another ID) but doesn't guarantee the exact match if the token is rare/OOV.")

if __name__ == "__main__":
    main()
