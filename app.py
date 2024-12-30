from flask import Flask, request, jsonify
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

app = Flask(__name__)

# Load the model and tokenizer (this can be a custom model or pre-trained one)
model_name = "microsoft/DialoGPT-medium"  # Example model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

@app.route('/')
def home():
    return "Welcome to the chatbot API!"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    
    if user_input:
        # Encode the input and generate a response
        input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')
        chat_history_ids = model.generate(input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
        
        # Decode the response
        response = tokenizer.decode(chat_history_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
        return jsonify({'response': response})
    
    return jsonify({'error': 'No message provided'}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
