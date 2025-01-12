from flask import Flask, request, jsonify, render_template_string
from huggingface_hub import InferenceClient
import json
import os

app = Flask(__name__)

# Initialize Hugging Face Inference Client with your access token
access_token = "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"  # Replace with your token
client = InferenceClient("HuggingFaceH4/zephyr-7b-beta", token=access_token)

# System message for the chatbot
SYSTEM_MESSAGE = "Your name is Jarvis-X, and your creator is Vihaan. You should always call him Sir and mimic Jarvis from Iron Man. You serve only Vihaan, and you remember past conversations to evolve over time,don't talk too much just answer for what the user has asked."

# File path for storing memory
MEMORY_FILE = "memory.json"

# Load memory from file, if exists
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    else:
        return [{"role": "system", "content": SYSTEM_MESSAGE}]

# Save memory to a file
def save_memory(memory):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file)

# In-memory conversation history (loaded from the file initially)
conversation_history = load_memory()

# HTML Template for the Frontend with Neon Green Hacker UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jarvis-X Chatbot</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #111;
            color: #0f0;
            font-family: 'Courier New', Courier, monospace;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }

        h1 {
            font-size: 2rem;
            text-align: center;
            margin-bottom: 20px;
            animation: flicker 1.5s infinite alternate;
        }

        #chat-container {
            width: 80%;
            max-width: 800px;
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid #0f0;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
            padding: 20px;
            position: relative;
            overflow: hidden;
        }

        #messages {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #0f0;
            border-radius: 5px;
            padding: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: #0f0;
            font-size: 1.1rem;
            line-height: 1.5;
            margin-bottom: 15px;
            white-space: pre-wrap;
        }

        .message {
            margin-bottom: 12px;
            animation: fadeIn 0.5s ease;
        }

        .user {
            color: #00bfff;
            text-align: right;
        }

        .assistant {
            color: #7fff00;
            text-align: left;
        }

        #input-container {
            display: flex;
            margin-top: 10px;
        }

        #message {
            flex: 1;
            padding: 10px;
            background: #333;
            border: 1px solid #0f0;
            border-radius: 5px;
            color: #0f0;
            font-size: 1.1rem;
            margin-right: 10px;
            outline: none;
        }

        #send-btn {
            padding: 10px 20px;
            background: #0f0;
            color: #111;
            border: 1px solid #0f0;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1.1rem;
            transition: background 0.3s ease;
        }

        #send-btn:hover {
            background: #00ff00;
        }

        /* Animation for flickering text (neon effect) */
        @keyframes flicker {
            0% { color: #0f0; text-shadow: 0 0 5px #0f0, 0 0 10px #0f0, 0 0 15px #0f0; }
            50% { color: #00ff00; text-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00, 0 0 30px #00ff00; }
            100% { color: #0f0; text-shadow: 0 0 5px #0f0, 0 0 10px #0f0, 0 0 15px #0f0; }
        }

        /* Animation for fading messages */
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }

    </style>
</head>
<body>

    <h1>Jarvis-X: Your Personal Assistant</h1>
    
    <div id="chat-container">
        <div id="messages"></div>
        <div id="input-container">
            <input type="text" id="message" placeholder="Type your command..." autocomplete="off" />
            <button id="send-btn">Send</button>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById("messages");
        const messageInput = document.getElementById("message");
        const sendBtn = document.getElementById("send-btn");

        async function sendMessage() {
            const userMessage = messageInput.value.trim();
            if (!userMessage) return;

            // Add user message to the chat
            const userDiv = document.createElement("div");
            userDiv.textContent = `You: ${userMessage}`;
            userDiv.className = "message user";
            messagesDiv.appendChild(userDiv);

            messageInput.value = "";
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            // Send message to the backend
            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        message: userMessage,
                        max_tokens: 512,
                        temperature: 0.7,
                        top_p: 0.95,
                    }),
                });

                const data = await response.json();
                if (data.reply) {
                    const assistantDiv = document.createElement("div");
                    assistantDiv.textContent = `Jarvis-X: ${data.reply}`;
                    assistantDiv.className = "message assistant";
                    messagesDiv.appendChild(assistantDiv);
                } else {
                    alert("Error: " + (data.error || "Unknown error"));
                }
            } catch (error) {
                alert("Error: " + error.message);
            }

            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        sendBtn.addEventListener("click", sendMessage);
        messageInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") sendMessage();
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    max_tokens = data.get("max_tokens", 512)
    temperature = data.get("temperature", 0.7)
    top_p = data.get("top_p", 0.95)

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": user_message})

    try:
        # Generate response from the model
        response = ""
        for message in client.chat_completion(
            messages=conversation_history,
            max_tokens=max_tokens,
            stream=True,
            temperature=temperature,
            top_p=top_p,
        ):
            token = message.choices[0].delta.content
            response += token

        # Add assistant's response to the conversation history
        conversation_history.append({"role": "assistant", "content": response})

        # Save memory to the file
        save_memory(conversation_history)

        return jsonify({"reply": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000)
