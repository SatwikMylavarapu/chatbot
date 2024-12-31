import streamlit as st
import requests
import asyncio
import uuid

# Backend API URL
BACKEND_URL = 'http://127.0.0.1:5000/chat'

# Initialize session state for managing chats
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())  # Unique ID for the current chat

# Function to start a new chat
def start_new_chat():
    new_chat_id = str(uuid.uuid4())
    st.session_state.chats[new_chat_id] = []
    st.session_state.current_chat_id = new_chat_id

# Function to send a message to the backend
async def send_message():
    user_message = st.session_state.user_input.strip()
    if user_message:
        current_chat_id = st.session_state.current_chat_id
        st.session_state.chats[current_chat_id].append({"sender": "user", "text": user_message})
        
        # Send message to backend
        try:
            response = await asyncio.to_thread(requests.post, BACKEND_URL, json={"message": user_message})
            if response.status_code == 200:
                bot_reply = response.json().get("response", "Sorry, I didn't understand that.")
            else:
                bot_reply = "Failed to get a response from the server."
        except Exception as e:
            bot_reply = f"Error: {e}"

        # Append bot reply to the chat
        st.session_state.chats[current_chat_id].append({"sender": "bot", "text": bot_reply})
        
        # Clear user input field
        st.session_state.user_input = ""

# UI Layout
st.set_page_config(page_title="OneAI Chatbot", layout="wide")

# Sidebar for chat management
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>OneAI Chatbot</h2>", unsafe_allow_html=True)
    st.button("Start New Chat", on_click=start_new_chat)
    st.markdown("### Previous Chats")
    for chat_id in st.session_state.chats:
        if st.button(f"Chat {chat_id[:8]}...", key=chat_id):
            st.session_state.current_chat_id = chat_id

# Main Chat Interface
st.markdown("<h1 style='text-align: center;'>🤖 OneAI Chatbot</h1>", unsafe_allow_html=True)
st.markdown(
    """
    <style>
        body {background-color: white;}
        .message {
            border-radius: 15px;
            padding: 10px;
            margin: 5px 0;
            max-width: 70%;
            word-wrap: break-word;
        }
        .user-message {
            background-color: white;
            color: black;
            text-align: right;
            margin-left: auto;
        }
        .bot-message {
            background-color: #DCF8C6;
            color: black;
            text-align: left;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Display chat history
current_chat_id = st.session_state.current_chat_id
if current_chat_id not in st.session_state.chats:
    st.session_state.chats[current_chat_id] = []

chat_html = ""
for msg in st.session_state.chats[current_chat_id]:
    if msg["sender"] == "user":
        chat_html += f"<div class='message user-message'>{msg['text']}</div>"
    elif msg["sender"] == "bot":
        chat_html += f"<div class='message bot-message'>{msg['text']}</div>"

st.markdown(chat_html, unsafe_allow_html=True)

# Input field
st.text_input(
    "Type your message here:",
    key="user_input",
    on_change=lambda: asyncio.run(send_message()),
    placeholder="Start typing...",
)
