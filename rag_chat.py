import os
import traceback
from pinecone import Pinecone
from groq import Groq
from sentence_transformers import SentenceTransformer

# =========================
# Environment Variables
# =========================

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
INDEX_NAME = "chatbot-index"

# =========================
# Initialize Models
# =========================

print("Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("Embedding model loaded.")

print("Initializing Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)
print("Pinecone connected.")

print("Initializing Groq client...")
client = Groq(api_key=GROQ_API_KEY)
print("Groq client ready.")

# =========================
# Helper Functions
# =========================

def generate_embedding(text):
    print("Step 1: Generating embedding for query...")
    embedding = embedding_model.encode(text).tolist()
    print("Embedding generated.")
    return embedding


def search_vector_db(embedding):
    print("Step 2: Searching Pinecone...")
    results = index.query(
        vector=embedding,
        top_k=5,
        include_metadata=True
    )
    print("Pinecone search complete.")
    return results


def build_context(results):
    print("Step 3: Building context from Pinecone results...")

    context = ""
    matches = results.get("matches", [])

    for match in matches:
        if "metadata" in match and "text" in match["metadata"]:
            context += match["metadata"]["text"] + "\n"

    print("Context built.")
    return context


def ask_llm(query, context):
    print("Step 4: Sending request to LLM...")

    prompt = f"""
Answer the question using the context below.

Context:
{context}

Question:
{query}
"""

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    print("LLM response received.")
    return completion.choices[0].message.content


# =========================
# Main Pipeline Function
# =========================

def chat(query):

    try:
        print("\n---------------------------")
        print("New Query Received:", query)

        # Step 1: Embedding
        embedding = generate_embedding(query)

        # Step 2: Vector Search
        results = search_vector_db(embedding)

        # Step 3: Context
        context = build_context(results)

        # Step 4: LLM
        response = ask_llm(query, context)

        print("Step 5: Returning response.")
        print("---------------------------\n")

        return response

    except Exception as e:
        print("\n!!!!!!!! ERROR OCCURRED !!!!!!!!")
        print(str(e))
        traceback.print_exc()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

        return "Server error occurred while processing the request."
