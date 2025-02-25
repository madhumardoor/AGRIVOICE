# -*- coding: utf-8 -*-
"""


@author: Madhu M
"""

import streamlit as st
import pdfplumber
import nltk
import re
import base64
from deep_translator import GoogleTranslator
from gtts import gTTS
from io import BytesIO

# Download necessary NLTK data
nltk.download("stopwords")
nltk.download("punkt")
stop_words = set(nltk.corpus.stopwords.words("english"))

# ------------------- Function to Set Background Image -------------------
def set_background():
    page_bg = """
    <style>
    .stApp {
        background: url(https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSge6E5SOQmGoZJzSiTr5-c2Go43RRvRJPV-w&s
        background-size: cover;
    }
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

# Call the function to apply background
set_background()

# ------------------- Streamlit UI -------------------
st.title("📄 AGRIVOICE: PDF Text Extraction & Translation")
st.markdown("Upload a **PDF file**, extract text, translate it, and convert it to **Kannada speech** 🎙️.")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    
    # ------------------- Extract text from PDF -------------------
    def extract_text_from_pdf(uploaded_file):
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n\n"
        return text

    policy_text = extract_text_from_pdf(uploaded_file)

    # Display extracted text
    st.subheader("📜 Extracted Text")
    st.write(policy_text[:500])  # Show first 500 characters

    # ------------------- Clean extracted text -------------------
    def clean_text(text):
        text = re.sub(r"\s+", " ", text)  # Remove extra spaces
        text = re.sub(r"[^a-zA-Z0-9.,\n\s]", "", text)  # Remove special characters
        text = text.lower()  # Convert to lowercase
        text = " ".join([word for word in text.split() if word not in stop_words])  # Remove stopwords
        return text

    cleaned_policy_text = clean_text(policy_text)

    # ------------------- Translate text -------------------
    translated_text_hindi = GoogleTranslator(source="auto", target="hi").translate(cleaned_policy_text)
    translated_text_kannada = GoogleTranslator(source="auto", target="kn").translate(cleaned_policy_text)

    # Display translations
    st.subheader("🇮🇳 Translated Text (Hindi)")
    st.write(translated_text_hindi[:500])  # Show first 500 characters

    st.subheader("🇮🇳 Translated Text (Kannada)")
    st.write(translated_text_kannada[:500])  # Show first 500 characters

    # ------------------- Convert Kannada text to speech -------------------
    if st.button("🎙️ Generate Kannada Audio"):
        tts = gTTS(translated_text_kannada, lang="kn")
        audio_buffer = BytesIO()
        tts.save(audio_buffer)
        audio_buffer.seek(0)
        st.audio(audio_buffer, format="audio/mp3", start_time=0)

st.markdown("🚀 Developed by **Madhu M | AGRIVOICE**")
