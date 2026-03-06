from vercel_runtime import VercelRequest, VercelResponse
from rag_chat import retrieve_documents, generate_answer, get_query_embedding

def handler(req: VercelRequest):
    try:
        body = req.json
        question = body.get("question", "")
        if not question:
            return VercelResponse.json({"error": "Question is required"}, status=400)

        # Get query embedding from HF API (or precompute offline)
        query_embedding = get_query_embedding(question)

        # Retrieve relevant chunks from Pinecone
        docs = retrieve_documents(query_embedding, top_k=5)

        # Generate final answer using Groq LLM
        answer = generate_answer(question, docs)

        return VercelResponse.json({"answer": answer})

    except Exception as e:
        return VercelResponse.json({"error": str(e)}, status=500)
