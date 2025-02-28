import streamlit as st
import pdfplumber
import re
import nltk
from nltk.corpus import stopwords
from googletrans import Translator
from gtts import gTTS
import openai
import os

# Download stopwords
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

# Set OpenAI API key securely
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ OpenAI API key is missing. Please set it as an environment variable.")
openai.api_key = api_key

def extract_text_from_pdf(file):
    """Extract text from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n\n"
    except Exception as e:
        st.error(f"Error extracting text: {e}")
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
    try:
        translated = translator.translate(text, dest=lang)
        return translated.text
    except Exception as e:
        st.error(f"Translation error: {e}")
        return "Translation failed."

def text_to_speech(text, lang):
    """Convert text to speech."""
    try:
        tts = gTTS(text=text, lang=lang)
        audio_path = "output.mp3"
        tts.save(audio_path)
        return audio_path
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")
        return None

def ask_ai(question):
    """Get AI-generated answers to farmers' questions using OpenAI."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": question}]
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        st.error(f"AI API Error: {e}")
        return "AI is currently unavailable."

# Streamlit UI
st.title("🌾 Farmer's AI Assistant")
st.write("Ask questions, translate agricultural content, and listen to responses!")

# File upload
uploaded_file = st.file_uploader("Upload an Agricultural PDF", type=["pdf"])
if uploaded_file:
    extracted_text = extract_text_from_pdf(uploaded_file)
    cleaned_text = clean_text(extracted_text)
    
    st.subheader("Extracted Text")
    st.text_area("", extracted_text, height=200)
    
    st.subheader("Cleaned Text")
    st.text_area("", cleaned_text, height=200)
    
    # Language selection
    lang = st.selectbox("Select Language", ["kn", "hi", "ta", "te", "mr", "bn"], 
                        format_func=lambda x: {"kn": "Kannada", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "mr": "Marathi", "bn": "Bengali"}[x])
    translated_text = translate_text(cleaned_text, lang)
    
    st.subheader("Translated Text")
    st.text_area("", translated_text, height=200)
    
    # Text to Speech
    if st.button("🎤 Listen to Translation"):
        audio_file = text_to_speech(translated_text, lang)
        if audio_file:
            st.audio(audio_file, format="audio/mp3")

# AI Question-Answering
st.subheader("Ask a Farming Question")
question = st.text_input("Enter your question")
if st.button("Get Answer"):
    if question:
        answer = ask_ai(question)
        st.write("🤖 AI Answer:", answer)
    else:
        st.warning("Please enter a question!")
