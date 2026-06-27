import numpy as np
import google.generativeai as genai
def create_embedding(text, task_type):

    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type=task_type
    )

    return result["embedding"]
def cosine_similarity(vec1, vec2):

    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    return np.dot(vec1, vec2) / (
        np.linalg.norm(vec1)
        *
        np.linalg.norm(vec2)
    )
def create_vector_store(chunks):

    vector_store = []

    for chunk in chunks:

        embedding = create_embedding(
    chunk,
    "retrieval_document"
 
        )  

        vector_store.append(
            {
                "text": chunk,
                "embedding": embedding
            }
        )

    return vector_store
def semantic_search(query, vector_store, top_k=2):

    query_embedding = create_embedding(
    query,
    "retrieval_query"
    )

    results = []


    for item in vector_store:

        score = cosine_similarity(
            query_embedding,
            item["embedding"]
        )

        results.append(
            {
                "text": item["text"],
                "score": score
            }
        )


    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )


    return results[:top_k]