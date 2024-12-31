from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import random

app = Flask(__name__)

# Load the models and tokenizers
tokenizer_medium = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model_medium = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

tokenizer_large = AutoTokenizer.from_pretrained("microsoft/DialoGPT-large")
model_large = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-large")

# Initialize chat history (global variable)
chat_history_ids = None

def chat_with_bot(input_text):
    global chat_history_ids

    # Encode the input text
    new_user_input_ids = tokenizer_medium.encode(input_text + tokenizer_medium.eos_token, return_tensors="pt")

    # Append the new user input tokens to the chat history (if available)
    if chat_history_ids is None:
        chat_history_ids = new_user_input_ids
    else:
        chat_history_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1)

    # Generate responses from both models
    bot_output_medium_ids = model_medium.generate(
        chat_history_ids,
        max_length=150,
        pad_token_id=tokenizer_medium.eos_token_id,
        temperature=0.9,  # Increase randomness
        top_p=0.95,       # Top-p sampling for better quality
        no_repeat_ngram_size=2  # Avoid repetitive phrases
    )
    
    bot_output_large_ids = model_large.generate(
        chat_history_ids,
        max_length=150,
        pad_token_id=tokenizer_large.eos_token_id,
        temperature=0.9,
        top_p=0.95,
        no_repeat_ngram_size=2
    )
    
    # Decode and get the model responses
    bot_response_medium = tokenizer_medium.decode(bot_output_medium_ids[:, chat_history_ids.shape[-1]:][0], skip_special_tokens=True)
    bot_response_large = tokenizer_large.decode(bot_output_large_ids[:, chat_history_ids.shape[-1]:][0], skip_special_tokens=True)

    # Combine the two responses or choose one
    combined_response = combine_responses(bot_response_medium, bot_response_large)

    # Update chat history
    chat_history_ids = bot_output_large_ids  # Update with the last response

    return combined_response

def combine_responses(response_medium, response_large):
    """ Combine or select the best response from the two models. """
    # For simplicity, let's randomly choose one for now
    # You can develop a more sophisticated approach based on your needs
    return random.choice([response_medium, response_large])

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    bot_response = chat_with_bot(user_message)
    return jsonify({"response": bot_response})

if __name__ == '__main__':
    app.run(debug=True)
