var initialMessageShown = false;

function toggleChat() {
    var chatPopup = document.getElementById("chatPopup");
    var chatButton = document.querySelector(".chat-button");
    if (chatPopup.style.display === "none" || chatPopup.style.display === "") {
        chatPopup.style.display = "block";
        chatButton.style.display = "none";

        if (!initialMessageShown) {
            addMessage("Bot", "You're talking to a Gemini-powered AI assistant. Please be respectful at all times.");
            initialMessageShown = true;
        }
    } else {
        chatPopup.style.display = "none";
        chatButton.style.display = "block";
    }
}

function sendMessage() {
    var message = document.getElementById("userMessage").value;
    if (message.trim() !== "") {
        addMessage("You", message);
        document.getElementById("userMessage").value = "";

        // Send message to Flask backend
        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({message: message})
        })
        .then(response => response.json())
        .then(data => {
            addMessage("Bot", data.response);
        })
        .catch(error => console.error('Error:', error));
    }
}

function addMessage(sender, message) {
    var chatBody = document.getElementById("chatBody");
    var messageBox = document.createElement("div");
    messageBox.classList.add("message-box");

    if (sender === "Bot") {
        messageBox.classList.add("bot");
    } else if (sender === "You") {
        messageBox.classList.add("user");
    }

    messageBox.textContent = message;
    chatBody.appendChild(messageBox);
    chatBody.scrollTop = chatBody.scrollHeight;
}
