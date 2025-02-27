import streamlit as st
import pdfplumber
import re
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n\n"
    return text

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9.,\n\s]", "", text)
    text = text.lower()
    text = " ".join([word for word in text.split() if word not in stop_words])
    return text

st.title("📄 PDF Text Extractor & Cleaner")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
if uploaded_file:
    extracted_text = extract_text_from_pdf(uploaded_file)
    cleaned_text = clean_text(extracted_text)
    st.subheader("Extracted Text")
    st.text_area("", extracted_text, height=200)
    st.subheader("Cleaned Text")
    st.text_area("", cleaned_text, height=200)
