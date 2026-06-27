import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

from retrieval import create_vector_store, semantic_search

from embedding_store import (
    load_embeddings,
    create_and_store_embeddings
)

from retrieval import semantic_search

# Load environment variables
load_dotenv()

# Read API key from .env
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=api_key)

# Select model
model = genai.GenerativeModel("gemini-2.5-flash")

def get_code():

    print("Paste your code below.")
    print("Type END on a new line when finished.")

    lines = []

    while True:
        line = input()

        if line.strip().upper() == "END":   
            break

        lines.append(line)

    return "\n".join(lines)

def get_file_path():
    return input("Enter Java file path: ").strip()

def get_user_choice():
    print("\nChoose an option:")
    print("1. Review Code")
    print("2. Generate Unit Tests")
    print("3. Generate Documentation")

    return input("Enter choice (1-3): ").strip()

def read_file(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read()

    except FileNotFoundError:
        return None

    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
def chunk_text(text, chunk_size=500):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)

    return chunks

def review_chunks(chunks):
    all_bugs = []
    all_security_issues = []
    all_improvements = []

    for chunk in chunks:
        prompt = build_review_prompt(chunk)

        review = review_code(prompt)

        review_data = parse_review(review)

        if review_data:
            all_bugs.extend(review_data["bugs"])
            all_security_issues.extend(
                review_data["security_issues"]
            )
            all_improvements.extend(
                review_data["improvements"]
            )

    return {
        "bugs": all_bugs,
        "security_issues": all_security_issues,
        "improvements": all_improvements
    }
    
def build_review_prompt(code):
    return f"""
You are a Principal Software Engineer.

Analyze the following Java code.

Return ONLY valid JSON.

Do not include explanations.
Do not include markdown.
Do not include code fences.

Format:

{{
  "bugs": ["string"],
  "security_issues": ["string"],
  "improvements": ["string"],
  "time_complexity": "string"
}}

Each list must contain strings only.
Do not return objects.
Do not include severity fields.

Code:
{code}
"""

def build_test_prompt(code):
    return f"""
You are a senior Java developer.

Generate JUnit 5 test cases for the following Java code.

Include:
1. Happy path tests
2. Edge cases
3. Exception scenarios

Code:
{code}
"""

def build_documentation_prompt(code):
    return f"""
You are a technical documentation expert.

Generate documentation for the following Java code.

Include:
1. Purpose
2. Method descriptions
3. Parameters
4. Return values
5. Usage example

Code:
{code}
"""

def review_code(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error while reviewing code: {e}"
    
def parse_review(review_text):
    try:
        return json.loads(review_text)

    except json.JSONDecodeError:
        print("Invalid JSON returned by Gemini.")
        return None
    
def validate_file(file_path):
    return file_path.endswith(".java")

def review_chunks(chunks):
    all_bugs = []
    all_security_issues = []
    all_improvements = []

    for chunk in chunks:

        prompt = build_review_prompt(chunk)

        review = review_code(prompt)

        review_data = parse_review(review)

        if review_data:

            all_bugs.extend(
                review_data["bugs"]
            )

            all_security_issues.extend(
                review_data["security_issues"]
            )

            all_improvements.extend(
                review_data["improvements"]
            )

    return {
        "bugs": list(dict.fromkeys(all_bugs)),
        "security_issues":
            list(dict.fromkeys(all_security_issues)),
        "improvements":
            list(dict.fromkeys(all_improvements))
    }

def find_relevant_chunks(chunks, keyword):
    relevant_chunks = []

    for chunk in chunks:

        if keyword.lower() in chunk.lower():
            relevant_chunks.append(chunk)

    return relevant_chunks

def review_by_keyword(chunks, keyword):

    vector_store = create_vector_store(chunks)

    relevant_chunks = semantic_search(
     query=keyword,
     vector_store=vector_store
 )


    if not relevant_chunks:
        print("No relevant chunks found.")
        return None

    return review_chunks(relevant_chunks)

def main():
    file_path = get_file_path()
    choice = get_user_choice()

    if not validate_file(file_path):
       print("Only .java files are supported.")
       return

    code = read_file(file_path)

    if code is None:
      print("Unable to read file.")
      return

    if choice == "1":

      chunks = chunk_text(code)
      vector_store = load_embeddings()


      if vector_store is None:

        print("Creating embeddings...")

        vector_store = create_and_store_embeddings(
            chunks
       )

      else:

        print("Using existing embeddings...")


      query = input(
        "\nEnter your query: "
      )


      relevant_chunks = semantic_search(
        query,
        vector_store
      )


      context = "\n".join(
        item["text"]
        for item in relevant_chunks
      )


      prompt = build_review_prompt(context)


      result = review_code(prompt)


      print(result)

      return

    elif choice == "2":
      prompt = build_test_prompt(code)

      result = review_code(prompt)

      print(result)

      return


    elif choice == "3":
      prompt = build_documentation_prompt(code)

      result = review_code(prompt)

      print(result)

      return


    else:
      print("Invalid choice.")

      chunks = [
        "LoginService handles authentication",
        "PaymentService processes payments",
        "UserProfile manages users"
     ]

      result = find_relevant_chunks(chunks, "payment")

      print(result)
      

if __name__ == "__main__":
    main()
