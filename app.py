import os
import pdfplumber
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
from deep_translator import GoogleTranslator
from gtts import gTTS
import sys
sys.stdout.reconfigure(encoding='utf-8')


# Ensure required NLTK packages are downloaded
nltk.download("punkt")

# Folder containing multiple PDFs
pdf_folder = "F:/MLT NOTES/zeopto/k-10/0000950170-23-001409-xbrl/project/policy_pdfs"
output_folder = "F:/MLT NOTES/zeopto/k-10/0000950170-23-001409-xbrl/project/processed_policies"

os.makedirs(output_folder, exist_ok=True)

def extract_text_from_pdf(pdf_path): 
    """Extracts text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n\n"
    return text

def clean_text(text):
    """Cleans extracted text by removing extra spaces and special characters."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9.,\n\s]", "", text)
    text = text.lower()
    return text

def translate_to_kannada(text):
    """Translates text from English to Kannada using Google Translator."""
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]  # Google API limit
    translated_chunks = []
    for chunk in chunks:
        try:
            translated_chunks.append(GoogleTranslator(source="en", target="kn").translate(chunk))
        except Exception as e:
            print(f"Translation failed for chunk: {chunk[:50]}... Error: {e}")
    return " ".join(translated_chunks)

def summarize_text(text):
    """Summarizes Kannada text using TextRank method."""
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    word_freq = Counter(words)

    sentence_scores = {sent: sum(word_freq[word] for word in word_tokenize(sent)) for sent in sentences}
    summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:5]
    
    return " ".join(summary_sentences)

def text_to_speech(text, output_path):
    """Converts Kannada text to speech and saves as MP3."""
    tts = gTTS(text, lang="kn")
    tts.save(output_path)

# Loop through all PDFs in the folder
for pdf_file in os.listdir(pdf_folder):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        base_filename = os.path.splitext(pdf_file)[0]

        print(f"Processing {pdf_file}...")

        # Extract text
        extracted_text = extract_text_from_pdf(pdf_path)

        # Clean text
        cleaned_text = clean_text(extracted_text)

        # Translate to Kannada
        kannada_text = translate_to_kannada(cleaned_text)

        # Summarize Kannada text
        kannada_summary = summarize_text(kannada_text)

        # Save translated Kannada text
        kannada_text_file = os.path.join(output_folder, f"{base_filename}_Kannada.txt")
        with open(kannada_text_file, "w", encoding="utf-8") as file:
            file.write(kannada_text)

        # Save summarized Kannada text
        kannada_summary_file = os.path.join(output_folder, f"{base_filename}_Summary_Kannada.txt")
        with open(kannada_summary_file, "w", encoding="utf-8") as file:
            file.write(kannada_summary)

        # Convert summary to speech
        kannada_audio_file = os.path.join(output_folder, f"{base_filename}_Summary_Kannada.mp3")
        text_to_speech(kannada_summary, kannada_audio_file)

        print(f"✅ Completed: {pdf_file} - Summary & Speech Saved!")

print("🎉 All PDFs processed successfully!")