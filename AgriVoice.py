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
from transformers import pipeline

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

# ------------------- File Uploader -------------------
st.markdown("## 📂 UPLOAD A DOCUMENT ")
uploaded_file = st.file_uploader("", type=["pdf", "docx"])

if uploaded_file:
    st.markdown("---")  

    # Custom Styled Title
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
        <p class="title">🌾 AGRIVOICE: Upload, Translate & Summarize Instantly! 🌏🔊</p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("📄🔊 **Turn Your Documents into Speech – Instantly!**")

    # ------------------- Extract Text Functions -------------------
    def extract_text_from_pdf(uploaded_file):
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n\n"
        return text

    def extract_text_from_docx(uploaded_file):
        doc = Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    # Extract text
    if uploaded_file.type == "application/pdf":
        policy_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        policy_text = extract_text_from_docx(uploaded_file)
    else:
        policy_text = ""

    # Display extracted text
    st.subheader("📜 Extracted Text")
    st.write(policy_text)  

    # ------------------- Clean Extracted Text -------------------
    def clean_text(text):
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^a-zA-Z0-9.,\n\s]", "", text)
        text = text.lower()
        text = " ".join([word for word in text.split() if word not in stop_words])
        return text

    cleaned_policy_text = clean_text(policy_text)

    # ------------------- Translation Functions -------------------
    def split_text(text, max_length=5000):
        chunks = []
        while len(text) > max_length:
            split_index = text[:max_length].rfind(" ")
            if split_index == -1:
                split_index = max_length
            chunks.append(text[:split_index])
            text = text[split_index:]
        chunks.append(text)
        return chunks

    def translate_large_text(text, target_lang):
        text_chunks = split_text(text, 5000)
        translated_chunks = [GoogleTranslator(source="auto", target=target_lang).translate(chunk) for chunk in text_chunks]
        return " ".join(translated_chunks)

    # Translate Text
    translated_text_hindi = translate_large_text(cleaned_policy_text, "hi")
    translated_text_kannada = translate_large_text(cleaned_policy_text, "kn")

    # Display translations
    st.subheader("🇮🇳 Translated Text (Hindi)")
    st.write(translated_text_hindi)
    st.subheader("🇮🇳 Translated Text (Kannada)")
    st.write(translated_text_kannada)

    # ------------------- Generate Summary -------------------
    summarizer = pipeline("summarization")

    def summarize_text(text):
        text_chunks = split_text(text, 1000)
        summarized_chunks = [summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]["summary_text"] for chunk in text_chunks]
        return " ".join(summarized_chunks)

    # Generate summary
    summary_english = summarize_text(cleaned_policy_text)
    summary_hindi = GoogleTranslator(source="auto", target="hi").translate(summary_english)
    summary_kannada = GoogleTranslator(source="auto", target="kn").translate(summary_english)

    # Display Summaries
    st.subheader("📌 Summary in Hindi 🇮🇳")
    st.write(summary_hindi)
    
    st.subheader("📌 Summary in Kannada 🇮🇳")
    st.write(summary_kannada)

    # ------------------- Select Language for Speech -------------------
    st.subheader("🎙️ Choose Language for Speech")
    speech_language = st.selectbox("Select language for audio:", ["Hindi", "Kannada"])

    # ------------------- Convert Selected Summary to Speech -------------------
    if st.button("🔊 Generate Summary Audio"):
        if speech_language == "Hindi":
            tts = gTTS(summary_hindi, lang="hi")
            audio_filename = "hindi_summary_audio.mp3"
        else:
            tts = gTTS(summary_kannada, lang="kn")
            audio_filename = "kannada_summary_audio.mp3"
        
        tts.save(audio_filename)

        if os.path.exists(audio_filename):
            st.success(f"✅ {speech_language} Summary Audio Generated Successfully! 🎧")
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
