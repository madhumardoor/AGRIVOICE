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
from docx import Document

# Download necessary NLTK data
nltk.download("stopwords")
nltk.download("punkt")
stop_words = set(nltk.corpus.stopwords.words("english"))

# ------------------- Function to Set Background Image -------------------
def set_background():
    page_bg = """
    <style>
    .stApp {
        background: url("https://www.jaagrukbharat.com/_next/image?url=https%3A%2F%2Fjaagruk-public.s3.ap-south-1.amazonaws.com%2Farticle%2Fimages%2Fea1570be-e12d-4d79-bb30-28074d56f917_18KORX2XWfg-oJtHiUzePNur8Kwtiy9Ba.webp&w=3840&q=75");
        background-size: cover;
    }
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

# Call the function to apply background
set_background()

# ------------------- Custom Styled Title (Single Line) -------------------
st.markdown(
    """
    <style>
    .title {
        text-align: center;
        font-size: 30px;
        font-weight: bold;
        white-space: nowrap; /* Prevents text wrapping */
        overflow: hidden;
        text-overflow: ellipsis;
        color: white; /* Adjust color based on background */
    }
    </style>
    <p class="title">🌾 AGRIVOICE: Upload, Translate & Listen Instantly! 🌏🔊</p>
    """,
    unsafe_allow_html=True
)

st.markdown("🌏📖 **Upload. Translate. Listen. Break Language Barriers!**")

# ------------------- File Uploader (PDF & DOCX) -------------------
uploaded_file = st.file_uploader("📂 Upload a Document (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file is not None:
    
    # ------------------- Extract Text from PDF -------------------
    def extract_text_from_pdf(uploaded_file):
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n\n"
        return text

    # ------------------- Extract Text from DOCX -------------------
    def extract_text_from_docx(uploaded_file):
        doc = Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    # Check file type and extract text accordingly
    if uploaded_file.type == "application/pdf":
        policy_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        policy_text = extract_text_from_docx(uploaded_file)
    else:
        policy_text = ""

    # Display extracted text
    st.subheader("📜 Extracted Text")
    st.write(policy_text[:500])  # Show first 500 characters

    # ------------------- Clean Extracted Text -------------------
    def clean_text(text):
        text = re.sub(r"\s+", " ", text)  # Remove extra spaces
        text = re.sub(r"[^a-zA-Z0-9.,\n\s]", "", text)  # Remove special characters
        text = text.lower()  # Convert to lowercase
        text = " ".join([word for word in text.split() if word not in stop_words])  # Remove stopwords
        return text

    cleaned_policy_text = clean_text(policy_text)

    # ------------------- Translate Text -------------------
    translated_text_hindi = GoogleTranslator(source="auto", target="hi").translate(cleaned_policy_text)
    translated_text_kannada = GoogleTranslator(source="auto", target="kn").translate(cleaned_policy_text)

    # Display translations
    st.subheader("🇮🇳 Translated Text (Hindi)")
    st.write(translated_text_hindi[:500])  # Show first 500 characters

    st.subheader("🇮🇳 Translated Text (Kannada)")
    st.write(translated_text_kannada[:500])  # Show first 500 characters

    # ------------------- Convert Kannada Text to Speech -------------------
    if st.button("🎙️ Generate Kannada Audio"):
        tts = gTTS(translated_text_kannada, lang="kn")
        audio_buffer = BytesIO()
        tts.save(audio_buffer)
        audio_buffer.seek(0)
        st.audio(audio_buffer, format="audio/mp3", start_time=0)

st.markdown("🚀 Developed by **Madhu M | AGRIVOICE**")
