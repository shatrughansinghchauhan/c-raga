from flask import Flask, request, jsonify, send_from_directory
from rag_chat import rag_chat
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR)


@app.route("/")
def serve_ui():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/script.js")
def serve_js():
    return send_from_directory(FRONTEND_DIR, "script.js")


@app.route("/style.css")
def serve_css():
    return send_from_directory(FRONTEND_DIR, "style.css")


@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()
        query = data.get("query")

        print("USER QUERY:", query)

        if not query:
            return jsonify({"error": "Query missing"}), 400

        result = rag_chat(query)

        return jsonify(result)

    except Exception as e:

        print("CHAT ROUTE ERROR:", str(e))

        return jsonify({
            "error": "Server failed to process request"
        }), 500


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
