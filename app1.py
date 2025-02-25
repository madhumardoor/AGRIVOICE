
@author: Madhu M
"""

import streamlit as st
import pdfplumber
import nltk
import re
from deep_translator import GoogleTranslator
from gtts import gTTS

# Download necessary NLTK data
nltk.download("stopwords")
nltk.download("punkt")
stop_words = set(nltk.corpus.stopwords.words("english"))

st.title("📄 AGRIVOICE: PDF Text Extraction & Translation")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    # Extract text from PDF
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
    st.subheader("Extracted Text")
    st.write(policy_text[:500])  # Show first 500 characters

    # Clean text
    def clean_text(text):
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^a-zA-Z0-9.,\n\s]", "", text)
        text = text.lower()
        text = " ".join([word for word in text.split() if word not in stop_words])
        return text

    cleaned_policy_text = clean_text(policy_text)

    # Translate to Hindi
    translated_text_hindi = GoogleTranslator(source="auto", target="hi").translate(cleaned_policy_text)
    
    # Translate to Kannada
    translated_text_kannada = GoogleTranslator(source="auto", target="kn").translate(cleaned_policy_text)

    # Display translations
    st.subheader("Translated Text (Hindi)")
    st.write(translated_text_hindi[:500])  # Show first 500 characters

    st.subheader("Translated Text (Kannada)")
    st.write(translated_text_kannada[:500])  # Show first 500 characters

    # Convert text to speech in Kannada
    if st.button("Generate Kannada Audio 🎙️"):
        tts = gTTS(translated_text_kannada, lang="kn")
        tts.save("Kannada_Speech.mp3")
        st.audio("Kannada_Speech.mp3")

st.markdown("🚀 Developed by Madhu M | AGRIVOICE")
