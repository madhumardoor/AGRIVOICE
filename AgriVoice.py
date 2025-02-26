import streamlit as st
import PyPDF2
import docx
from googletrans import Translator
import pyttsx3

# Initialize translator and TTS engine
translator = Translator()
tts = pyttsx3.init()

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def translate_text(text, target_lang):
    return translator.translate(text, dest=target_lang).text

def text_to_speech(text, language):
    tts.setProperty('rate', 150)
    tts.setProperty('voice', language)
    tts.say(text)
    tts.runAndWait()

# Streamlit UI
st.title("📄 File Extraction, Translation & TTS App")
st.subheader("Developed by Madhu M | AGRIVOICE 🌿")

uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"], key="file_uploader")

if uploaded_file:
    file_type = uploaded_file.type
    st.success(f"Uploaded: {uploaded_file.name}")
    
    if file_type == "application/pdf":
        extracted_text = extract_text_from_pdf(uploaded_file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        extracted_text = extract_text_from_docx(uploaded_file)
    else:
        extracted_text = ""
    
    if extracted_text:
        st.subheader("Extracted Text:")
        st.text_area("", extracted_text, height=200)
        
        # Translation Options
        target_lang = st.selectbox("Translate to:", ["hi", "kn"], format_func=lambda x: "Hindi" if x == "hi" else "Kannada")
        
        if st.button("Translate"):
            translated_text = translate_text(extracted_text, target_lang)
            st.subheader("Translated Text:")
            st.text_area("", translated_text, height=200)
            
            if st.button("Play Audio"):
                lang_voice = 'hi' if target_lang == "hi" else 'kn'
                text_to_speech(translated_text, lang_voice)
                st.success("Playing Translated Speech!")
    else:
        st.warning("No text extracted. Please upload a valid file.")
