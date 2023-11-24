import argparse
from datasets import load_dataset
from functools import partial
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import pandas as pd
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from helpers.chat_model_prompt_generator import LanguageLevelAssistant

PATH = "gs://kisai-data-msca310019-capstone/Text_Simplification/finetuned_llama2_responses.csv"
model_name = "meta-llama/Llama-2-7b-chat-hf" 
seed = 42


app = Flask(__name__)
CORS(app)
assistant = LanguageLevelAssistant(model_name)


# Health check route
@app.route("/isalive")
def is_alive():
    print("/isalive request")
    status_code = Response(status=200)
    return status_code

# Predict route
@app.route("/predict", methods=["POST"])
def predict():
    print("/predict request")
    req_json = request.get_json()
    context = req_json["text"]
    target_level = req_json['target_level']
    source_level = req_json["source_level"]

    instruction = f"Simplify the following context from {source_level} language level to {target_level} language level"
    simplified_text = assistant.make_inference(instruction, context)
    return jsonify({
        "simplified_text": simplified_text
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, use_reloader=False)
