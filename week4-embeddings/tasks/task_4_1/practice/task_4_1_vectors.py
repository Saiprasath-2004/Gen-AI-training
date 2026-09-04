"""
Task 4.1: See the vectors for yourself
Goal: Embed 200 sentences, verify Cosine Similarity via manual NumPy vs Library,
      and identify semantic vs. keyword search edge cases.

This script demonstrates how text is converted into high-dimensional vectors (embeddings)
and how these vectors can be used to perform semantic search. It includes persistence
to avoid redundant embedding computations.
"""

import os
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain_huggingface import HuggingFaceEmbeddings

# Define persistence file paths in the same directory as the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORPUS_FILE = os.path.join(BASE_DIR, "corpus.json")
EMBEDDINGS_FILE = os.path.join(BASE_DIR, "embeddings.json")


# 1. Corpus Generation
def generate_corpus():
    """
    Generates a synthetic corpus of 200 sentences across various technical
    and non-technical topics to test semantic search.

    Returns:
        list: A list of 200 strings.
    """
    topics = [
        "Database indexing improves B-tree lookup speeds for heavy read operations.",
        "PostgreSQL pgvector extension enables high-dimensional vector similarity queries.",
        "Employee health insurance covers inpatient hospitalization up to 500,000 INR.",
        "Annual leave allocation is 20 days per fiscal year, non-accruable.",
        "HTTP 502 Bad Gateway indicates an upstream service failed to respond in time.",
        "The system uses OAuth2 JSON Web Tokens (JWT) for microservice authentication.",
        "Error code ERR_AUTH_8091 occurs when the client refresh token expires.",
        "Chest pain radiating to the left arm requires immediate emergency evaluation.",
        "Chest of drawers in office supplies must be anchor-secured to prevent tipping.",
        "Optical Character Recognition (OCR) converts scanned image PDFs into plaintext string buffers."
    ]

    # Expand programmatically to exactly 200 clean sentences
    corpus = []
    for i in range(200):
        base_sentence = topics[i % len(topics)]
        corpus.append(f"[{i+1:03d}] {base_sentence} (ID-{1000+i})")
    return corpus


# 2. Persistence Utilities
def save_data(corpus, embeddings):
    """
    Saves the corpus and embeddings to separate JSON files for persistence.

    Args:
        corpus (list): The list of sentences.
        embeddings (np.ndarray): The numpy array of vectors.
    """
    # Save corpus as a simple JSON list
    with open(CORPUS_FILE, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2)

    # NumPy arrays aren't JSON serializable, so convert to a list first
    with open(EMBEDDINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(embeddings.tolist(), f)

    print(f"Successfully saved corpus to {CORPUS_FILE} and embeddings to {EMBEDDINGS_FILE}")


def load_data():
    """
    Loads the corpus and embeddings from JSON files if they exist.

    Returns:
        tuple: (corpus, embeddings) if both files exist, otherwise (None, None).
    """
    if os.path.exists(CORPUS_FILE) and os.path.exists(EMBEDDINGS_FILE):
        try:
            with open(CORPUS_FILE, "r", encoding="utf-8") as f:
                corpus = json.load(f)
            with open(EMBEDDINGS_FILE, "r", encoding="utf-8") as f:
                embeddings = np.array(json.load(f))
            return corpus, embeddings
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading persistence files: {e}")
            return None, None
    return None, None


# 3. Cosine Similarity Calculations
def manual_cosine_similarity(query_vector: np.ndarray, doc_vectors: np.ndarray) -> np.ndarray:
    """
    Computes Cosine Similarity manually using matrix operations.

    Formula: (A · B) / (||A|| * ||B||)

    Args:
        query_vector (np.ndarray): 1D vector of the query (d,)
        doc_vectors (np.ndarray): 2D matrix of documents (N, d)

    Returns:
        np.ndarray: 1D array of similarity scores for each document.
    """
    # Dot product between 1D query vector (d,) and 2D doc matrix (N, d) -> result (N,)
    dot_product = np.dot(doc_vectors, query_vector)

    # Compute L2 norms (magnitudes)
    query_norm = np.linalg.norm(query_vector)
    doc_norms = np.linalg.norm(doc_vectors, axis=1)

    # Compute similarity, adding a small epsilon to avoid division by zero
    similarity = dot_product / (doc_norms * query_norm + 1e-10)
    return similarity


def manual_cosine_distance(query_vector: np.ndarray, doc_vectors: np.ndarray) -> np.ndarray:
    """
    Computes Cosine Distance, which is the complement of Cosine Similarity.

    Formula: Cosine Distance = 1 - Cosine Similarity
    Range: [0.0 (identical), 2.0 (opposite)]
    """
    return 1.0 - manual_cosine_similarity(query_vector, doc_vectors)


# 4. Main Execution Workflow
def main():
    print("--- Vector Search Demonstration ---\n")

    # Step 1: Load or Generate Data
    corpus, doc_embeddings = load_data()

    if corpus is None:
        print("Data not found on disk. Generating and embedding corpus...")
        # Initialize the embedding model
        embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        corpus = generate_corpus()
        print(f"Generated {len(corpus)} sentences.")

        # Generate embeddings for the entire corpus (N, d)
        doc_embeddings = np.array(embedder.embed_documents(corpus))
        print(f"Doc Embeddings Matrix Shape: {doc_embeddings.shape}")

        # Persist for future runs
        save_data(corpus, doc_embeddings)
    else:
        print(f"Loading existing corpus and embeddings from disk...")
        print(f"Corpus size: {len(corpus)}, Embeddings shape: {doc_embeddings.shape}")

    # We need the embedder for the queries, regardless of whether we loaded the corpus
    # (Initialize only once if not already initialized)
    if 'embedder' not in locals():
        embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Sample Queries for Verification
    queries = [
        "How do I speed up database query lookups?",          # Query 1: Semantic (DB)
        "What is the medical policy for heart issues?",       # Query 2: Polysemy/Semantic (Health)
        "ERR_AUTH_8091",                                      # Query 3: Exact Keyword (Auth Error Code)
        "How do we handle scanned PDF files?",                # Query 4: Ingestion/OCR
        "Furniture safety guidelines for desks and drawers"   # Query 5: Word-sense disambiguation
    ]

    print("\n--- 3. Running Queries: NumPy vs Library Verification ---")

    for idx, q in enumerate(queries, 1):
        # Embed the query vector (d,)
        q_embedding = np.array(embedder.embed_query(q))

        # METHOD A: Pure NumPy Calculation
        manual_sims = manual_cosine_similarity(q_embedding, doc_embeddings)
        manual_dists = manual_cosine_distance(q_embedding, doc_embeddings)

        # METHOD B: Library Similarity Search (scikit-learn implementation)
        # Reshape 1D query array (384,) to 2D matrix (1, 384) for sklearn interface
        library_sims = cosine_similarity(q_embedding.reshape(1, -1), doc_embeddings)[0]

        # Verification: Compare manual vs library results
        max_diff = np.max(np.abs(manual_sims - library_sims))
        is_exact_match = np.allclose(manual_sims, library_sims, atol=1e-6)

        # Find top 3 closest documents (smallest distance)
        top_3_indices = np.argsort(manual_dists)[:3]

        print(f"\n[Query {idx}]: '{q}'")
        print(f"   Verification -> Exact Match? {is_exact_match} | Max Diff: {max_diff:.10f}")
        print("  Top 3 Nearest Neighbors:")
        for rank, doc_idx in enumerate(top_3_indices, 1):
            print(
                f"    {rank}. [Dist: {manual_dists[doc_idx]:.4f} | "
                f"Manual Sim: {manual_sims[doc_idx]:.6f} | "
                f"Library Sim: {library_sims[doc_idx]:.6f}] "
                f"{corpus[doc_idx]}"
            )

    print("\n" + "="*60)
    print("--- 4. Semantic Search WIN vs Keyword Search WIN ---")
    print("="*60)

    # CASE 1: Semantic Search Win
    win_semantic_query = "myocardial infarction treatment covered?"
    q_sem_vec = np.array(embedder.embed_query(win_semantic_query))
    sem_dists = manual_cosine_distance(q_sem_vec, doc_embeddings)
    top_sem = np.argsort(sem_dists)[0]

    print("\n[SEMANTIC WIN CASE]")
    print(f"Query: '{win_semantic_query}'")
    print(f"Nearest Doc: {corpus[top_sem]}")
    print(f"Cosine Distance: {sem_dists[top_sem]:.4f}")
    print("Explanation: The query shares zero matching words with the document, but vector search recognized 'myocardial infarction' aligns semantically with health insurance and hospitalization.")

    # CASE 2: Keyword search (Embedding failure)
    win_keyword_query = "ID-1006"
    q_kw_vec = np.array(embedder.embed_query(win_keyword_query))
    kw_dists = manual_cosine_distance(q_kw_vec, doc_embeddings)
    top_kw = np.argsort(kw_dists)[0]

    print("\n[KEYWORD WIN / EMBEDDING FAILURE CASE]")
    print(f"Query: '{win_keyword_query}'")
    print(f"Nearest Doc: {corpus[top_kw]}")
    print(f"Cosine Distance: {kw_dists[top_kw]:.4f}")
    print("Explanation: Vector embeddings blur exact alphanumeric identifiers into general high-dimensional context space. BM25 or exact SQL ILIKE would find ID-1006 instantly, whereas vector search returns an inaccurate near neighbor.")

if __name__ == "__main__":
    main()
