import os
import requests
from pinecone import Pinecone

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "chatbot-index")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Connect to Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

# Retrieve top-k relevant documents from Pinecone
def retrieve_documents(query_embedding, top_k=5):
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return [match["metadata"]["text"] for match in results.get("matches", [])]

# Generate answer using Groq LLM
def generate_answer(question, context_docs):
    prompt = f"Context: {context_docs}\n\nQuestion: {question}\nAnswer:"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama3", "prompt": prompt, "max_tokens": 512}

    resp = requests.post("https://api.groq.com/v1/completions", headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json().get("text", "")

# Optional: function to query HF embeddings API for user question
def get_query_embedding(question):
    HF_API_KEY = os.getenv("HF_API_KEY")
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    data = {"inputs": question}
    resp = requests.post(
        "https://api-inference.huggingface.co/pipeline/feature-extraction/BAAI/bge-large-en-v1.5",
        headers=headers, json=data
    )
    resp.raise_for_status()
    return resp.json()[0]
