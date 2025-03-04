import streamlit as st
import pdfplumber
import faiss
import numpy as np
import os
import google.generativeai as genai
import asyncio
import torch
from sentence_transformers import SentenceTransformer
from gtts import gTTS

# Configure API
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("⚠️ API Key is missing! Set GOOGLE_API_KEY as an environment variable.")
    st.stop()

genai.configure(api_key=API_KEY)

# Load FAISS Index
INDEX_PATH = "agri_vector.index"
if not os.path.exists(INDEX_PATH):
    st.error(f"⚠️ FAISS index file `{INDEX_PATH}` not found. Upload or generate the index.")
    st.stop()
try:
    index = faiss.read_index(INDEX_PATH)
except Exception as e:
    st.error(f"⚠️ Error loading FAISS index: {e}")
    st.stop()

# Load embedding model
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    st.error(f"⚠️ Error loading embedding model: {e}")
    st.stop()

documents = [
    "How to improve soil fertility?",
    "Best irrigation techniques for rice farming",
    "Effective pest control methods in agriculture",
    "How to increase crop yield efficiently?"
]

# Streamlit UI
st.markdown(
    """
    <style>
        body { background-color: #ADD8E6; }
    </style>
    """,
    unsafe_allow_html=True
)
st.title("🌱 AgriVoice: AI-Powered Agricultural Chatbot")

# File upload
uploaded_file = st.file_uploader("Upload an Agricultural PDF", type=["pdf"])

def extract_text_from_pdf(file):
    """Extract text from PDF."""
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n\n"
    return text

def text_to_speech(text, lang):
    """Convert text to speech."""
    tts = gTTS(text=text, lang=lang)
    audio_path = "output.mp3"
    tts.save(audio_path)
    return audio_path

def ask_ai(question, context):
    """Generate AI response using Google Gemini API."""
    try:
        model_gemini = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model_gemini.generate_content([f"Context: {context}\n\nQuestion: {question}"])
        return response.text.strip() if response else "No response from AI."
    except Exception as e:
        return f"Error: {str(e)}"

if uploaded_file:
    extracted_text = extract_text_from_pdf(uploaded_file)
    st.subheader("Extracted Text")
    st.text_area("", extracted_text, height=200)

# AI Question-Answering
st.subheader("Ask a Farming Question")
question = st.text_input("Enter your question")
if st.button("Get Answer"):
    if uploaded_file and extracted_text:
        if question:
            answer = ask_ai(question, extracted_text)
            st.write("🤖Answer:", answer)
        else:
            st.warning("Please enter a question!")
    else:
        st.warning("Please upload a PDF first!")

# Translation & Speech
lang = st.selectbox("Select Language", ["kn", "hi", "ta", "te", "mr", "bn"], format_func=lambda x: {
    "kn": "Kannada", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "mr": "Marathi", "bn": "Bengali"
}[x])

if st.button("🎤 Listen to Answer"):
    if question and extracted_text:
        answer = ask_ai(question, extracted_text)
        audio_file = text_to_speech(answer, lang)
        st.audio(audio_file, format="audio/mp3")
    else:
        st.warning("Upload a PDF and ask a question first!")
