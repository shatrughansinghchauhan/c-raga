import os
import requests
from pinecone import Pinecone
from groq import Groq

# Environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

INDEX_NAME = "chatbot-index"

# Smaller embedding model
EMBED_MODEL = "BAAI/bge-small-en-v1.5"

HF_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{EMBED_MODEL}"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

# Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# Groq
groq_client = Groq(api_key=GROQ_API_KEY)


def generate_query_embedding(query):

    payload = {"inputs": query}

    response = requests.post(
        HF_URL,
        headers=headers,
        json=payload
    )

    embedding = response.json()

    return embedding


def retrieve_context(query, top_k=5):

    query_embedding = generate_query_embedding(query)

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    contexts = []
    sources = []

    for match in results["matches"]:

        meta = match["metadata"]

        contexts.append(meta["text"])

        sources.append({
            "source": meta["source"],
            "page": meta["page"]
        })

    context = "\n\n".join(contexts)

    return context, sources


def ask_llm(query, context):

    prompt = f"""
You are a helpful assistant answering questions from documents.

Use ONLY the context below.

If the answer is not present say:
"I could not find the answer in the documents."

Context:
{context}

Question:
{query}

Answer:
"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


def rag_chat(query):

    context, sources = retrieve_context(query)

    answer = ask_llm(query, context)

    return {
        "answer": answer,
        "sources": sources
    }
