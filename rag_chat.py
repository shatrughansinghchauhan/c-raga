import os
import requests
import pinecone
from typing import List

# -----------------------------
# ENVIRONMENT VARIABLES
# -----------------------------
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "chatbot-index")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east1-gcp")  # replace with your env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# -----------------------------
# INITIALIZE PINECONE
# -----------------------------
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index = pinecone.Index(PINECONE_INDEX)

# -----------------------------
# FUNCTIONS
# -----------------------------

def retrieve_documents(query_embedding: List[float], top_k: int = 5) -> List[str]:
    """
    Retrieve top-k relevant chunks from Pinecone.
    query_embedding: precomputed embedding of the question (list of floats)
    """
    try:
        res = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
        matches = res.get("matches", [])
        return [match["metadata"]["text"] for match in matches]
    except Exception as e:
        print("Pinecone retrieval error:", e)
        return []

def generate_answer(question: str, context_docs: List[str]) -> str:
    """
    Generate answer from Groq LLM given question and context.
    """
    try:
        prompt = f"Context: {context_docs}\n\nQuestion: {question}\nAnswer:"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "max_tokens": 512
        }

        resp = requests.post(
            "https://api.groq.com/v1/completions",
            headers=headers,
            json=payload,
            timeout=20
        )
        resp.raise_for_status()
        return resp.json().get("completion", "Sorry, I could not generate an answer.")
    except Exception as e:
        print("Groq API error:", e)
        return "Sorry, something went wrong with the LLM."
