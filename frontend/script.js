const input = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const messages = document.getElementById("chatMessages");

sendBtn.addEventListener("click", sendMessage);

async function sendMessage() {
  const question = input.value.trim();
  if (!question) return;

  appendMessage("You", question);
  input.value = "";

  const res = await fetch("/api/index", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });

  const data = await res.json();
  appendMessage("Bot", data.answer || "No answer returned");
}

function appendMessage(sender, text) {
  const div = document.createElement("div");
  div.classList.add("message");
  div.innerHTML = `<b>${sender}:</b> ${text}`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}
