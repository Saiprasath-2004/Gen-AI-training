# Task 4.1: See the Vectors for Yourself

## 1. Corpus Embedding
- Embedded 200 sentences from a custom corpus containing clusters on "Cloud Computing" and "Gardening".
- Model used: `all-MiniLM-L6-v2`.
- Results saved to `embeddings.json`.

## 2. Nearest Neighbors Verification
Verified 5 queries using both a manual Numpy implementation of cosine similarity and the `scikit-learn` library.

| Query | Numpy Top 1 | Library Top 1 | Match |
| :--- | :--- | :--- | :--- |
| How to scale cloud infrastructure? | AWS is a powerful tool for scaling. | AWS is a powerful tool for scaling. | Yes |
| Best way to grow spring flowers | Soil blooms beautifully in the spring. | Soil blooms beautifully in the spring. | Yes |
| Managed database services in AWS | AWS offers managed database services. | AWS offers managed database services. | Yes |
| Organic soil for gardening | Soil is a key part of organic gardening. | Soil is a key part of organic gardening. | Yes |
| Container orchestration with Kubernetes | Kubernetes allows for seamless deployment of containers. | Kubernetes allows for seamless deployment of containers. | Yes |

## 3. Semantic vs Keyword Search

### Semantic Search Win
**Query:** "Increasing infrastructure capacity"
- **Semantic Match:** "Kubernetes helps in automating infrastructure."
- **Keyword Match:** No exact match for "Increasing" or "capacity".
- **Why:** The embedding captures the conceptual relationship between "capacity" and "scaling/automation" in a technical context.

### Keyword Search Win
**Query:** "XYZ-999-ABC-123" (Unique Identifier)
- **Semantic Match:** Might find other ID-like strings or the correct one.
- **Keyword Match:** Exact match for the specific token.
- **Why:** Unique identifiers (UUIDs, Error Codes) often have no "semantic" meaning. They are distinct tokens. A keyword search ensures we find the exact record, whereas a semantic search might cluster all "ID-looking" strings together.

## 4. Design Implications
The fact that keyword search wins on unique identifiers means that any production RAG system should likely use a **Hybrid Search** approach. Combining dense embeddings (for conceptual queries) with sparse BM25/keyword indexing (for exact matches, IDs, and rare technical terms) ensures that we don't miss specific records while still benefiting from the flexibility of semantic understanding.

## 5. Cosine Distance Explanation
Cosine distance measures the cosine of the angle between two vectors. If two sentences are conceptually similar, their vectors point in roughly the same direction, resulting in a small angle and a cosine similarity near 1.

**Example from corpus:**
1. "AWS provides high availability for applications."
2. "Azure provides high availability for applications."
These two sentences are almost identical in meaning (differing only by the provider). Their vectors will be very close in space, meaning the angle between them is tiny, and their cosine similarity will be very high (close to 1.0).
