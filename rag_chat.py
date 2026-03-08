import os
import requests
from pinecone import Pinecone
from groq import Groq

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

INDEX_NAME = "chatbot-index"

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
HF_URL = f"https://router.huggingface.co/hf-inference/models/{EMBED_MODEL}"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

groq_client = Groq(api_key=GROQ_API_KEY)


def generate_query_embedding(query):

    payload = {
        "inputs": query
    }

    response = requests.post(
        HF_URL,
        headers=headers,
        json=payload
    )

    result = response.json()

    print("HF RESPONSE:", result)

    if isinstance(result, dict):
        raise Exception(f"HuggingFace error: {result}")

    # ensure vector format
    embedding = result[0] if isinstance(result[0], list) else result

    return embedding


def retrieve_context(query, top_k=5):

    query_embedding = generate_query_embedding(query)

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        namespace="class 6 - class 6th - Science (3).pdf",
        include_metadata=True
    )

    matches = results.matches if hasattr(results, "matches") else []

    if not matches:
        print("No matches returned from Pinecone")
        return "", []

    contexts = []
    sources = []

    for match in matches:

        meta = match.metadata if hasattr(match, "metadata") else {}

        contexts.append(meta.get("text", ""))

        sources.append({
            "source": meta.get("source", "unknown"),
            "page": meta.get("page", "unknown")
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

    except Exception:

        import traceback
        print("========== RAG ERROR ==========")
        traceback.print_exc()
        print("================================")

        return {
            "answer": "Server error occurred while processing the request.",
            "sources": []
        }
