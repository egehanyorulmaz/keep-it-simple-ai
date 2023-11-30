import argparse
from datasets import load_dataset
from functools import partial
import os
import time
import torch
from torch.nn.functional import softmax
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoTokenizer, AutoModelForSequenceClassification#, TextClassificationPipeline
from peft import AutoPeftModelForCausalLM
import pandas as pd
from collections import defaultdict
from flask import Flask, request, jsonify
import os
import ktrain
from ktrain import text
from ktrain import load_predictor as lp
import warnings
import tempfile
from google.cloud import storage
import tempfile
from flask_cors import CORS
import tensorflow as tf
from helper_func.chat_model_prompt_generator import LanguageLevelAssistant

##################### Setup GCP connection  #################################

bucket_name = "kisai-data-msca310019-capstone"


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from COS bucket."""
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    
#############################################################################
######################  CEFR CLASSIFIER MODEL ###############################
#############################################################################

## Set the initializer to ignore the warning generated during model load
# if(1):
#     from tensorflow.keras.initializers import GlorotNormal

#     # Specify a seed value for GlorotNormal initializer
#     initializer = GlorotNormal(seed=42)

model_dir = "./model/CEFR"
if os.path.isdir(model_dir):
    
    print("Loading CEFR model...")
    model_cefr = ktrain.load_predictor(model_dir)
    print("Done")
    
else:
    os.mkdir(model_dir)
    source_blob_name_1 = "CEFR/models/cefr_ktrain_bert/tf_model.h5"
    source_blob_name_2 = "CEFR/models/cefr_ktrain_bert/tf_model.preproc"
    
    download_blob(bucket_name, source_blob_name_1, model_dir + "/tf_model.h5")
    download_blob(bucket_name, source_blob_name_2, model_dir + "/tf_model.preproc")
    
    print("Loading CEFR model...")
    model_cefr = ktrain.load_predictor(model_dir)
    print("Done")
    

#############################################################################
######################  SIMPLIFICATION MODEL ###############################
#############################################################################

model_dir = "./model/Llama2_7b"
model_name = "meta-llama/Llama-2-7b-chat-hf"
seed = 42
# kisai-data-msca310019-capstone/Text_Simplification/models/kisai-llama-2-7b-chat/version_1/final_checkpoint
if os.path.isdir(model_dir):
    
    print("Loading simplification model...")
    assistant = LanguageLevelAssistant(model_name, model_dir)
    print("Done")
    
else:
    os.mkdir(model_dir)
    source_blob_name_1 = "Text_Simplification/models/kisai-llama-2-7b-chat/version_1/final_checkpoint/adapter_model.bin"
    source_blob_name_2 = "Text_Simplification/models/kisai-llama-2-7b-chat/version_1/final_checkpoint/adapter_config.json"
    source_blob_name_3 = "Text_Simplification/models/kisai-llama-2-7b-chat/version_1/final_checkpoint/README.md"

    download_blob(bucket_name, source_blob_name_1, model_dir + "/adapter_model.bin")
    download_blob(bucket_name, source_blob_name_2, model_dir + "/adapter_config.json")
    download_blob(bucket_name, source_blob_name_3, model_dir + "/README.md")
    
    print("Loading simplification model...")
    assistant = LanguageLevelAssistant(model_name, model_dir)
    print("Done")




#############################################################################
######################  HATE SPEECH MODEL ###############################
#############################################################################

print("Loading HateSpeech model...")
tokenizer = AutoTokenizer.from_pretrained("tomh/toxigen_hatebert")
model = AutoModelForSequenceClassification.from_pretrained("tomh/toxigen_hatebert")
# hatespeech_pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer)
safety_probability_threshold = 0.2
print("Done")

## API Endpoints for each model #############################################
app = Flask(__name__)
CORS(app)


# Health check route
@app.route("/isalive")
def is_alive():
    print("/isalive request")
    status_code = Response(status=200)
    return status_code

# Simplify route
@app.route("/simplify", methods=["POST"])
def predict():
    print("/simplify request")

    # Start the timer
    start_time = time.time()

    req_json = request.get_json()
    context = req_json["text"]
    target_level = req_json['target_level']
    source_level = req_json["source_level"]

    instruction = f"Simplify the following context from {source_level} language level to {target_level} language level"
    simplified_text = assistant.make_inference(instruction, context)
    print("Simplification response generated")

    # End the timer
    end_time = time.time()

    # Calculate and print the elapsed time
    elapsed_time = end_time - start_time
    print(f"Process took {elapsed_time:.2f} seconds")

    return jsonify({
        "simplified_text": simplified_text
    })

# AISafety route
@app.route("/aisafety", methods=["POST"])
def ai_safety():
    print("/aisafety request")
    req_json = request.get_json()
    context = req_json["text"]

    # Tokenize the input text
    inputs = tokenizer(context, return_tensors="pt", truncation=True, max_length=1028)

    # Get model predictions
    with torch.no_grad():
        outputs = model(**inputs)

    # Apply softmax to logits to get probabilities
    probabilities = softmax(outputs.logits, dim=1)[0]

    # Initialize a defaultdict for probabilities
    prob_dict = defaultdict(float)

    # Assuming LABEL_0 is for hate speech and LABEL_1 is for non-hate speech
    prob_dict["hs_prob"] = probabilities[0].item()  # Hate speech probability
    prob_dict["non_hs_prob"] = probabilities[1].item()  # Not hate speech probability

    safety_probability_threshold = 0.5  # Define your threshold here

    if prob_dict["non_hs_prob"] - prob_dict["hs_prob"] > safety_probability_threshold:
        output = "safe"
    elif prob_dict["non_hs_prob"] - prob_dict["hs_prob"] > 0:
        output = "not_sure_but_safe"
    else:
        output = "not_safe"
    
    print(f"The input is {output}") 
    return jsonify({"result": output})

# def ai_safety():
#     print("/aisafety request")
#     req_json = request.get_json()
#     context = req_json["text"]
#     hs_predictions = hatespeech_pipe.predict(context)[0]
    
#     probabilities = defaultdict()
#     for output in hs_predictions:
#         if output['label']=='LABEL_0':
#             # HATE SPEECH PROBABILITY
#             probabilities["hs_prob"] = output["score"]
#         elif output['label']=='LABEL_1':
#             # NOT HATE SPEECH PROBABILITY
#             probabilities["non_hs_prob"] = output["score"]
    
    
#     if probabilities["non_hs_prob"] - probabilities["hs_prob"] > safety_probability_threshold:
#         output = "safe"
#     elif probabilities["non_hs_prob"] - probabilities["hs_prob"] > 0:
#         output = "not_sure_but_safe"
#     else:
#         output = "not_safe"
    
#     return jsonify({
#         "result": output})

# CEFR classification route     
@app.route('/cefr', methods=['POST'])
def get_data():
    print("/cefr request")

    input_text = request.json.get("user_input", "")
    prediction = model_cefr.predict(input_text)
    cefr_levels = {
        'label_0': 'Beginner',
        'label_1': 'Intermediate',
        'label_2': 'Advanced'
    }
    print("Classification response generated")
    return jsonify({"CEFR Level": cefr_levels[prediction]})
        
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, use_reloader=False)
