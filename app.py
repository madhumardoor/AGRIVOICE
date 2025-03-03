import streamlit as st
import faiss
import numpy as np
import os
import google.generativeai as genai
import asyncio
import torch
from sentence_transformers import SentenceTransformer

# Securely load API key
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("⚠️ API Key is missing! Please set GOOGLE_API_KEY as an environment variable.")
    st.stop()

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Ensure FAISS index file exists before loading
INDEX_PATH = "agri_vector.index"
if not os.path.exists(INDEX_PATH):
    st.error(f"⚠️ FAISS index file `{INDEX_PATH}` not found. Please upload or generate the index.")
    st.stop()

# Load FAISS vector database safely
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

# Sample stored documents (should be loaded dynamically in production)
documents = [
    "How to improve soil fertility?",
    "Best irrigation techniques for rice farming",
    "Effective pest control methods in agriculture",
    "How to increase crop yield efficiently?"
]

# Streamlit UI
st.title("🌱 AgriVoice: AI-Powered Agricultural Chatbot")

query = st.text_input("🔍 Ask an agricultural question:")

if st.button("Search"):
    if not query.strip():
        st.warning("⚠️ Please enter a question!")
    else:
        try:
            # Encode query
            query_embedding = model.encode([query])
            query_embedding = np.array(query_embedding).reshape(1, -1)

            # Search FAISS index for top matches
            D, I = index.search(query_embedding, k=2)
            retrieved_text = [documents[i] for i in I[0] if 0 <= i < len(documents)]

            st.subheader("🔍 Relevant Context Found:")
            for i, text in enumerate(retrieved_text, 1):
                st.write(f"**{i}.** {text}")

            # Generate response using Gemini
            model_gemini = genai.GenerativeModel("gemini-1.5-pro-latest")

            async def fetch_response():
                response = await asyncio.to_thread(model_gemini.generate_content, [f"Based on this info: {retrieved_text}, {query}"])
                return response.text

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response_text = loop.run_until_complete(fetch_response())

            st.subheader("🤖 Gemini AI Response:")
            st.write(response_text)

        except Exception as e:
            st.error(f"⚠️ API Error: {str(e)}")
