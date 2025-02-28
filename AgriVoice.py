import streamlit as st
import pdfplumber
from docx import Document
from deep_translator import GoogleTranslator
from gtts import gTTS
from transformers import pipeline

# ------------------- File Uploader -------------------
st.title("📂 AGRIVOICE: Translate & Summarize Instantly!")
uploaded_file = st.file_uploader("", type=["pdf", "docx"])

if uploaded_file:
    # Extract text from uploaded document
    def extract_text(file):
        if file.type == "application/pdf":
            with pdfplumber.open(file) as pdf:
                return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return "\n".join(para.text for para in Document(file).paragraphs)
        return ""

    policy_text = extract_text(uploaded_file)

    # Display extracted text
    st.subheader("📜 Extracted Text")
    st.write(policy_text[:2000] + "...")  # Show only the first 2000 characters for readability

    # ------------------- Translate Text -------------------
    def translate_text(text, lang):
        return GoogleTranslator(source="auto", target=lang).translate(text[:5000])  # Translate only first 5000 chars

    hindi_translation = translate_text(policy_text, "hi")
    kannada_translation = translate_text(policy_text, "kn")

    st.subheader("🇮🇳 Hindi Translation")
    st.write(hindi_translation)
    
    st.subheader("🇮🇳 Kannada Translation")
    st.write(kannada_translation)

    # ------------------- Generate Summary -------------------
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def summarize_text(text):
        return summarizer(text[:1000], max_length=150, min_length=50, do_sample=False)[0]["summary_text"]

    english_summary = summarize_text(policy_text)

    # Translate summary
    hindi_summary = translate_text(english_summary, "hi")
    kannada_summary = translate_text(english_summary, "kn")

    st.subheader("📌 Hindi Summary")
    st.write(hindi_summary)

    st.subheader("📌 Kannada Summary")
    st.write(kannada_summary)

    # ------------------- Convert Kannada Summary to Speech -------------------
    if st.button("🎙️ Generate Kannada Audio"):
        tts = gTTS(kannada_summary, lang="kn")
        tts.save("kannada_summary.mp3")
        st.audio("kannada_summary.mp3", format="audio/mp3")
