import streamlit as st
import pdfplumber
import os
from docx import Document
from transformers import pipeline
from deep_translator import GoogleTranslator
from gtts import gTTS

# ------------------- Streamlit UI -------------------
st.title("📄 AGRIVOICE: Translate & Summarize Documents")
st.write("Upload a **PDF** or **DOCX** file to extract text, summarize, translate, and generate speech.")

uploaded_file = st.file_uploader("📂 Upload File", type=["pdf", "docx"])

# ------------------- Extract Text from PDF -------------------
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n\n"
    except Exception as e:
        st.error(f"❌ Error reading PDF: {e}")
    return text

# ------------------- Extract Text from DOCX -------------------
def extract_text_from_docx(uploaded_file):
    text = ""
    try:
        doc = Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"❌ Error reading DOCX: {e}")
    return text

# ------------------- Summarization -------------------
try:
    summarizer = pipeline("summarization")
except Exception as e:
    st.error(f"❌ Error loading summarization model: {e}")

def summarize_text(text):
    try:
        return summarizer(text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
    except Exception as e:
        st.error(f"❌ Error summarizing text: {e}")
        return ""

# ------------------- Main Logic -------------------
if uploaded_file:
    st.success("✅ File Uploaded Successfully!")

    # Extract text based on file type
    if uploaded_file.type == "application/pdf":
        policy_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        policy_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("❌ Unsupported file type!")
        policy_text = ""

    # Display extracted text
    if policy_text:
        st.subheader("📜 Extracted Text")
        st.text_area("📝 Text Preview", policy_text[:500], height=200)

        # ------------------- Summarization -------------------
        summary_english = summarize_text(policy_text)
        st.subheader("📌 Summary")
        st.write(summary_english)

        # ------------------- Translation -------------------
        translation_option = st.radio("🌍 Translate to:", ("No Translation", "Hindi", "Kannada"), index=0)

        if translation_option != "No Translation":
            target_lang = "hi" if translation_option == "Hindi" else "kn"
            translated_summary = GoogleTranslator(source="auto", target=target_lang).translate(summary_english)
            st.subheader(f"📖 Summary in {translation_option}")
            st.write(translated_summary)

            # ------------------- Convert to Speech -------------------
            if st.button(f"🎙️ Generate {translation_option} Audio"):
                tts = gTTS(translated_summary, lang=target_lang)
                audio_filename = "summary_audio.mp3"
                tts.save(audio_filename)
                st.success("✅ Audio Generated Successfully!")
                st.audio(audio_filename, format="audio/mp3")
