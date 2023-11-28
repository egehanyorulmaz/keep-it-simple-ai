import streamlit as st
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
from json import JSONDecodeError

# Simplify text function
def simplify_text(text, reading_level):
    return text  # No change currently

# Bionic Reading Function
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

# Text to Speech Function
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

# output style
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
    # Render the content as Markdown within the styled box
    st.markdown(f"<div style='{box_style}'>{content}</div>", unsafe_allow_html=True)
    
# Functions for Download PDF Button
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

# Page setup
st.set_page_config(
    page_title='Keep It Simple',
    layout='wide'
)
st.title('KeepItSimple-AI')
st.markdown("""<br>""", unsafe_allow_html=True)

# Tabs
default, tab1, tab2, tab3 = st.tabs(["KeepItSimple App", "How to Use", "How it Works", "About Us"])

with default:
    
    heading_style = "color: darkblue; font-size: 1.4em; font-weight: 600;"

    # Reading levels
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="large")
    level_options = ['Beginner', 'Intermediate']


    # Initialize session state for simplified text 
    if 'simplified_text' not in st.session_state:
        st.session_state.simplified_text = ""

    # Add session state variables for custom view settings
    if 'custom_view_settings' not in st.session_state:
        st.session_state.custom_view_settings = {
            'font_size': 16,
            'font_type': 'Arial',
            'text_color': "#000000",
            'bg_color': "#FFFFFF"
        }

    # Initialize a variable to check if there is user input
    is_input_present = False

    with col1:
        st.markdown(f"<p style='{heading_style}'>SIMPLIFY TEXT TO: </p>", unsafe_allow_html=True)
        selected_level = st.radio("", level_options, key="reading_level",
                                  label_visibility="collapsed")
        st.markdown("""<br>""", unsafe_allow_html=True)
        st.markdown("""<br>""", unsafe_allow_html=True)


    # Dropdown for Learning Disabilities / Reading Type
    with col2:
        st.markdown(f"<p style='{heading_style}'>MODE</p>", unsafe_allow_html=True)
        reading_type = st.selectbox("", ['Default', 'Bionic Reading'],
                                  label_visibility="collapsed")

    # Side by side input and output text areas
    col8, col9 = st.columns([1, 1], gap="large")

    with col8:
        st.markdown(f"<p style='{heading_style}'>  ORIGINAL TEXT</p>", unsafe_allow_html=True)
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

        # CEFR Level Prediction
        api_url_cefr = 'https://10b3-34-123-103-86.ngrok-free.app/api/data'
        response = requests.post(api_url_cefr, json={"user_input": user_input})

        simplified_text = "" 
        text_for_speech = ""
        text_simplified = False 

        reading_level_prediction = {"CEFR Level": "Unknown"}

        col8a, col8b = st.columns([2,1])

        with col8b:
            if response.status_code == 200:
                reading_level_prediction = response.json()

                if st.button(':bulb: **SIMPLIFY** :bulb:'):
                    # Update the session state variable instead of a local one
                    st.session_state.simplified_text = simplify_text(user_input, selected_level)
                    text_for_speech = st.session_state.simplified_text
                    text_simplified = True

                    # Bionic Reading
                    if reading_type == 'Bionic Reading':
                            st.session_state.simplified_text = bionic_read(st.session_state.simplified_text)

                    # Convert text to speech
                    st.session_state.sound_file = text_to_speech(text_for_speech)

        with col8a:
            if is_input_present is True:
                st.write(f"**{reading_level_prediction['CEFR Level']} Level**")

    with col9:
        st.markdown(f"<p style='{heading_style}'>  SIMPLIFIED TEXT</p>", unsafe_allow_html=True)
        print_text = st.session_state.simplified_text
        print_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', print_text)

        with st.sidebar.expander("Customize Simplified Text View"):
            st.session_state.custom_view_settings['font_size'] = st.slider('Font Size', 12, 24, 16)
            st.session_state.custom_view_settings['font_type'] = st.selectbox('Font Type', ['Arial', 'Courier New', 'Georgia', 'Times New Roman', 'Verdana'])
            st.session_state.custom_view_settings['text_color'] = st.color_picker('Text Color', '#000000')
            st.session_state.custom_view_settings['bg_color'] = st.color_picker('Background Color', '#FFFFFF')

        font_size = st.session_state.custom_view_settings['font_size']
        font_type = st.session_state.custom_view_settings['font_type']
        text_color = st.session_state.custom_view_settings['text_color']
        bg_color = st.session_state.custom_view_settings['bg_color']

        # render_markdown_in_box_output(print_text)
        render_markdown_in_box_output(print_text, font_size, font_type, text_color, bg_color)

        # Play audio if available in session state
        if 'sound_file' in st.session_state and st.session_state.sound_file:
            st.audio(st.session_state.sound_file, format='audio/mp3')

        # Download PDF button
        col9a, col9b = st.columns([2.3, 1])
        with col9b:  # This will place the button a bit to the right
            if st.session_state.simplified_text:
                generate_pdf_download_link(st.session_state.simplified_text)
            
 



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
    
