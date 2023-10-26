# KeepItSimple      <img width="100" alt="Screenshot 2023-10-25 at 8 06 10 PM" src="https://github.com/AnkitaNambiar/keep-it-simple-ai/assets/105748980/bce6a2e9-9c9b-429d-b9e5-039e637eb4f0">


### Making Information Accessible
Keep it Simple is an AI tool designed to make written information more accessible for everyone, whether you're new to English, a young learner, or someone who faces challenges with reading due to learning disabilities. Our tool uses cutting-edge technology to transform text into a more readable, understandable, and visually accessible format, ensuring that information is within reach for everyone.  

### Pioneering Digital Accessibility in AI
                                      'For most people, technology makes things easier. 
                           But for people with disabilities, technology makes things possible.'
                                                – Mary Pat Radabaugh

Our AI-driven solution streamlines content, ensuring that it's not only accessible but also comprehensible, empowering individuals of all backgrounds and abilities to access the knowledge they need. 

We aim to make the digital realm more inclusive and information more easily digestible. Welcome to the future of digital accessibility.

![images](https://github.com/AnkitaNambiar/keep-it-simple-ai/assets/105748980/a4dbc3c9-c45c-4f8b-9fdd-81d756cb4340)
![download](https://github.com/AnkitaNambiar/keep-it-simple-ai/assets/105748980/2420e913-6615-4385-93e9-6b84d1f483fd)
![images](https://github.com/AnkitaNambiar/keep-it-simple-ai/assets/105748980/9857a86a-f5bb-4b89-908b-bdb8cabfec74)

---
## Table of Contents
1. Project Overview
2. Data
3. AI Model: Clasifier + Simplifier
4. Model Evaluation 
5. User Interface 
6. How to Use
7. About Us
8. More about Digital Accessibility 

---
## 1. Project Overview
1. Text Readability Classification: Classify the inputted text to be one of three [CEFR levels](https://www.coe.int/en/web/common-european-framework-reference-languages/level-descriptions
): Beginner, Intermediate, and Advanced. 
2. Simplify Text: Readers can choose the text to be simplified to either Beginner or Intermediate levels.
3. Inclusivity for new learners and those with learning disorders:
   - Complex material broken down into digestible portions
   - Reading formats that allow for easier reading, including Bionic Reading
   - Text-to-speech for comprehension
4. Seamless integration: User-friendly browser

## 2. Data

## 3. AI Model: Clasifier + Simplifier 

- **AI-Powered**: Utilizes the Llama 2 series models including:
    - Llama 2 7b
    - Llama 2 chat 7b
    - Llama 2 13b
    - Llama 2 chat 13b
- **Cloud Deployment**: Efficiently deployed on GCP servers ensuring optimal performance and scalability.
- **Interactive UI**: A user-friendly interface developed using Streamlit, enabling seamless interactions.

## 4. Model Evaluation
For the robust evaluation of the tool's performance, we've incorporated several methods:
1. **CEFR (Common European Framework of Reference for Languages)**: A readability index, trained on a dataset sourced from Kaggle. Using this, we generate labels for the produced text and juxtapose it against the ground truth from our evaluation set.
2. **SMOG (Simple Measure of Gobbledygook)**: Assesses the years of education required to comprehend a piece of writing.
3. **Flesch Reading Ease Score**: A test that rates text on a 100-point scale; the higher the score, the easier it is to understand the document.
4. **Additional Indices**: Incorporation of other readability indices to comprehensively gauge the model's capability in conditional text simplification.

## 5. User Interface 

## 6. How to Use

1. Access the tool via our web portal.
2. Paste or type in the content you wish to simplify.
3. Select the desired readability level.
4. View the simplified content and compare it with the original.
5. (Optional) Provide feedback for continuous model improvement.

**Getting Started for Developers:**
1. Clone the GitHub repository.
2. Ensure all dependencies are installed.
3. For local testing, run the Streamlit app.
4. For deploying on your server, modify the necessary configuration settings.

### 7. More about Digital Accessibility 



### 8. About Us

Team: 
- Ankita Nambiar
- Egehan Yorulmaz
- Lavanya Srivastava
- Prayut Jain

Conversation AI with Nick Kadochnikov @ University of Chicago M.S. in Applied Data Science 

Contributions, feedback, and improvements are always welcome. Feel free to submit pull requests or raise issues.
This project is licensed under the MIT License. Refer to the `LICENSE` file for more details.

                                    Keep It Simple. Making Information Accessible with AI. 
