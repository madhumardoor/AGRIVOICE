import streamlit as st
import pdfplumber
import re
import nltk
import faiss
import numpy as np
import os
import google.generativeai as genai
import asyncio
import torch
from sentence_transformers import SentenceTransformer
from googletrans import Translator
from gtts import gTTS
from nltk.corpus import stopwords

# Download stopwords
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

# Load API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GEMINI_API_KEY or not GOOGLE_API_KEY:
    st.error("⚠️ Missing API Keys. Set GEMINI_API_KEY and GOOGLE_API_KEY in your environment variables.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# Load FAISS index
INDEX_PATH = "agri_vector.index"
if not os.path.exists(INDEX_PATH):
    st.error(f"⚠️ FAISS index file `{INDEX_PATH}` not found. Please generate it first.")
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

# Sample stored documents (this should be dynamically updated)
documents = [
    "How to improve soil fertility?",
    "Best irrigation techniques for rice farming",
    "Effective pest control methods in agriculture",
    "How to increase crop yield efficiently?"
]

# Functions
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
    text = text.lower()
    text = " ".join([word for word in text.split() if word not in stop_words])
    return text

def translate_text(text, lang):
    """Translate text to the selected language."""
    translator = Translator()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    translated = loop.run_until_complete(translator.translate(text, dest=lang))
    return translated.text if translated else "Translation failed."

def text_to_speech(text, lang):
    """Convert text to speech."""
    tts = gTTS(text=text, lang=lang)
    tts.save("output.mp3")
    return "output.mp3"

def ask_ai(question, context):
    """Generate AI responses using Google Gemini."""
    try:
        model_gemini = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model_gemini.generate_content(f"Context: {context}\n\nQuestion: {question}")
        return response.text.strip() if response else "No response from AI."
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("🌾 AgriVoice: AI-Powered Agricultural Chatbot")

# File upload
uploaded_file = st.file_uploader("📄 Upload an Agricultural PDF", type=["pdf"])
if uploaded_file:
    extracted_text = extract_text_from_pdf(uploaded_file)
    cleaned_text = clean_text(extracted_text)

    st.subheader("📜 Extracted Text")
    st.text_area("", extracted_text, height=200)

    st.subheader("🧹 Cleaned Text")
    st.text_area("", cleaned_text, height=200)

    # Language translation
    lang = st.selectbox(
        "🌍 Select Language", 
        ["kn", "hi", "ta", "te", "mr", "bn"], 
        format_func=lambda x: {"kn": "Kannada", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "mr": "Marathi", "bn": "Bengali"}[x]
    )
    translated_text = translate_text(cleaned_text, lang)

    st.subheader("🌐 Translated Text")
    st.text_area("", translated_text, height=200)

    # Text-to-speech
    if st.button("🎤 Listen to Translation"):
        audio_file = text_to_speech(translated_text, lang)
        st.audio(audio_file, format="audio/mp3")

# AI Question-Answering Section
st.subheader("❓ Ask a Farming Question")
query = st.text_input("🔍 Enter your question")
if st.button("Get Answer"):
    if uploaded_file and extracted_text:  # Ensure document is uploaded
        if query:
            # Encode query
            query_embedding = model.encode([query])
            query_embedding = np.array(query_embedding).reshape(1, -1)

            # Search FAISS index for top matches
            D, I = index.search(query_embedding, k=2)
            retrieved_text = [documents[i] for i in I[0] if 0 <= i < len(documents)]

            st.subheader("📚 Relevant Context Found:")
            for i, text in enumerate(retrieved_text, 1):
                st.write(f"**{i}.** {text}")

            # Generate response using AI
            async def fetch_response():
                response = await asyncio.to_thread(ask_ai, query, retrieved_text)
                return response

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response_text = loop.run_until_complete(fetch_response())

            st.subheader("🤖 AI Response:")
            st.write(response_text)
        else:
            st.warning("⚠️ Please enter a question!")
    else:
        st.warning("⚠️ Please upload a PDF first!")
