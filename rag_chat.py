import os
import requests
from pinecone import Pinecone
from groq import Groq

# Environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

INDEX_NAME = "chatbot-index"

# Embedding model
EMBED_MODEL = "BAAI/bge-large-en-v1.5"

HF_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{EMBED_MODEL}"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

# Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# Groq client
groq_client = Groq(api_key=GROQ_API_KEY)


def generate_query_embedding(query):
    """Generate embedding from Hugging Face API"""

    payload = {"inputs": query}

    response = requests.post(
    HF_URL,
    headers=headers,
    json=payload,
    timeout=20
    )

    data = response.json()

    if not data:
        raise Exception("Embedding API returned empty response")

    # HF returns token embeddings -> average them
    if isinstance(data[0], list):
        embedding = [sum(col) / len(col) for col in zip(*data)]
    else:
        embedding = data

    return embedding


def retrieve_context(query):

    embedding = get_embedding(query)

    results = index.query(
        vector=embedding,
        top_k=3,
        include_metadata=True
    )

    matches = results.get("matches", [])

    if not matches:
        return "", []

    context = ""
    sources = []

    for match in matches:
        context += match["metadata"]["text"] + "\n"
        sources.append(match["metadata"].get("source", "Unknown"))

    return context, sources

def ask_llm(query, context):
    """Send context + question to LLM"""

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
    """Main RAG pipeline"""

    try:

        print("STEP 1: Query received ->", query)

        context, sources = retrieve_context(query)

        print("STEP 2: Context length ->", len(context))

        if not context:
            print("No context retrieved from Pinecone")

            return {
                "answer": "I could not find the answer in the documents.",
                "sources": []
            }

        print("STEP 3: Sending prompt to LLM")

        answer = ask_llm(query, context)

        print("STEP 4: LLM response received")

        return {
            "answer": answer,
            "sources": sources
        }

    except Exception as e:

        import traceback
        print("========== RAG ERROR ==========")
        traceback.print_exc()   # THIS SHOWS THE REAL ERROR
        print("================================")

        return {
            "answer": "Server error occurred while processing the request.",
            "sources": []
        }
