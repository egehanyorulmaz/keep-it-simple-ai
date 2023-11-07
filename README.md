# KeepItSimple

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
1. Text Readability Classification: Classify the inputted text to be one of three [Common European Framework of Reference for Languages (CEFR) levels](https://www.coe.int/en/web/common-european-framework-reference-languages/level-descriptions
): Beginner, Intermediate, and Advanced. 
2. Simplify Text: Readers can choose the text to be simplified to either Beginner or Intermediate levels.
3. Inclusivity for new learners and those with learning disorders:
   - Complex material broken down into digestible portions
   - Reading formats that allow for easier reading, including Bionic Reading
   - Text-to-speech for comprehension
4. Seamless integration: User-friendly browser

## 2. Data
We collected the open source data available in multiple levels of readability as defined by the "Common European Framework of Reference for Languages (CEFR)". Its important to understand the structure of this data, which has the same text rewritten in different levels of readability. From the source of these datasets, there are 6 levels in which the text is available, but we map it to 3 major levels defined by CEFR as C-B-A corresponding to Advanced-Intermediate-Beginner.

### 2.1 For training our CEFR models 
We structured our dataset such that the each text (from a set of same text at 3 different readability levels) is treated as individual data point with labels in the set {C, B, A}. 

### 2.2 For fine tuning LLMs
The aim of fine tuning is unidirectional where the model is to be trained to simplify ONLY. The data is structured such that from a set of same text at 3 readability levels, we create 3 data observations; the higher level text is treated as context and the lower level as target. The 3 generated subsamples pairs of context-target are 3-2, 3-1, and 2-1.

Sources of data: NewsInLevels, OneStopEnglishCorpus, Wiki, and Newsela.

## 3. AI Model: Clasifier + Simplifier 
In the domain of language learning and content adaptation, the ability to classify and simplify texts according to language proficiency levels is essential. 
Below, we present the modeling designed to classify texts into one of three predefined CEFR levels—Basic, Intermediate, and Advanced—and subsequently simplifies the text according to the target level. The modeling operates in two main components: a text classifier and a text simplifier. The classifier uses a ktrain BERT model classification model, while the simplifier is based on variants of the llama-2 language model. We demonstrate the efficiency and accuracy of the tool in both classification and simplification tasks.

### 3.1 Text Classifier
![image](https://github.com/egehanyorulmaz/keep-it-simple-ai/assets/48676337/12558601-2e20-4bb3-90f7-d794df768865)

**3.1.1 Model Selection and Training**
For the text classification component, we employed the ktrain BERT (Bidirectional Encoder Representations from Transformers) model, a sequence-to-sequence model known for its efficacy in handling natural language processing tasks. The model was fine-tuned on a dataset comprising texts labeled with CEFR levels. The importance of accurate labeling cannot be overstated, as it ensures the model's effectiveness in classifying texts correctly.

### 3.2 Text Simplifier
![image](https://github.com/egehanyorulmaz/keep-it-simple-ai/assets/48676337/3ca34faa-2807-4dc5-927c-19e99975e69e)
**3.2.1 Label Embedding**  \
For model to be contextually aware of the language level of the provided text, the mentioned text classifier model is utilized to predict the language level of the user-inputted text , and subsequently embed the predicted source level as well as target level to the prompt. Labels embedded in the prompts were then fed to the Large Language Model for further fine-tuning on this newly introduced conditional down-stream task. 

**3.2.2 Model Selection**  \
For the text simplification task, we selected the llama-2 language model. We evaluated four variants of the llama-2 model: the 7B and 13B standard models, and the Chat model variants with 7B and 13B configurations. Several experiments are conducted across different large language models from the Open LLM Leaderboard. Llama-2 model is preferred for the superior capabilities among other language models, and more resource availability online.  

**3.2.3 Fine-Tuning with llora and qlora**  \
For fine-tuning, we utilized llora and qlora techniques. Qlora notably enhanced the processing speed and significantly reduced the resources needed for text simplification without compromising quality. 4-bit and 8-bit quantizations are chosen based on the limited resource availability.


## 4. Model Evaluation
For the robust evaluation of the tool's performance, we've incorporated several methods:
1. **CEFR (Common European Framework of Reference for Languages)**: A readability index, trained on a dataset sourced from Kaggle. Using this, we generate labels for the produced text and juxtapose it against the ground truth from our evaluation set.
2. **SMOG (Simple Measure of Gobbledygook)**: Assesses the years of education required to comprehend a piece of writing.
3. **Flesch Reading Ease Score**: A test that rates text on a 100-point scale; the higher the score, the easier it is to understand the document.
4. **Additional Indices**: Incorporation of other readability indices to comprehensively gauge the model's capability in conditional text simplification.

   
|      Model       | CEFR Accuracy |     SMOG     | Flesch Reading Ease | GPT-4 Judge         |
| :--------------: | :-----------: | :----------: | :-----------------: | :-----------------: |
| Llama-2-7b       | VAL1          |              |                     |                     |
| Llama-2-13b      | VAL2          |              |                     |                     |
| Llama-2-7b-chat  | VAL2          |              |                     |                     |
| Llama-2-13b-chat | VAL2          |              |                     |                     |
| Mistral-7b       | VAL2          |              |                     |                     |


## 5. User Interface 
Cloud Deployment: Efficiently deployed on GCP servers ensuring optimal performance and scalability.
A user-friendly interface developed using Streamlit, enabling seamless interactions.

Accessibility Features:

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
