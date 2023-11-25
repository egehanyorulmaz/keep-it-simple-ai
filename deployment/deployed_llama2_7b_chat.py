import argparse
from datasets import load_dataset
from functools import partial
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
import pandas as pd
from collections import defaultdict
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from helpers.chat_model_prompt_generator import LanguageLevelAssistant

### SIMPLIFICATION MODEL ###
PATH = "gs://kisai-data-msca310019-capstone/Text_Simplification/finetuned_llama2_responses.csv"
model_name = "meta-llama/Llama-2-7b-chat-hf"
seed = 42
assistant = LanguageLevelAssistant(model_name)


### HATE SPEECH DETECTION ###
tokenizer = AutoTokenizer.from_pretrained("tomh/toxigen_hatebert")
model = AutoModelForSequenceClassification.from_pretrained("tomh/toxigen_hatebert")
hatespeech_pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer)
safety_probability_threshold = 0.2


app = Flask(__name__)
CORS(app)


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

# Predict route
@app.route("/aisafety", methods=["POST"])
def ai_safety():
    print("/aisafety")
    req_json = request.get_json()
    context = req_json["text"]
    hs_predictions = hatespeech_pipe.predict(context)[0]
    
    probabilities = defaultdict()
    for output in hs_predictions:
        if output['label']=='LABEL_0':
            # HATE SPEECH PROBABILITY
            probabilities["hs_prob"] = output["score"]
        elif output['label']=='LABEL_1':
            # NOT HATE SPEECH PROBABILITY
            probabilities["non_hs_prob"] = output["score"]
    
    
    if probabilities["non_hs_prob"] - probabilities["hs_prob"] > safety_probability_threshold:
        output = "safe"
    elif probabilities["non_hs_prob"] - probabilities["hs_prob"] > 0:
        output = "not_sure_but_safe"
    else:
        output = "not_safe"
    
    return jsonify({
        "result": output})
        
        
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, use_reloader=False)
