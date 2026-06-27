import json
import os
from retrieval import create_vector_store
def save_embeddings(vector_store, file_name="embeddings.json"):

    with open(file_name, "w") as file:
        json.dump(
            vector_store,
            file,
            indent=4
        )

    print("Embeddings saved successfully.")
def load_embeddings(file_name="embeddings.json"):

    if not os.path.exists(file_name):
        return None

    with open(file_name,"r") as file:
        return json.load(file)
    from retrieval import create_vector_store


def create_and_store_embeddings(chunks):

    vector_store = create_vector_store(chunks)

    save_embeddings(vector_store)

    return vector_store