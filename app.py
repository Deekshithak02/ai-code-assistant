import streamlit as st
import tempfile
from main import (
    read_file,
    validate_file,
    build_review_prompt,
    build_test_prompt,
    build_documentation_prompt,
    review_code,
    chunk_text
)
from embedding_store import load_embeddings, create_and_store_embeddings
from retrieval import semantic_search

st.set_page_config(
    page_title="AI Code Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Code Assistant")
st.write("Analyze Java code using Google Gemini AI.")

uploaded_file = st.file_uploader(
    "Upload Java File",
    type=["java"]
)

option = st.selectbox(
    "Choose an option",
    [
        "Review Code",
        "Generate Unit Tests",
        "Generate Documentation"
    ]
)

query = st.text_input("Enter your query")
if st.button("Analyze"):

    if uploaded_file is None:
        st.error("Please upload a Java file.")
        st.stop()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".java") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    if not validate_file(temp_path):
        st.error("Only Java files are supported.")
        st.stop()

    code = read_file(temp_path)

    if code is None:
        st.error("Unable to read file.")
        st.stop()
        if option == "Review Code":

           chunks = chunk_text(code)

           vector_store = load_embeddings()

        if vector_store is None:
            vector_store = create_and_store_embeddings(chunks)

        relevant_chunks = semantic_search(query, vector_store)

        context = "\n".join(
            item["text"] for item in relevant_chunks
        )

        prompt = build_review_prompt(context)

    elif option == "Generate Unit Tests":

        prompt = build_test_prompt(code)

    else:

        prompt = build_documentation_prompt(code)

    with st.spinner("Analyzing..."):

        result = review_code(prompt)

    st.subheader("Result")

    st.code(result, language="json")