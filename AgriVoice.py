# -*- coding: utf-8 -*-
"""
Fixed Streamlit App for File Extraction, Translation, Summarization & TTS
@author: Madhu M
"""

import streamlit as st
import pdfplumber
import nltk
import re
import io
import os
import torch
from deep_translator import GoogleTranslator
from gtts import gTTS
from docx import Document
from transformers import pipeline

# Avoid CUDA issues with torch
os.environ["TORCH_USE_CUDA"] = "0"

# Download NLTK stopwords
nltk.download("stopwords")
nltk.download("punkt")
stop_words = set(nltk.corpus.stopwords.words("english"))

# ------------------- UI Customization -------------------
st.set_page_config(page_title="Agrivoice", page_icon="📄", layout="wide")

def set_background():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #004AAD;
            color: white;
        }
        h1, h2, h3, h4, h5, h6, p {
            color: white !important;
        }
        .stTextArea textarea, .stTextInput input {
            background-color: #002F6C;
            color: white;
            border-radius: 5px;
        }
        .stFileUploader {
            background-color: white;
            padding: 10px;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

set_background()

# ------------------- File Uploader -------------------
st.title("📄 Agrivoice: Extract, Translate & Summarize")

uploaded_file = st.file_uploader("Upload a PDF or DOCX", type=["pdf", "docx"], key="file_upload")

if uploaded_file:
    st.markdown("---")

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

    # Extract text based on file type
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
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^a-zA-Z0-9.,\n\s]", "", text)
        text = text.lower()
        text = " ".join([word for word in text.split() if word not in stop_words])
        return text

    cleaned_policy_text = clean_text(policy_text)

    # ------------------- Function to Split Large Text -------------------
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

    # ------------------- Translate Large Text -------------------
    def translate_large_text(text, target_lang):
        text_chunks = split_text(text, 5000)
        translated_chunks = [GoogleTranslator(source="auto", target=target_lang).translate(chunk) for chunk in text_chunks]
        return " ".join(translated_chunks)  

    # ------------------- Translate Text -------------------
    translated_text_hindi = translate_large_text(cleaned_policy_text, "hi")
    translated_text_kannada = translate_large_text(cleaned_policy_text, "kn")

    # Display translations
    st.subheader("🇮🇳 Translated Text (Hindi)")
    st.write(translated_text_hindi)  
    st.subheader("🇮🇳 Translated Text (Kannada)")
    st.write(translated_text_kannada) 

    # ------------------- Generate Summary -------------------
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def summarize_text(text):
        text_chunks = split_text(text, 1000)
        summarized_chunks = [summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]["summary_text"] for chunk in text_chunks]
        return " ".join(summarized_chunks)  

    # Generate summary in English
    summary_english = summarize_text(cleaned_policy_text)

    # Translate summaries into Hindi and Kannada
    summary_hindi = GoogleTranslator(source="auto", target="hi").translate(summary_english)
    summary_kannada = GoogleTranslator(source="auto", target="kn").translate(summary_english)

    # Display Summaries
    st.subheader("📌 Summary in Hindi 🇮🇳")
    st.write(summary_hindi)
    
    st.subheader("📌 Summary in Kannada 🇮🇳")
    st.write(summary_kannada)

    # ------------------- Convert Hindi & Kannada Summary to Speech -------------------
    def generate_audio(summary_text, lang="kn"):
        tts = gTTS(summary_text, lang=lang)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎙️ Generate Hindi Summary Audio"):
            audio_data_hindi = generate_audio(summary_hindi, lang="hi")
            st.success("✅ Hindi Summary Audio Generated! 🎧")
            st.audio(audio_data_hindi, format="audio/mp3")

    with col2:
        if st.button("🎙️ Generate Kannada Summary Audio"):
            audio_data_kannada = generate_audio(summary_kannada, lang="kn")
            st.success("✅ Kannada Summary Audio Generated! 🎧")
            st.audio(audio_data_kannada, format="audio/mp3")

# ------------------- Custom Footer -------------------
st.markdown("---")
st.markdown(
    """
    <p style="text-align: center; font-size: 16px; font-weight: bold; color: white;">
    Developed with ❤️ by <strong>Madhu M</strong> | AGRIVOICE 🌿</p>
    """,
    unsafe_allow_html=True
)
# -*- coding: utf-8 -*-
"""
@author: Madhu M
"""

import streamlit as st
import pdfplumber
import nltk# -*- coding: utf-8 -*-
"""
Complete Streamlit App for File Extraction, Translation, Summarization & TTS
@author: Madhu M
"""

import streamlit as st
import pdfplumber
import nltk
import re
import io
from deep_translator import GoogleTranslator
from gtts import gTTS
from docx import Document
from transformers import pipeline

# Download NLTK stopwords
nltk.download("stopwords")
nltk.download("punkt")
stop_words = set(nltk.corpus.stopwords.words("english"))

# ------------------- UI Customization -------------------
def set_background():
    page_bg = """
    <style>
    .stApp {
        background-color: #004AAD; /* Deep Blue */
        color: white;
    }
    h1, h2, h3, h4, h5, h6, p {
        color: white !important;
    }
    .stTextArea textarea, .stTextInput input {
        background-color: #002F6C;
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

set_background()

# ------------------- File Uploader -------------------
st.markdown("## 📂 UPLOAD A DOCUMENT ")
uploaded_file = st.file_uploader("", type=["pdf", "docx"])

if uploaded_file:
    st.markdown("---")  

    st.markdown(
        """
        <style>
        .title {
            text-align: center;
            font-size: 35px;
            font-weight: bold;
            color: white;
        }
        </style>
        <p class="title">🌾 AGRIVOICE: Upload, Translate & Summarize Instantly! 🌏🔊</p>
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
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^a-zA-Z0-9.,\n\s]", "", text)
        text = text.lower()
        text = " ".join([word for word in text.split() if word not in stop_words])
        return text

    cleaned_policy_text = clean_text(policy_text)

    # ------------------- Function to Split Large Text -------------------
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

    # ------------------- Translate Large Text -------------------
    def translate_large_text(text, target_lang):
        text_chunks = split_text(text, 5000)
        translated_chunks = [GoogleTranslator(source="auto", target=target_lang).translate(chunk) for chunk in text_chunks]
        return " ".join(translated_chunks)  

    # ------------------- Translate Text -------------------
    translated_text_hindi = translate_large_text(cleaned_policy_text, "hi")
    translated_text_kannada = translate_large_text(cleaned_policy_text, "kn")

    # Display translations
    st.subheader("🇮🇳 Translated Text (Hindi)")
    st.write(translated_text_hindi)  
    st.subheader("🇮🇳 Translated Text (Kannada)")
    st.write(translated_text_kannada) 

    # ------------------- Generate Summary -------------------
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def summarize_text(text):
        text_chunks = split_text(text, 1000)
        summarized_chunks = [summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]["summary_text"] for chunk in text_chunks]
        return " ".join(summarized_chunks)  

    # Generate summary in English
    summary_english = summarize_text(cleaned_policy_text)

    # Translate summaries into Hindi and Kannada
    summary_hindi = GoogleTranslator(source="auto", target="hi").translate(summary_english)
    summary_kannada = GoogleTranslator(source="auto", target="kn").translate(summary_english)

    # Display Summaries
    st.subheader("📌 Summary in Hindi 🇮🇳")
    st.write(summary_hindi)
    
    st.subheader("📌 Summary in Kannada 🇮🇳")
    st.write(summary_kannada)

    # ------------------- Convert Hindi & Kannada Summary to Speech -------------------
    def generate_audio(summary_text, lang="kn"):
        tts = gTTS(summary_text, lang=lang)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎙️ Generate Hindi Summary Audio"):
            audio_data_hindi = generate_audio(summary_hindi, lang="hi")
            st.success("✅ Hindi Summary Audio Generated! 🎧")
            st.audio(audio_data_hindi, format="audio/mp3")

    with col2:
        if st.button("🎙️ Generate Kannada Summary Audio"):
            audio_data_kannada = generate_audio(summary_kannada, lang="kn")
            st.success("✅ Kannada Summary Audio Generated! 🎧")
            st.audio(audio_data_kannada, format="audio/mp3")

# ------------------- Custom Footer -------------------
st.markdown("---")
st.markdown(
    """
    <p class="footer">Developed with ❤️ by <strong>Madhu M</strong> | AGRIVOICE 🌿</p>
    """,
    unsafe_allow_html=True
)

import re
import io
from deep_translator import GoogleTranslator
from gtts import gTTS
from docx import Document
from transformers import pipeline

# Download NLTK data
nltk.download("stopwords")
nltk.download("punkt")
stop_words = set(nltk.corpus.stopwords.words("english"))

# ------------------- Function to Set Background -------------------
def set_background():
    page_bg = """
    <style>
    .stApp {
        background-color: #004AAD; /* Deep Blue */
        color: white;
    }
    h1, h2, h3, h4, h5, h6, p {
        color: white !important;
    }
    .stTextArea textarea, .stTextInput input {
        background-color: #002F6C;
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

set_background()

# ------------------- File Uploader -------------------
st.markdown("## 📂 UPLOAD A DOCUMENT ")
uploaded_file = st.file_uploader("", type=["pdf", "docx"])

if uploaded_file:
    st.markdown("---")  

    st.markdown(
        """
        <style>
        .title {
            text-align: center;
            font-size: 35px;
            font-weight: bold;
            color: white;
        }
        </style>
        <p class="title">🌾 AGRIVOICE: Upload, Translate & Summarize Instantly! 🌏🔊</p>
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
    st.write(policy_text[5000])  # Show first 5000 characters

    # ------------------- Clean Extracted Text -------------------
    def clean_text(text):
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^a-zA-Z0-9.,\n\s]", "", text)
        text = text.lower()
        text = " ".join([word for word in text.split() if word not in stop_words])
        return text

    cleaned_policy_text = clean_text(policy_text)

    # ------------------- Function to Split Large Text -------------------
    def split_text(text, max_length):
        chunks = []
        while len(text) > max_length:
            split_index = text[:max_length].rfind(" ")  
            if split_index == -1:  
                split_index = max_length
            chunks.append(text[:split_index])
            text = text[split_index:]
        chunks.append(text)  
        return chunks

    # ------------------- Translate Large Text -------------------
    def translate_large_text(text, target_lang):
        text_chunks = split_text(text)
        translated_chunks = [GoogleTranslator(source="auto", target=target_lang).translate(chunk) for chunk in text_chunks]
        return " ".join(translated_chunks)  

    # ------------------- Translate Text -------------------
    translated_text_hindi = translate_large_text(cleaned_policy_text, "hi")
    translated_text_kannada = translate_large_text(cleaned_policy_text, "kn")

    # Display translations
    st.subheader("🇮🇳 Translated Text (Hindi)")
    st.write(translated_text_hindi)  
    st.subheader("🇮🇳 Translated Text (Kannada)")
    st.write(translated_text_kannada) 

    # ------------------- Generate Summary -------------------
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def summarize_text(text):
        text_chunks = split_text(text)
        summarized_chunks = [summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]["summary_text"] for chunk in text_chunks]
        return " ".join(summarized_chunks)  

    # Generate summary in English
    summary_english = summarize_text(cleaned_policy_text)

    # Translate summaries into Hindi and Kannada
    summary_hindi = GoogleTranslator(source="auto", target="hi").translate(summary_english)
    summary_kannada = GoogleTranslator(source="auto", target="kn").translate(summary_english)

    # Display Summaries
    st.subheader("📌 Summary in Hindi 🇮🇳")
    st.write(summary_hindi)
    
    st.subheader("📌 Summary in Kannada 🇮🇳")
    st.write(summary_kannada)

    # ------------------- Convert Kannada Summary to Speech -------------------
    def generate_audio(summary_text, lang="kn"):
        tts = gTTS(summary_text, lang=lang)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer

    if st.button("🎙️ Generate Kannada Summary Audio"):
        audio_data = generate_audio(summary_kannada)
        st.success("✅ Kannada Summary Audio Generated Successfully! 🎧")
        st.audio(audio_data, format="audio/mp3")

# ------------------- Custom Footer -------------------
st.markdown("---")
st.markdown(
    """
    <p class="footer">Developed with ❤️ by <strong>Madhu M</strong> | AGRIVOICE 🌿</p>
    """,
    unsafe_allow_html=True
)
