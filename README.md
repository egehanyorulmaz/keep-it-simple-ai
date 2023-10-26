# KeepItSimple: AI-Powered Text Simplification Tool

### Making Information Accessible
Keep it Simple is an AI tool designed to make written information more accessible for everyone, whether you're new to English, a young learner, or someone who faces challenges with reading due to learning diabilities. Our tool uses cutting-edge technology to transform text into a more readable, understandable, and visually accessible format, ensuring that information is within reach for everyone.  

## Overview
KeepItSimple is a cutting-edge tool that conditionally simplifies any provided text to a user-specified readability level. Leveraging the power of Large Language Models (LLMs) and specifically fine-tuning on Llama 2 models with various capacities, our tool aims to make content more accessible to everyone.

## Key Features
- **Conditional Text Simplification**: Adjust the readability level of any given text to either Elementary, Intermediate, or Advanced.
- **AI-Powered**: Utilizes the Llama 2 series models including:
    - Llama 2 7b
    - Llama 2 chat 7b
    - Llama 2 13b
    - Llama 2 chat 13b
- **Cloud Deployment**: Efficiently deployed on GCP servers ensuring optimal performance and scalability.
- **Interactive UI**: A user-friendly interface developed using Streamlit, enabling seamless interactions.

## Evaluation Metrics
For the robust evaluation of the tool's performance, we've incorporated several methods:
1. **CEFR (Common European Framework of Reference for Languages)**: A readability index, trained on a dataset sourced from Kaggle. Using this, we generate labels for the produced text and juxtapose it against the ground truth from our evaluation set.
2. **SMOG (Simple Measure of Gobbledygook)**: Assesses the years of education required to comprehend a piece of writing.
3. **Flesch Reading Ease Score**: A test that rates text on a 100-point scale; the higher the score, the easier it is to understand the document.
4. **Additional Indices**: Incorporation of other readability indices to comprehensively gauge the model's capability in conditional text simplification.

## How to Use
1. Access the tool via our web portal.
2. Paste or type in the content you wish to simplify.
3. Select the desired readability level.
4. View the simplified content and compare it with the original.
5. (Optional) Provide feedback for continuous model improvement.

## Getting Started for Developers
1. Clone the GitHub repository.
2. Ensure all dependencies are installed.
3. For local testing, run the Streamlit app.
4. For deploying on your server, modify the necessary configuration settings.

## Contribution
Contributions, feedback, and improvements are always welcome. Feel free to submit pull requests or raise issues.

## License
This project is licensed under the MIT License. Refer to the `LICENSE` file for more details.

---

### Team Members
- Ankita Nambiar
- Egehan Yorulmaz
- Lavanya Srivastava
- Prayut Jain

We believe in the power of AI to make content universally accessible and comprehendible. KeepItSimple is our step towards that vision.

