import streamlit as st
import requests

# Streamlit frontend for chatbot interaction
st.title("Chatbot")

# Display chat input
user_input = st.text_input("You: ", "")

if user_input:
    # Send message to Flask API
    response = requests.post("http://localhost:8080/chat", json={"message": user_input})
    
    if response.status_code == 200:
        chatbot_response = response.json().get('response')
        st.write(f"Chatbot: {chatbot_response}")
    else:
        st.write("Error: Could not get response from chatbot API.")
