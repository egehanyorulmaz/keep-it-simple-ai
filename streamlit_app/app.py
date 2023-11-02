from flask import Flask, request, jsonify
import os
import ktrain
from ktrain import text
import warnings
import tempfile
from google.cloud import storage
import tempfile


## IMPORTANT: Set this True to load model from GCP directly
# LOAD_GCP_MODEL_CEFR = False
LOAD_GCP_MODEL_LLM = False

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
if(1):
    from tensorflow.keras.initializers import GlorotNormal

    # Specify a seed value for GlorotNormal initializer
    initializer = GlorotNormal(seed=42)

model_dir = "./models"
if os.path.isdir(model_dir):
    model_cefr = ktrain.load_predictor(model_dir)
    
else:
    os.mkdir(model_dir)
    source_blob_name_1 = "CEFR/models/cefr_ktrain_bert/tf_model.h5"
    source_blob_name_2 = "CEFR/models/cefr_ktrain_bert/tf_model.preproc"
    
    download_blob(bucket_name, source_blob_name_1, model_dir + "/tf_model.h5")
    download_blob(bucket_name, source_blob_name_2, model_dir + "/tf_model.preproc")
    
    model_cefr = ktrain.load_predictor(model_dir)
    
##############################################################################


#############################################################################
###################  CONDITIONAL SIMPLIFICATION MODEL #######################
#############################################################################

if LOAD_GCP_MODEL_LLM:
    
    LLM_MODEL_DIR = "finetuned_models"

    model_directory_path = download_dir_blob(LLM_MODEL_DIR)
    model_path = model_directory_path + "/Llama2_finetuned.h5"
    model_simp = AutoModelForSequenceClassification.from_pretrained(model_directory_path)
        
else:
    
    model_path = '../finetuned_models/Llama2_finetuned.h5' ## point this to the correct directory
    
    if os.path.isdir(model_path):
        model_simp = AutoModelForSequenceClassification.from_pretrained(model_path)
    else:
        print(f"Model '{model_path}' not found")
    
##############################################################################

## Initiate flask
app = Flask(__name__)

def get_cefr_level():
    input_text = request.json.get("user_input", "")
    prediction = model_cefr.predict(input_text)
    cefr_levels = {
        'label_0': 'Elementary',
        'label_1': 'Intermediate',
        'label_2': 'Advanced'
    }
    return cefr_levels[prediction]

@app.route('/api/data', methods=['POST'])
def get_data():
    # input_text = request.json.get("user_input","") ## If error, check this
    #input_text = data.get("user_input","")
    
    # if not input_text:
    #     return jsonify({"error": "Missing 'text' field in the request."}), 400

    cefr_level = get_cefr_level()

    # cefr_level = get_cefr_level(input_text, model)

    return jsonify({"CEFR Level": cefr_level}), 200, {"Content-Type": "application/json"}



if __name__ == '__main__':
    app.run(host = 'localhost',port='8501',debug=False)
    
########################### ON THE TERMINAL ###############

## Terminal 1
# > python app.py

## Terminal 2

### If ngrok not downloaded, while setting up new cluster
# > wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
# > unzip ngrok-stable-linux-amd64.zip

# > ./ngrok http 5000 
# and use the generated url in your streamlit