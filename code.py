# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 21:48:57 2025

@author: PC
"""

import pdfplumber

# Path to the uploaded file
pdf_path =r"F:\app\AGRIVOICE-1\PMKisanSamanNidhi.pdf"

# Extract text from the PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:  # Ensure page has text
                text += extracted_text + "\n\n"
    return text

# Run the function and save the extracted text
policy_text = extract_text_from_pdf(pdf_path)

# Save extracted text to a file
text_file_path =r"F:\app\AgriVoice\policy_pdfs\policy_pdfs\PMKisanSamanNidhi_extracted.txt"


with open(text_file_path, "w", encoding="utf-8") as file:
    file.write(policy_text)

print("Text extraction complete. Saved to:", text_file_path)

import re
import nltk
from nltk.corpus import stopwords

# Download stopwords
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

# Function to clean text
def clean_text(text):
    text = re.sub(r"\s+", " ", text)  # Remove extra spaces
    text = re.sub(r"[^a-zA-Z0-9.,\n\s]", "", text)  # Remove special characters
    text = text.lower()  # Convert to lowercase
    text = " ".join([word for word in text.split() if word not in stop_words])  # Remove stopwords
    return text

# Apply text cleaning
cleaned_policy_text = clean_text(policy_text)

# Save cleaned text
clean_text_file =r"F:\app\AgriVoice\policy_pdfs\policy_pdfs\PMKisanSamanNidhi_cleaned.txt"
with open(clean_text_file, "w", encoding="utf-8") as file:
    file.write(cleaned_policy_text)

print("Text cleaning complete. Saved to:", clean_text_file)

from nltk.tokenize import sent_tokenize, word_tokenize

nltk.download("punkt")  # Download tokenizer models

# Tokenize into sentences
sentences = sent_tokenize(cleaned_policy_text)

# Tokenize into words
words = word_tokenize(cleaned_policy_text)

print("Sample Sentences:", sentences[:3])
print("Sample Words:", words[:10])

from deep_translator import GoogleTranslator

# Translate text to Hindi
translated_text = GoogleTranslator(source="auto", target="hi").translate(cleaned_policy_text)

# Save translated text
translated_text_file =r"F:\app\AgriVoice\policy_pdfs\policy_pdfs\PMKisanSamanNidhi_translated_text.txt"
with open(translated_text_file, "w", encoding="utf-8") as file:
    file.write(translated_text)

print("Translation complete. Saved to:", translated_text_file)

from deep_translator import GoogleTranslator

def split_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

chunks = split_text(policy_text)
translated_chunks = []

for chunk in chunks:
    try:
        translated_chunks.append(GoogleTranslator(source="en", target="kn").translate(chunk))
    except Exception as e:
        print(f"Translation failed for chunk: {chunk[:50]}... Error: {e}")

translated_text = " ".join(translated_chunks)
print(translated_text)

translated_text_file = r"F:\app\AgriVoice\policy_pdfs\policy_pdfs\PMKisanSamanNidhi_Kannada_translated_text.txt"

with open(translated_text_file, "w", encoding="utf-8") as file:
    file.write(translated_text)

print("Kannada translation saved to:", translated_text_file)

from gtts import gTTS

tts = gTTS(translated_text, lang="kn")
tts.save("Kannada_Speech.mp3")

print("Kannada speech saved as Kannada_Speech.mp3")






