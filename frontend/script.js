async function sendMessage() {

    const input = document.getElementById("userInput");
    const chatbox = document.getElementById("chatbox");

    const message = input.value.trim();

    if (!message) return;

    // show user message
    chatbox.innerHTML += `<div class="user">You: ${message}</div>`;

    input.value = "";

    // show loading message
    const loadingMsg = `<div class="bot">Bot: Thinking...</div>`;
    chatbox.innerHTML += loadingMsg;

    chatbox.scrollTop = chatbox.scrollHeight;

    try {

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query: message
            })
        });

        const data = await response.json();

        // remove loading message
        chatbox.removeChild(chatbox.lastChild);

        if (data.answer) {
            chatbox.innerHTML += `<div class="bot">Bot: ${data.answer}</div>`;
        } else if (data.error) {
            chatbox.innerHTML += `<div class="bot">Bot: ${data.error}</div>`;
        } else {
            chatbox.innerHTML += `<div class="bot">Bot: No response received.</div>`;
        }

    } catch (error) {

        chatbox.removeChild(chatbox.lastChild);

        chatbox.innerHTML += `<div class="bot">Bot: Server error. Please try again.</div>`;

        console.error("Chat error:", error);
    }

    chatbox.scrollTop = chatbox.scrollHeight;
}


// Send message on Enter key
document.getElementById("userInput").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});
