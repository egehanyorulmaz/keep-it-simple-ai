import streamlit as st
import requests

# Simplify text function (dummy logic, can be enhanced)
def simplify_text(text, reading_level):
    return text  # No change currently

# Bionic Reading function
def bionic_read(text):
    words = text.split()
    formatted_words = []

    for word in words:
        word_length = len(word)
        half_length = word_length // 2

        formatted_word = f"**{word[:half_length]}**{word[half_length:]}"
        formatted_words.append(formatted_word)

    return ' '.join(formatted_words).replace('****', ' ')

# Page setup
st.set_page_config(
    page_title='Keep It Simple',
    layout='wide'
)

st.title('KeepItSimple-AI')

# Tabs for languages
# tab = st.selectbox('Language Selection', ['English (US)', 'German', 'French'], index=0)
# if tab == 'English (US)':

    
# Reading levels
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)


level_options = ['Elementary Level', 'Middle school Level', 'High School Level']

with col1:
    st.write("Readability modes:")
    selected_level = st.radio("", level_options, key="reading_level")


# Dropdown for Learning Disabilities / Reading Type
with col7:
    reading_type = st.selectbox("Learning Disabilities", ['Default', 'Dyslexia', 'Hyperlexia', 'Surface Dyslexia', 
                                                            'Double Deficit Dyslexia', 'Ocular Motor Deficit', 
                                                            'ADHD (Bionic Reading)'])


# Side by side input and output text areas
col8, col9 = st.columns(2)

with col8:
    st.write('Original Text:')
    user_input = st.text_area("","Enter or paste your text here to simplify...", height=200, key="input_text_area")

    # CEFR Level Prediction
    api_url_cefr = 'http://localhost:5000/api/data'
    response = requests.post(api_url_cefr, json={"user_input": user_input})
    simplified_text = "" ## Intiate blank field

    col8a, col8b, col8c = st.columns(3)

    

    with col8c:
        if response.status_code == 200:
            reading_level_prediction = response.json()
            if st.button('Simplify'):
                simplified_text = simplify_text(user_input, selected_level)
                if reading_type == 'ADHD (Bionic Reading)':
                    simplified_text = bionic_read(simplified_text)
    
    with col8a:
        st.write(f"Text level: **{reading_level_prediction['CEFR Level']}**")

    



with col9:
    st.write('Simplified Text:')
    st.text_area("",simplified_text, height=200, key = "output_text_area")
