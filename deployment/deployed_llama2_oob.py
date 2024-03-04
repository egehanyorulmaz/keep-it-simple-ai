import argparse
from datasets import load_dataset
from functools import partial
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import pandas as pd
from flask import Flask, request, Response, jsonify
from flask_cors import CORS

def load_model(model_name):
    n_gpus = torch.cuda.device_count()
    max_memory = f'{15960}MB'

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto", # dispatch efficiently the model on the available ressources
        max_memory = {i: max_memory for i in range(n_gpus)},
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=True)

    # Needed for LLaMA tokenizer
    tokenizer.pad_token = tokenizer.eos_token

    return model, tokenizer

def make_inference(instruction, context = None):
    if context:
        prompt = f"Below is an instruction that describes a task, paired with an input that provides further context.\n\n### Instruction: \n{instruction}\n\n### Input: \n{context}\n\n### Response: \n"
    else:
        prompt = f"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction: \n{instruction}\n\n### Response: \n"
    
    inputs = tokenizer(prompt, return_tensors="pt", return_token_type_ids=False).to("cuda:0")
    outputs = model.generate(**inputs, max_new_tokens=150)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
    # New code to trim output
    response = response.split('End of context:')[0]
    
    filtered_response = response.split("End of response:")[0].split("Response:")[1]
    
    # display(Markdown(response))
    return filtered_response

PATH = "gs://XXX/Text_Simplification/finetuned_llama2_responses.csv"
model_name = "meta-llama/Llama-2-7b-hf" 
seed = 42

data = pd.read_csv(PATH)
model, tokenizer = load_model(model_name)


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
    simplified_text = make_inference(instruction=instruction, context=context)
    return jsonify({
        "simplified_text": simplified_text
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, use_reloader=False)