# import sys
# import subprocess

# # Get the argument from the command line
# ngrok_url = sys.argv[1]

# # Set the environment variable
# os.environ['NGROK_URL'] = ngrok_url

# # Run the Streamlit app
# subprocess.run(["streamlit", "run", "app_deco.py"])

import subprocess
import os
import time
import requests

def start_flask_app():
    # Start the Flask server on a separate process
    return subprocess.Popen(["python", "server.py"])

def start_ngrok():
    # Start Ngrok
    ngrok_process = subprocess.Popen(["./ngrok", "start", "--all", "-config", "ngrok.yml"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3)  # Wait for Ngrok to initialize
    return ngrok_process

def get_ngrok_url():
    # Fetch the Ngrok tunnel information using Ngrok's API
    tunnels = requests.get("http://localhost:4040/api/tunnels").json()["tunnels"]
    flask_url = next(tunnel['public_url'] for tunnel in tunnels if tunnel['config']['addr'] == 'http://localhost:5000')
    streamlit_url = next(tunnel['public_url'] for tunnel in tunnels if tunnel['config']['addr'] == 'http://localhost:8501')
    return flask_url, streamlit_url

def run_streamlit_app(flask_url):
    # Set the Flask URL as an environment variable
    os.environ["FLASK_URL"] = flask_url
    # Run the Streamlit app
    subprocess.run(["streamlit", "run", "app_deco.py"])

if __name__ == "__main__":
    flask_process = start_flask_app()
    ngrok_process = start_ngrok()

    try:
        flask_url, streamlit_url = get_ngrok_url()
        print(f"Flask URL: {flask_url}")
        print(f"Streamlit URL: {streamlit_url}")
        run_streamlit_app(flask_url)

    finally:
        flask_process.terminate()
        ngrok_process.terminate()
