import streamlit as st
import pdfplumber
import re
import faiss
import numpy as np
import os
import google.generativeai as genai
import torch
from sentence_transformers import SentenceTransformer
from gtts import gTTS
import base64

# Load API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("\u26a0\ufe0f Missing GEMINI API Key. Set GEMINI_API_KEY in your environment variables.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# Load FAISS index
INDEX_PATH = "agri_vector.index"
if not os.path.exists(INDEX_PATH):
    st.error(f"\u26a0\ufe0f FAISS index file `{INDEX_PATH}` not found. Generate it first.")
    st.stop()
index = faiss.read_index(INDEX_PATH)

# Load Sentence Transformer Model
model = SentenceTransformer("all-MiniLM-L6-v2")

documents = [
    "How to improve soil fertility?",
    "Best irrigation techniques for rice farming",
    "Effective pest control methods in agriculture",
    "How to increase crop yield efficiently?"
]

def extract_text_from_pdf(file):
    """Extract text from PDF."""
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n\n"
    return text

def clean_text(text):
    """Clean extracted text."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9.,\n\s]", "", text)
    return text.lower()

def ask_gemini(prompt):
    """Use Gemini API to process tasks."""
    try:
        model_gemini = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model_gemini.generate_content(prompt)
        return response.text.strip() if response else "No response from AI."
    except Exception as e:
        return f"Error: {str(e)}"

def text_to_speech(text, lang):
    """Convert text to speech using gTTS."""
    tts = gTTS(text=text, lang=lang)
    tts.save("output.mp3")
    with open("output.mp3", "rb") as f:
        audio_bytes = f.read()
    return base64.b64encode(audio_bytes).decode()

# Streamlit Styling
st.markdown(
    """
    <style>
        body {
            background-color: #D0E2F2;
        }
        .stTextArea, .stTextInput {
            border-radius: 10px;
            padding: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("\U0001F33E AgriVoice: AI-Powered Agricultural Chatbot")

uploaded_file = st.file_uploader("\U0001F4C4 Upload an Agricultural PDF", type=["pdf"])
if uploaded_file:
    extracted_text = extract_text_from_pdf(uploaded_file)
    cleaned_text = clean_text(extracted_text)
    st.text_area("\U0001F4DC Extracted Text", extracted_text, height=200)
    st.text_area("\U0001F9F9 Cleaned Text", cleaned_text, height=200)
    
    # Translation using Gemini
    lang = st.selectbox("\U0001F310 Select Language", ["kn", "hi", "ta", "te", "mr", "bn"], format_func=lambda x: {
        "kn": "Kannada", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "mr": "Marathi", "bn": "Bengali"
    }[x])
    prompt = f"Translate the following text to {lang}:\n\n{cleaned_text}"
    translated_text = ask_gemini(prompt)
    st.text_area("\U0001F30D Translated Text", translated_text, height=200)
    
    # Speech Translation
    if st.button("\U0001F50A Play Translation"):
        speech_data = text_to_speech(translated_text, lang)
        st.audio(base64.b64decode(speech_data), format="audio/mp3")

st.subheader("\u2753 Ask a Farming Question")
query = st.text_input("\U0001F50D Enter your question")
if st.button("Get Answer"):
    if uploaded_file:
        if query:
            query_embedding = model.encode([query])
            query_embedding = np.array(query_embedding).reshape(1, -1)
            D, I = index.search(query_embedding, k=2)
            retrieved_text = [documents[i] for i in I[0] if 0 <= i < len(documents)]
            context = "\n".join(retrieved_text)
            response_text = ask_gemini(f"Context: {context}\n\nQuestion: {query}")
            st.subheader("\U0001F916 AI Response:")
            st.write(response_text)
        else:
            st.warning("\u26a0\ufe0f Please enter a question!")
    else:
        st.warning("\u26a0\ufe0f Please upload a PDF first!")
