from flask import Flask, request, jsonify
import os
import ktrain
from ktrain import text
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='keras.initializers')

## Load model
### NOTE: DO not import model in the function,always import it outside 
model_path = './model'
model = ktrain.load_predictor(model_path)

## Initiate flask
app = Flask(__name__)




# def get_data():
#     input_text = request.json.get("user_input", "")
#     prediction = model.predict(input_text)
#     cefr_levels = {
#         'label_0': 'Elementary',
#         'label_1': 'Intermediate',
#         'label_2': 'Advanced'
#     }
#     result = cefr_levels[prediction]
#     return jsonify({"CEFR Level": result})
  




    ## Route the flask to app
# @app.route('/api/data', methods = ['POST']) ## methods is to communicate and get input from the streamlit app

# # ## CEFR model call
# def get_cefr_level(text):
#     prediction = model.predict(text)
#     # Map the prediction to CEFR levels (customize this mapping as needed)
#     cefr_levels = {
#         'label_0':'Elementary',
#         'label_1':'Intermediate',
#         'label_2':'Advanced'
#                 }
#     # Return the CEFR level based on the prediction
#     return cefr_levels[prediction]

def get_cefr_level():
    input_text = request.json.get("user_input", "")
    prediction = model.predict(input_text)
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

    return jsonify({"CEFR Level": cefr_level})



if __name__ == '__main__':
    app.run(host = 'localhost',port='5000',debug=False)