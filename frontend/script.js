// Select DOM elements
const chatContainer = document.getElementById("chat-container");
const inputForm = document.getElementById("input-form");
const userInput = document.getElementById("user-input");

// Scroll to bottom helper
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Add message to chat
function addMessage(content, sender = "bot") {
    const msg = document.createElement("div");
    msg.classList.add("chat-message", sender);
    msg.innerHTML = content;
    chatContainer.appendChild(msg);
    scrollToBottom();
    return msg;
}

// Smooth typing animation
async function typeMessage(element, text, delay = 20) {
    element.innerHTML = "";
    for (let i = 0; i < text.length; i++) {
        element.innerHTML += text[i];
        await new Promise((r) => setTimeout(r, delay));
        scrollToBottom();
    }
}

// Send user question to API
async function sendMessage(question) {
    const response = await fetch("/api/index", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
    });

    const data = await response.json();
    return data.answer;
}

// Handle form submit
inputForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const question = userInput.value.trim();
    if (!question) return;

    // Add user message
    addMessage(question, "user");

    // Clear input
    userInput.value = "";

    // Add bot placeholder
    const botMsg = addMessage("...", "bot");

    try {
        // Get answer from API
        const answer = await sendMessage(question);

        // Replace placeholder with typing animation
        await typeMessage(botMsg, answer, 15);
    } catch (err) {
        botMsg.innerHTML = "⚠️ Error fetching answer.";
        console.error(err);
    }
});
