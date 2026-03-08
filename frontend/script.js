
async function sendMessage() {

    const input = document.getElementById("userInput");
    const chatbox = document.getElementById("chatbox");

    const message = input.value.trim();
    if (!message) return;

    // show user message
    chatbox.innerHTML += `<div class="user">You: ${message}</div>`;
    input.value = "";

    // loading message
    const loading = document.createElement("div");
    loading.className = "bot";
    loading.innerText = "Bot: Thinking...";
    chatbox.appendChild(loading);

    chatbox.scrollTop = chatbox.scrollHeight;

    try {

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: message })
        });

        const data = await response.json();

        chatbox.removeChild(loading);

        if (data.answer) {
            chatbox.innerHTML += `<div class="bot">Bot: ${data.answer}</div>`;
        } 
        else if (data.error) {
            chatbox.innerHTML += `<div class="bot">Bot: ${data.error}</div>`;
        } 
        else {
            chatbox.innerHTML += `<div class="bot">Bot: No response received.</div>`;
        }

    } catch (error) {

        chatbox.removeChild(loading);

        chatbox.innerHTML += `<div class="bot">Bot: Server error. Please try again.</div>`;

        console.error("Chat error:", error);
    }

    chatbox.scrollTop = chatbox.scrollHeight;
}

// Enter key support
document.getElementById("userInput").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});
