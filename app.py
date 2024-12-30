import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

# Initialize chat history
chat_history_ids = None

# Define the function to generate bot's response
def chat_with_bot(input_text):
    global chat_history_ids

    # Encode the input text
    new_user_input_ids = tokenizer.encode(input_text + tokenizer.eos_token, return_tensors="pt")

    # Append the new user input tokens to the chat history (if available)
    if chat_history_ids is None:
        chat_history_ids = new_user_input_ids
    else:
        chat_history_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1)

    # Generate a response with custom parameters for more dynamic replies
    bot_output_ids = model.generate(
        chat_history_ids,
        max_length=150,
        pad_token_id=tokenizer.eos_token_id,
        temperature=0.9,  # Increase randomness
        top_p=0.95,       # Top-p sampling for better quality
        no_repeat_ngram_size=2  # Avoid repetitive phrases
    )

    # Decode and get the model response
    bot_response = tokenizer.decode(bot_output_ids[:, chat_history_ids.shape[-1]:][0], skip_special_tokens=True)

    # Update chat history
    chat_history_ids = bot_output_ids

    return bot_response

# Streamlit UI
st.title("DialoGPT Chatbot")

# Input box for user to type
user_message = st.text_input("You:", "")

# Button to submit message
if st.button("Send"):
    if user_message:
        bot_response = chat_with_bot(user_message)
        st.write(f"Bot: {bot_response}")
    else:
        st.write("Please type a message!")
