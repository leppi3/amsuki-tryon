import streamlit as st
import requests
import base64
from PIL import Image
import io

st.set_page_config(
    page_title='Amsuki Virtual Try-On',
    page_icon='🥻',
    layout='centered'
)

st.markdown('''
<style>
@import url(https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=Raleway:wght@300;400;500&display=swap);

html, body, [class*="css"] {
    background-color: #1a1410;
    color: #f5e6c8;
    font-family: Raleway, sans-serif;
}

.main { background-color: #1a1410; }

.amsuki-header {
    text-align: center;
    padding: 2rem 1rem 1rem;
    border-bottom: 1px solid #c9a96e55;
    margin-bottom: 2rem;
}

.amsuki-logo {
    font-family: Cormorant Garamond, serif;
    font-size: 3rem;
    font-weight: 300;
    color: #f5e6c8;
    margin: 0;
}

.amsuki-tagline {
    color: #c9a96e;
    font-size: 0.8rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

.tips-box {
    background: #2a211a;
    border: 1px solid #c9a96e33;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin-top: 1.5rem;
    font-size: 0.85rem;
    color: #e8d5b0;
    line-height: 1.8;
}

.stButton > button {
    background: linear-gradient(135deg, #c0392b, #922b21) !important;
    color: #f5e6c8 !important;
    font-family: Raleway, sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    font-size: 0.8rem !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #e74c3c, #c0392b) !important;
}

section[data-testid="stFileUploader"] {
    background: #2a211a;
    border: 1px dashed #c9a96e66;
    border-radius: 10px;
    padding: 1rem;
}

.footer {
    text-align: center;
    padding: 2rem 1rem 1rem;
    border-top: 1px solid #c9a96e33;
    margin-top: 2rem;
    color: #c9a96e;
    font-family: Cormorant Garamond, serif;
    font-size: 0.85rem;
    letter-spacing: 0.15em;
}

.stImage { border-radius: 10px; }
</style>
''', unsafe_allow_html=True)

st.markdown('''
<div class="amsuki-header">
    <div class="amsuki-logo">&#3349;&#3306;suki</div>
    <div class="amsuki-tagline">Authentic Handloom Sarees &middot; Virtual Try-On</div>
</div>
''', unsafe_allow_html=True)

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format='PNG')
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def try_on_saree(person_image, saree_image):
    try:
        person_image = person_image.resize((512, 768))
        saree_image = saree_image.resize((384, 512))
        API_URL = 'https://yisol-idm-vton.hf.space/run/predict'
        person_b64 = image_to_base64(person_image)
        saree_b64 = image_to_base64(saree_image)
        payload = {
            'data': [
                {'image': 'data:image/png;base64,' + person_b64, 'mask': None},
                {'image': 'data:image/png;base64,' + saree_b64},
                True,
                True,
                30,
                42,
                'upper_body'
            ]
        }
        response = requests.post(API_URL, json=payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            if result and 'data' in result and len(result['data']) > 0:
                img_data = result['data'][0]
                if isinstance(img_data, dict) and 'image' in img_data:
                    img_bytes = base64.b64decode(img_data['image'].split(',')[1])
                    return Image.open(io.BytesIO(img_bytes)), None
        return None, 'AI service is busy. Please try again in a moment.'
    except requests.exceptions.Timeout:
        return None, 'Request timed out. Please try again in a minute.'
    except Exception as e:
        return None, 'Something went wrong: ' + str(e)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<p style="color:#f5e6c8;font-family:Cormorant Garamond,serif;font-size:1.1rem;letter-spacing:0.08em;">Your Photo</p>', unsafe_allow_html=True)
    st.caption('Front-facing, full body, good lighting')
    person_file = st.file_uploader('Upload your photo', type=['jpg', 'jpeg', 'png'], key='person', label_visibility='collapsed')

with col2:
    st.markdown('<p style="color:#f5e6c8;font-family:Cormorant Garamond,serif;font-size:1.1rem;letter-spacing:0.08em;">Choose a Saree</p>', unsafe_allow_html=True)
    st.caption('Upload any saree from our collection')
    saree_file = st.file_uploader('Upload saree image', type=['jpg', 'jpeg', 'png'], key='saree', label_visibility='collapsed')

if person_file:
    with col1:
        st.image(person_file, use_column_width=True)

if saree_file:
    with col2:
        st.image(saree_file, use_column_width=True)

st.markdown('<br>', unsafe_allow_html=True)

if st.button('✦  Drape This Saree  ✦'):
    if not person_file:
        st.warning('Please upload your photo first.')
    elif not saree_file:
        st.warning('Please upload a saree image.')
    else:
        with st.spinner('AI is draping the saree... please wait 30-60 seconds'):
            person_image = Image.open(person_file).convert('RGB')
            saree_image = Image.open(saree_file).convert('RGB')
            result_image, error = try_on_saree(person_image, saree_image)
            if result_image:
                st.markdown('<p style="color:#f5e6c8;font-family:Cormorant Garamond,serif;font-size:1.1rem;letter-spacing:0.08em;margin-top:1rem;">Your Look</p>', unsafe_allow_html=True)
                st.image(result_image, use_column_width=True)
                st.success('Your virtual try-on is ready! Tag us @amsuki_handlooms')
                buf = io.BytesIO()
                result_image.save(buf, format='PNG')
                st.download_button(
                    label='Download Your Look',
                    data=buf.getvalue(),
                    file_name='amsuki_tryon.png',
                    mime='image/png'
                )
            else:
                st.error(error)

st.markdown('''
<div class="tips-box">
    <strong style="color:#c9a96e;">Tips for best results:</strong><br>
    Stand straight, facing forward with arms slightly away from your body.<br>
    Use a well-lit photo with a plain background.<br>
    Processing takes 30 to 60 seconds. Please be patient.
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="footer">
    Amsuki Handlooms &middot; Instagram @amsuki_handlooms &middot; DM to Order
</div>
''', unsafe_allow_html=True)
