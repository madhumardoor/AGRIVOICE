# -*- coding: utf-8 -*-
"""
@author: Madhu M
"""

import streamlit as st
import pdfplumber
import nltk
import re
import os
from deep_translator import GoogleTranslator
from gtts import gTTS
from docx import Document

# Download necessary NLTK data
nltk.download("stopwords")
nltk.download("punkt")
stop_words = set(nltk.corpus.stopwords.words("english"))

# ------------------- Function to Set Background Color -------------------
def set_background():
    page_bg = """
    <style>
    .stApp {
        background-color: #004AAD; /* Deep Blue */
        color: white; /* White Text */
    }
    h1, h2, h3, h4, h5, h6, p {
        color: white !important;
    }
    .stTextArea textarea, .stTextInput input {
        background-color: #002F6C; /* Darker Blue */
        color: white;
        border-radius: 5px;
    }
    .stFileUploader {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
    }
    .footer {
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        color: white;
        padding-top: 20px;
    }
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

# Apply background
set_background()

# ------------------- File Uploader (Appears First) -------------------
st.markdown("## 📂 UPLOAD A DOCUMENT ")
uploaded_file = st.file_uploader("", type=["pdf", "docx"])

if uploaded_file:
    st.markdown("---")  # Separator line

    # ------------------- Custom Styled Title -------------------
    st.markdown(
        """
        <style>
        .title {
            text-align: center;
            font-size: 45px;
            font-weight: bold;
            color: black;
        }
        </style>
        <p class="title">🌾 AGRIVOICE: Upload, Translate & Listen Instantly! 🌏🔊</p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("📄🔊 **Turn Your Documents into Speech – Instantly!**")

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

    # Check file type and extract text
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

    # ------------------- Function to Split Large Text for Translation -------------------
    def split_text(text, max_length=5000):
        chunks = []
        while len(text) > max_length:
            split_index = text[:max_length].rfind(" ")  # Find the nearest space before 5000 characters
            if split_index == -1:  # If no space found, split at max_length
                split_index = max_length
            chunks.append(text[:split_index])
            text = text[split_index:]
        chunks.append(text)  # Add remaining text
        return chunks

    # ------------------- Function to Translate Large Text -------------------
    def translate_large_text(text, target_lang):
        text_chunks = split_text(text, 5000)
        translated_chunks = [GoogleTranslator(source="auto", target=target_lang).translate(chunk) for chunk in text_chunks]
        return " ".join(translated_chunks)  # Combine translated parts

    # ------------------- Translate Text -------------------
    translated_text_hindi = translate_large_text(cleaned_policy_text, "hi")
    translated_text_kannada = translate_large_text(cleaned_policy_text, "kn")

    # Display translations
    st.subheader("🇮🇳 Translated Text (Hindi)")
    st.write(translated_text_hindi)  
    st.subheader("🇮🇳 Translated Text (Kannada)")
    st.write(translated_text_kannada) 

    # ------------------- Convert Kannada Text to Speech -------------------
    if st.button("🎙️ Generate Kannada Audio"):
        tts = gTTS(translated_text_kannada, lang="kn")
        
        # Save as a file instead of memory buffer
        audio_filename = "kannada_audio.mp3"
        tts.save(audio_filename)

        # Check if file is generated
        if os.path.exists(audio_filename):
            st.success("✅ Audio generated successfully! Click below to listen 🎧")
            st.audio(audio_filename, format="audio/mp3")
        else:
            st.error("❌ Audio generation failed. Please try again.")

# ------------------- Custom Footer -------------------
st.markdown("---")
st.markdown(
    """
    <p class="footer">Developed with ❤️ by <strong>Madhu M</strong> | AGRIVOICE 🌿</p>
    """,
    unsafe_allow_html=True
)
