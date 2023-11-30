
## Make necessary imports ######################################################
import streamlit as st
import os
import requests
from gtts import gTTS
from io import BytesIO
from streamlit.config import set_option
import re
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
import markdown
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
import markdown2
import base64


## TODOs:
# 1) Define a placeholder input text and hardcode the response
# 2) Integrate AI Safety model
# 3) Error exception handling in case 
#    a) source==target level
#    b) Generated response == input text
#    c) AI Safety errors
#     d) No response exception
# 4) Look into a more robust regex substitute
# 5) Ctrl+Enter -> Is this necessary in the input?


## Define helper functions #####################################################

# Simplify text function (dummy logic, can be enhanced)
# UPDATE: Now replaced with original hosted simplification model
# def simplify_text(text, reading_level):
#     return text  # No change currently

pattern = re.compile(r"as follows:(.*?)(</s>|$)", flags=re.DOTALL)

def clean_simplified_text(response_data):
    # Check if 'simplified_text' is in the response and is not empty
    if 'simplified_text' in response_data and response_data['simplified_text'].strip():
        # Split the text on [/INST] and take the last part
        split_text = response_data['simplified_text'].split('[/INST]')
        last_part = split_text[-1] if split_text else ''

        # Remove line breaks from the last part
        last_part = last_part.replace('\n', ' ')  # Replace '\n' with a space

        # Use the compiled regex pattern to find all matches in the last part
        matches = pattern.findall(last_part.strip())
        if matches:
            # Take the first match's group and strip it of whitespace
            cleaned_text = matches[0][0].strip()
            # Optionally, remove line breaks from the cleaned text as well
            cleaned_text = cleaned_text.replace('\n', ' ')  # Replace '\n' with a space
            return cleaned_text
        else:
            # Handle cases where no match is found in the last part
            return "No simplified text found or format is incorrect in the last part."
    else:
        # Handle cases where 'simplified_text' is not in the response or is empty
        return "Invalid response: 'simplified_text' not found or empty."

    
### Bionic Reading Function
def bionic_read(text):
    words = text.split()
    formatted_words = []
    for word in words:
        word_length = len(word)
        half_length = word_length // 2
        if word_length % 2 == 0:
            formatted_word = f"**{word[:half_length]}**{word[half_length:]}"
        else:
            formatted_word = f"**{word[:half_length+1]}**{word[half_length+1:]}"    
        formatted_words.append(formatted_word)
    return ' '.join(formatted_words)

def unbionic_read(text):
    # Remove Markdown bold syntax (**)
    unformatted_text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    return unformatted_text

### Text to Speech Function
def text_to_speech(text):
    try:
        sound_file = BytesIO()
        tts = gTTS(text, lang='en')
        tts.write_to_fp(sound_file)
        sound_file.seek(0)
        return sound_file
    except Exception as e:
        print("Error in text_to_speech:", e)
        return None 

def update_text_display():
    print_text = st.session_state.get('simplified_text', '')
    print_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', print_text)
    render_markdown_in_box_output(print_text, 
                                  st.session_state.custom_view_settings['font_size'], 
                                  st.session_state.custom_view_settings['font_type'], 
                                  st.session_state.custom_view_settings['text_color'], 
                                  st.session_state.custom_view_settings['bg_color'])


### Text output rendering function
def render_markdown_in_box_output(content, font_size=16, font_type='Arial', text_color="#000000", bg_color="#FFFFFF"):
    box_style = f"""
        display: block;
        width: 100%;
        height: 200px;
        padding: 10px;
        margin-top: 18px;
        background-color: {bg_color};
        color: {text_color};
        border: 1px solid #ccc;
        border-radius: 1px;
        overflow-y: scroll;
        white-space: pre-wrap;
        font-size: {font_size}px;
        font-family: {font_type};
    """
    st.markdown(f"<div style='{box_style}'>{content}</div>", unsafe_allow_html=True)


    
### Functions for Download PDF Button
def markdown_to_html(markdown_text):
    return markdown.markdown(markdown_text)

def convert_html_to_pdf(html_text, pdf_filename):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = [Paragraph(html_text, styles["Normal"])]
    doc.build(story)
    with open(pdf_filename, "wb") as f:
        f.write(buffer.getbuffer())

def generate_pdf_download_link(text, filename="output.pdf"):
    html_text = markdown_to_html(text)
    convert_html_to_pdf(html_text, filename)
    with open(filename, "rb") as f:
        st.download_button("Download PDF", f, file_name=filename)

## Set page config ############################################################
st.set_page_config(
    page_title='Keep It Simple',
    layout='wide',
    # theme={'primaryColor':'#FF4B4B'}
)
st.title('KeepItSimple-AI')
st.markdown("""<br>""", unsafe_allow_html=True)

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# def set_background(png_file, opacity=0.1):
#     bin_str = get_base64(png_file)
#     page_bg_img = '''
#     <style>
#     .stApp {
#     background-image: url("data:image/png;base64,%s");
#     background-size: cover;
#     opacity: 0.1;
#     }
#     </style>
#     ''' % bin_str
#     st.markdown(page_bg_img, unsafe_allow_html=True)
    
def set_background(png_file, opacity=0.5):
    bin_str = get_base64(png_file)
    page_bg_img = f'''
    <style>
    .backgroundLayer {{
        position: fixed;
        top: 0; left: 0;
        right: 0; bottom: 0;
        z-index: -1;
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        opacity: {opacity}; /* Adjust the opacity here */
    }}
    </style>

    <div class="backgroundLayer"></div>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)
    
# set_background('./Banner_streamlit.png')

# Tabs
default, tab1, tab2, tab3 = st.tabs(["Home", "How to Use", "How it Works", "About Us"])

with default:
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    /* Main font style */
    body {
        font-family: 'Arial', sans-serif;
    }
    /* Custom styling for the buttons */
    .stButton>button {
        color: white;
        background-color: #FF4B4B;
        border: none;
        border-radius: 5px;
        padding: 10px 24px;
        margin: 10px 0;
        float: right;
    }
    /* Custom styling for st.DownloadButton */
    .download-button>button {
        color: white;
        background-color: #4CAF50;  /* Change the color as needed */
        border: none;
        border-radius: 5px;
        padding: 10px 24px;
        margin: 10px 0;
        float: right;
    }
    /* Custom styling for the text areas */
    .stTextArea {
        border-radius: 5px;
    }
    /* Custom styling for the selectbox */
    .stSelectbox {
        border-radius: 5px;
    }
    /* Custom styling for expander */
    .stExpander {
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)


    ### Headings style
    heading_style = "color: darkblue; font-size: 1.4em; font-weight: 600;"


    ### Initialize session state for simplified text 
    if 'simplified_text' not in st.session_state:
        st.session_state.simplified_text = ""
        
    if 'sound_file' not in st.session_state:
        text_for_speech = "Input text to begin simplifying."
        st.session_state.sound_file = text_to_speech(text_for_speech)
        
    if 'is_input_present' not in st.session_state:
        st.session_state.is_input_present = False
    
    if 'original_text' not in st.session_state:
        st.session_state.original_text = st.session_state.simplified_text
        
    if 'custom_view_settings' not in st.session_state:
        st.session_state.custom_view_settings = {
            'font_size': 16,
            'font_type': 'Arial',
            'text_color': '#000000',
            'bg_color': '#FFFFFF'
        }
    
    reading_level_prediction = {"CEFR Level": "Unknown"}
    
    ### Add session state variables for custom view settings
    if 'custom_view_settings' not in st.session_state:
        custom_view_settings = {
            'font_size': 16,
            'font_type': 'Arial',
            'text_color': "#000000",
            'bg_color': "#FFFFFF"
        }

    ### Initialize other flags
    safe_flag= True
    # text_simplified = False 
    
    ### Server URL - Has to be updated when the server is restarted
    flask_url = os.environ["FLASK_URL"]
    
    ## Main app code ##############################################################

    ####### Section 1: I/O boxes ##########
    #######################################

    # Side by side input and output text areas
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        # st.markdown(f"<p style='{heading_style}'>  ORIGINAL TEXT</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 24px; font-weight: bold;'>ORIGINAL TEXT</p>", unsafe_allow_html=True)
        st.markdown("""
        <style>
        .stTextArea [data-baseweb=base-input] {
            background-color: #E7EDFB; 
            -webkit-text-fill-color: black; 
        }
        </style>
        """, unsafe_allow_html=True)

        user_input = st.text_area("",placeholder = "Enter or paste your text here to simplify...", 
                                  height=200, 
                                  key="input_text_area",
                                  label_visibility = "collapsed")

        # Update the variable based on user input
        is_input_present = bool(user_input.strip())

        

        col1a, col1b = st.columns([2,1])
        level_options = ['Beginner', 'Intermediate']

        with col1a:
            if is_input_present:
                # CEFR Level Prediction
                url_cefr = flask_url + '/cefr'
                response = requests.post(url_cefr, json={"user_input": user_input})
                
                if response.status_code == 200:
                    reading_level_prediction = response.json()
                    st.markdown(f"<h5 style='text-align: left; color: black;'>Input text is at <em><b>{reading_level_prediction['CEFR Level']} Level</b></em></h5>", unsafe_allow_html=True)

            st.markdown(f"<h4 style='{heading_style}'>Simplify to:</h4>", unsafe_allow_html=True)
            selected_level = st.radio("", level_options, key="reading_level",
                                      label_visibility="collapsed")
            st.markdown("""<br>""", unsafe_allow_html=True)
            st.markdown("""<br>""", unsafe_allow_html=True)


        with col1b:
            st.markdown(f"<h4 style='{heading_style}'>Select reading mode:</h4>", unsafe_allow_html=True)
            reading_type = st.selectbox("", ['Default', 'Bionic Reading'],
                                      label_visibility="collapsed")

            # Bionic Reading
            if reading_type == 'Bionic Reading':
                st.session_state.simplified_text = bionic_read(st.session_state.original_text)
            elif reading_type == 'Default':
                st.session_state.simplified_text = unbionic_read(st.session_state.original_text)
                
            
            if st.button(':bulb: **SIMPLIFY** :bulb:', key='simplify_button'):
                if is_input_present:
                    # AISafety check
                    url_simplify = flask_url + '/aisafety'
                    response_aisafety = requests.post(url_simplify, json={"text": user_input})

                    if response_aisafety.status_code == 200:
                        response_safe = response_aisafety.json()
                        safe_flag = response_safe['result'] in ['safe', 'not_sure_but_safe']
                    else:
                        # st.error("Error in checking text safety. User discretion is advised.")
                        # Stop further processing by skipping to the end of the if block
                        safe_flag = True

                    # Check if the text is already too simplified
                    if safe_flag and reading_level_prediction['CEFR Level'] == 'Beginner':
                        st.warning("Text is already too simplified for AI to help.")
                    elif safe_flag and selected_level == reading_level_prediction['CEFR Level']:
                        st.warning("Input text is at the same level as the target reading level. Select a lower target level.")
                    elif safe_flag and selected_level == 'Intermediate' and reading_level_prediction['CEFR Level'] == 'Beginner':
                        st.warning("Input text is at the lower level than the target reading level. Select an appropriate target level.")
                    elif safe_flag:
                        # Further logic to simplify text
                        url_simplify = flask_url + '/simplify'
                        response_llm = requests.post(url_simplify, json={
                            "text": user_input,
                            "target_level": selected_level,
                            "source_level": reading_level_prediction['CEFR Level']
                        })

                        if response_llm.status_code == 200:
                            ## Post process response
                            # pattern = r"as follows:(.*?)(</s>|$)"
                            simp_text = response_llm.json()
                            simp_text_clean = clean_simplified_text(simp_text)
                            
                            # Update the session state variable instead of a local one
                            st.session_state.original_text = simp_text_clean
                            # st.session_state.original_text = st.session_state.simplified_text
                            
                            if reading_type == 'Bionic Reading':
                                st.session_state.simplified_text = bionic_read(st.session_state.original_text)
                            elif reading_type == 'Default':
                                st.session_state.simplified_text = unbionic_read(st.session_state.original_text)
#                             text_for_speech = st.session_state.simplified_text
#                             # text_simplified = True

#                             # Convert text to speech
#                             st.session_state.sound_file = text_to_speech(text_for_speech)
                            
                    elif not safe_flag:
                        # Handle the case where safe_flag is False
                        st.session_state.original_text = "Your text may contain harmful or offensive language. Please review and revise it to ensure it's respectful and appropriate."
                else:
                    # Handle the case where input is not present
                    st.warning("Please enter text to simplify.")


    with col2:
        st.markdown("<p style='font-size: 24px; font-weight: bold;'>SIMPLIFIED TEXT</p>", unsafe_allow_html=True)

        # Apply regex to text for bold formatting
        print_text = st.session_state.simplified_text
        print_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', print_text)

        # Extract settings from session state
        font_size = st.session_state.custom_view_settings['font_size']
        font_type = st.session_state.custom_view_settings['font_type']
        text_color = st.session_state.custom_view_settings['text_color']
        bg_color = st.session_state.custom_view_settings['bg_color']

        # Render the markdown text with custom settings
        render_markdown_in_box_output(print_text, font_size, font_type, text_color, bg_color)


        # Text to Speech
        text_for_speech = st.session_state.original_text
        st.session_state.sound_file = text_to_speech(text_for_speech)
        st.audio(st.session_state.sound_file, format='audio/mp3')

        # Download PDF button
        col2a, col2b, col2c, col2d = st.columns([1, 1, 1, 1])

        st.markdown("""<br>""", unsafe_allow_html=True)
        with col2a:
            with st.expander("Font Options"):
                st.session_state.custom_view_settings['font_size'] = st.slider('Font Size', 12, 24, st.session_state.custom_view_settings['font_size'])
                st.session_state.custom_view_settings['font_type'] = st.selectbox('Font Type', ['Arial', 'Courier New', 'Georgia', 'Times New Roman', 'Verdana'], index=['Arial', 'Courier New', 'Georgia', 'Times New Roman', 'Verdana'].index(st.session_state.custom_view_settings['font_type']))
                st.session_state.custom_view_settings['text_color'] = st.color_picker('Text Color', st.session_state.custom_view_settings['text_color'])
                st.session_state.custom_view_settings['bg_color'] = st.color_picker('Background Color', st.session_state.custom_view_settings['bg_color'])



        with col2d:  # This will place the button a bit to the right
            generate_pdf_download_link(st.session_state.simplified_text)
            



    # st.image('./Banner_streamlit.png', use_column_width=True)
    

with tab1:
    heading_style = "color: darkblue; font-size: 2em; font-weight: 600;"
    st.markdown(f"<p style='{heading_style}'>How To Use</p>", unsafe_allow_html=True)
    st.write("""
    Keep it Simple is designed to be user-friendly and intuitive. Here’s a guide to help you get the most out of our platform:
    
    **1. Choosing your Desired Reading Level**:
       - When you insert text, you can select the target readability level (Beginner or Intermediate).
       - This feature helps tailor the complexity of the text to your specific needs or preferences.

    **2. Bionic Reading**:
       - Bionic Reading is a unique reading approach that enhances the most important parts of words to guide the eyes through the text.
       - This method can significantly aid in improving reading comprehension, especially for those with dyslexia or other reading difficulties.

    **3. Display Adjustment**:
       - You can customize how the simplified text appears on your screen, adjusting factors like font size, contrast, and color.
       - These adjustments are designed to make reading more comfortable and accessible for all users.

    **4. Text to Speech**:
       - Our Text to Speech feature converts written text into spoken words, helping those who prefer auditory learning or face challenges with reading.
       - It’s also a great tool for language learners to understand pronunciation and natural speech patterns.

    **5. Download to PDF**:
       - Once you have the simplified text, you can easily download it as a PDF.

    By following these steps, you can leverage the full potential of Keep it Simple to make reading and understanding written content easier and more effective.
    """)
    
    
with tab2:
    heading_style = "color: darkblue; font-size: 2em; font-weight: 600;"
    st.markdown(f"<p style='{heading_style}'>How It Works</p>", unsafe_allow_html=True)
    st.write("""
    Welcome to Keep it Simple, your gateway to accessible information. Our AI-powered platform is designed to make written content more understandable and accessible for everyone, regardless of their proficiency in English or learning abilities.
    
    Here's how we do it:
    
    1. **Project Overview**:
       - **Text Classification**: We classify inputted text into three readability levels: Beginner, Intermediate, and Advanced, based on the Common European Framework of Reference for Languages (CEFR).
       - **Text Simplification**: Our tool simplifies complex texts to make them easier to understand.
       - **Inclusivity**: We offer inclusive features, including bionic reading, text-to-speech, diplay adjustment, and a 'Safe Text' option.
    
    2. **Data & Model Development**:
       - We leverage open-source data, aligning it with the CEFR's three major levels: Advanced, Intermediate, and Beginner.
       - Our AI models, trained on these datasets, focus on unidirectional simplification of text, ensuring clarity and ease of understanding.
    
    3. **AI Model Components**:
       - **Classifier + Simplifier + Safety Check**: Our model first classifies texts into the predefined CEFR levels and then simplifies the content to match the target level. We also determine if a text has Unsafe Text, including profane language and hate speech.
       - **Text Classifier**: Utilizes the ktrain BERT model for accurate text classification.
       - **Text Simplifier**: Employs the llama-2 language model, fine-tuned with llora and qlora techniques, ensuring efficient and quality text simplification.
       - **Safety Check**: First, we use a keyword-based check to flag profane language. Then, hateBERT model is used to flag hate speech, which can include discriminatory, prejudiced, or inflammatory language.
       
    Join us in our mission to make digital content universally accessible. At Keep it Simple, we're not just simplifying text; we're opening doors to knowledge for everyone.
    
    Our GITHUB page: https://github.com/egehanyorulmaz/keep-it-simple-ai
    """)    

with tab3:
    heading_style = "color: darkblue; font-size: 2em; font-weight: 600"
    st.markdown(f"<p style='{heading_style}'>Empowering Through Understanding - About Keep it Simple</h1>", unsafe_allow_html=True)
    
    quote_style = "color: darkblue; font-size: 1.2em; font-weight: 200;"
    attribution_style = "font-size: 0.9em;"
    st.markdown(f"""
        <p style="{quote_style}">
            <b><i>"For most people, technology makes things easier. But for people with disabilities, technology makes things possible."</i> <b><br>
            <span style="{attribution_style}"> – Mary Pat Radabaugh (Director of IBM National Support Center for Persons with Disabilities, 1988) </span>
        </p>
        """, unsafe_allow_html=True)

    st.write("""
    At Keep it Simple, we're driven by the belief that knowledge should be accessible to everyone. Inspired by the vision of technology as an enabler, our platform is dedicated to transforming complex written information into easily digestible formats.
    """)
    
    st.write("""
    **Our Mission**:
    - To break down barriers in digital communication and make information understandable for all, regardless of language proficiency or learning abilities.
    - To empower individuals with learning and attention issues by providing tools that simplify and clarify content.

    **Our Inspiration**:
    - Drawing from the insight that 1 in 5 individuals in the United States faces learning and attention issues (U.S. Census Bureau, 2019), we strive to make technology a tool for possibility, not just convenience.

    **Our Approach**:
    - Using cutting-edge AI, we ensure that our text simplification and classification tools are top-notch in efficiency and accuracy.
    - We prioritize safety, inclusivity, and ease of use in all our solutions, making sure that our technology is a stepping stone towards a more inclusive digital world.

    Join us at Keep it Simple, where we are making information more accessible.
    
    Contributions, feedback, and improvements are always welcome. Feel free to submit pull requests or raise issues at https://github.com/egehanyorulmaz/keep-it-simple-ai
    
    **Contributors:** [Ankita Nambiar](https://www.linkedin.com/in/ankita-n-b4aa04140/), [Egehan Yorulmaz](https://www.linkedin.com/in/egehanyorulmaz/), [Lavanya Srivastava](https://www.linkedin.com/in/lav-sri/), [Prayut Jain](https://www.linkedin.com/in/prayutjain/)

    """)