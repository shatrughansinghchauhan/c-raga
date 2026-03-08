from flask import Flask, request, jsonify, send_from_directory
from rag_chat import rag_chat
import os

app = Flask(__name__, static_folder="../frontend")


@app.route("/")
def serve_ui():
    return send_from_directory("../frontend", "index.html")


@app.route("/script.js")
def serve_js():
    return send_from_directory("../frontend", "script.js")


@app.route("/style.css")
def serve_css():
    return send_from_directory("../frontend", "style.css")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    query = data.get("query")

    if not query:
        return jsonify({"error": "Query missing"}), 400

    result = rag_chat(query)

    return jsonify(result)


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
