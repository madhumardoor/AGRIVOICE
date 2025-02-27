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

# Set OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

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
    translated = translator.translate(text, dest=lang)
    return translated.text

def text_to_speech(text, lang):
    """Convert text to speech."""
    tts = gTTS(text=text, lang=lang)
    tts.save("output.mp3")
    return "output.mp3"

def ask_ai(question):
    """Get AI-generated answers to farmers' questions."""
    client = openai.OpenAI(api_key="YOUR_OPENAI_API_KEY")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content.strip()

# Streamlit UI
st.title("\U0001F33E Farmer's AI Assistant")
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
    lang = st.selectbox("Select Language", ["kn", "hi", "ta", "te", "mr", "bn"], format_func=lambda x: {"kn": "Kannada", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "mr": "Marathi", "bn": "Bengali"}[x])
    translated_text = translate_text(cleaned_text, lang)
    
    st.subheader("Translated Text")
    st.text_area("", translated_text, height=200)
    
    # Text to Speech
    if st.button("\U0001F3A4 Listen to Translation"):
        audio_file = text_to_speech(translated_text, lang)
        st.audio(audio_file, format="audio/mp3")

# AI Question-Answering
st.subheader("Ask a Farming Question")
question = st.text_input("Enter your question")
if st.button("Get Answer"):
    if question:
        answer = ask_ai(question)
        st.write("\U0001F916 AI Answer:", answer)
    else:
        st.warning("Please enter a question!")
