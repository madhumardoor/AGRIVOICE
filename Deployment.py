# -*- coding: utf-8 -*-
"""
Created on Sun Mar  2 16:55:37 2025

@author: PC
"""

#Optical Character Recognition (OCR) for Text Extraction

import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

#Text Summarization with Transformer Models
from transformers import pipeline
summarizer = pipeline('summarization')
def summarize_text(text):
    summary = summarizer(text, max_length=150, min_length=40, do_sample=False)
    return summary[0]['summary_text']

#Text-to-Speech (TTS) Conversion
from gtts import gTTS
def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)
    #Language Translation (Optional)
from googletrans import Translator
def translate_text(text, dest_language):
    translator = Translator()
    translation = translator.translate(text, dest=dest_language)
    return translation.text
#User Interface Development
from flask import Flask, request, render_template
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Save the file and process it
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        text = extract_text_from_image(file_path)
        summary = summarize_text(text)
        audio_file = 'static/output.mp3'
        text_to_speech(summary, audio_file)
        return render_template('result.html', summary=summary, audio_file=audio_file)

if __name__ == '__main__':
    app.run(debug=True)
