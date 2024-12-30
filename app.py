from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = Flask(__name__)

# Load the model and tokenizer
if __name__ == '__main__':
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
    model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

    # Initialize chat history (global variable)
    chat_history_ids = None

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

    @app.route('/chat', methods=['POST'])
    def chat():
        user_message = request.json.get("message")
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        bot_response = chat_with_bot(user_message)
        return jsonify({"response": bot_response})

    # Explicitly bind to port 10000 for Render
    app.run(debug=True, host='0.0.0.0', port=10000)
