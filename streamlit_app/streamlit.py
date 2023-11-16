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

# Simplify text function (dummy logic, can be enhanced)
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

# Headings style
heading_style = "color: darkblue; font-size: 1.4em; font-weight: 600;"

# Reading levels
col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="large")
level_options = ['Beginner', 'Intermediate', 'Advanced']

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


with col1:
    st.markdown(f"<p style='{heading_style}'>READING LEVEL</p>", unsafe_allow_html=True)
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

    # CEFR Level Prediction
    api_url_cefr = 'https://4ce4-34-132-250-26.ngrok-free.app/api/data'
    response = requests.post(api_url_cefr, json={"user_input": user_input})
    simplified_text = "" 
    text_for_speech = ""
    text_simplified = False
    
    # Initialize reading_level_prediction with a default value
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
                    
                # Text2speech
                st.session_state.sound_file = text_to_speech(text_for_speech)
    with col8a:
        st.write(f"**{reading_level_prediction['CEFR Level']} Level**")
    
with col9:
    st.markdown(f"<p style='{heading_style}'>  SIMPLIFIED TEXT</p>", unsafe_allow_html=True)
    print_text = st.session_state.simplified_text
    print_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', print_text)

    # Sidebar #Display Adjustment
    with st.sidebar.expander("Customize Simplified Text View"):
        st.session_state.custom_view_settings['font_size'] = st.slider('Font Size', 12, 24, 16)
        st.session_state.custom_view_settings['font_type'] = st.selectbox('Font Type', ['Arial', 'Courier New', 'Georgia', 'Times New Roman', 'Verdana'])
        st.session_state.custom_view_settings['text_color'] = st.color_picker('Text Color', '#000000')
        st.session_state.custom_view_settings['bg_color'] = st.color_picker('Background Color', '#FFFFFF')

    font_size = st.session_state.custom_view_settings['font_size']
    font_type = st.session_state.custom_view_settings['font_type']
    text_color = st.session_state.custom_view_settings['text_color']
    bg_color = st.session_state.custom_view_settings['bg_color']
    
    render_markdown_in_box_output(print_text, font_size, font_type, text_color, bg_color)
    
    # Text2Speech
    if 'sound_file' in st.session_state and st.session_state.sound_file:
        st.audio(st.session_state.sound_file, format='audio/mp3')

    # Download PDF button
    col9a, col9b = st.columns([2.3, 1])
    with col9b:  # This will place the button a bit to the right
        if st.session_state.simplified_text:
            generate_pdf_download_link(st.session_state.simplified_text)
            
    
