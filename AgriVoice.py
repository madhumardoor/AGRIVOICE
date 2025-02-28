import streamlit as st
import pdfplumber
import re
import nltk
import asyncio
from nltk.corpus import stopwords
from googletrans import Translator
from gtts import gTTS
import google.generativeai as genai
import os

# ✅ Fix: Ensure stopwords are only downloaded if missing
nltk.data.path.append("/home/appuser/nltk_data")
try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))

# ✅ Set up Google Gemini API key (replace with your actual key)
genai.configure(api_key=st.secrets["YOUR_GEMINI_API_KEY"])

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

def ask_ai(question):
    """Get AI-generated answers using Google Gemini API."""
    try:
        model = genai.GenerativeModel("gemini-pro")  # Using Gemini AI model
        response = model.generate_content(question)
        return response.text.strip() if response.text else "No response."
    except Exception as e:
        return f"Error: {str(e)}"

# ✅ Streamlit UI
st.title("🌾 Farmer's AI Assistant")
st.write("Ask questions, translate agricultural content, and listen to responses!")

# ✅ File upload
uploaded_file = st.file_uploader("Upload an Agricultural PDF", type=["pdf"])
if uploaded_file:
    extracted_text = extract_text_from_pdf(uploaded_file)
    cleaned_text = clean_text(extracted_text)
    
    st.subheader("Extracted Text")
    st.text_area("Extracted Text", extracted_text, height=200, label_visibility="collapsed")
    
    st.subheader("Cleaned Text")
    st.text_area("Cleaned Text", cleaned_text, height=200, label_visibility="collapsed")
    
    # ✅ Language selection
    lang = st.selectbox("Select Language", ["kn", "hi", "ta", "te", "mr", "bn"], 
                        format_func=lambda x: {"kn": "Kannada", "hi": "Hindi", "ta": "Tamil", 
                                               "te": "Telugu", "mr": "Marathi", "bn": "Bengali"}[x])
    
    translated_text = translate_text(cleaned_text, lang)
    
    st.subheader("Translated Text")
    st.text_area("Translated Text", translated_text, height=200, label_visibility="collapsed")
    
    # ✅ Text to Speech
    if st.button("🎤 Listen to Translation"):
        audio_file = text_to_speech(translated_text, lang)
        st.audio(audio_file, format="audio/mp3")

# ✅ AI Question-Answering
st.subheader("Ask a Farming Question")
question = st.text_input("Enter your question")
if st.button("Get Answer"):
    if question:
        answer = ask_ai(question)
        st.write("🤖 AI Answer:", answer)
    else:
        st.warning("Please enter a question!")
