async function sendMessage() {

    const input = document.getElementById("userInput")
    const chatbox = document.getElementById("chatbox")

    const message = input.value

    if (!message) return

    chatbox.innerHTML += `<div class="user">You: ${message}</div>`

    input.value = ""

    const response = await fetch("/chat", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            query: message
        })
    })

    const data = await response.json()

    chatbox.innerHTML += `<div class="bot">Bot: ${data.answer}</div>`

    chatbox.scrollTop = chatbox.scrollHeight
}
