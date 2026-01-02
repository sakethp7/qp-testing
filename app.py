import base64
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import time
from PIL import Image
from io import BytesIO
from pydantic import BaseModel, Field
from typing import List, Optional
import streamlit as st
from prompts import get_question_paper_system_prompt
from models import QuestionPaper
from utils import pdf_to_images, pil_to_bytes
import json

load_dotenv()


def generate_question_paper(pdf_path: str):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    model = "gemini-3-flash-preview"

    pages = pdf_to_images(pdf_path)
    parts = []
    
    parts.append(
        types.Part.from_text(
            text="""
You are a question paper extraction engine.

Rules:
- Extract questions accurately.
- Preserve original wording.
- Keep page-wise separation.
- Do not hallucinate missing text.
"""
        )
    )
    for page_number, img in pages:
        parts.append(
            types.Part.from_text(
                text=f"Page {page_number}"
            )
        )
        parts.append(
            types.Part.from_bytes(
                data=pil_to_bytes(img),
                mime_type="image/jpeg"
            )
        )
    contents = [
        types.Content(
            role="user",
            parts=parts
        )
    ]
    
    generate_content_config = types.GenerateContentConfig(
        temperature=1.0,
        response_mime_type="application/json",
        response_schema=QuestionPaper.model_json_schema(),
        thinking_config=types.ThinkingConfig(thinking_level="medium"),
        system_instruction=get_question_paper_system_prompt()
    )

    a = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config
    )
    a = QuestionPaper.model_validate_json(a.text)
    
    return a


# Streamlit App
st.set_page_config(page_title="Question Paper Extractor", page_icon="📄", layout="wide")

st.title("📄 Question Paper Extractor")
st.write("Upload a question paper PDF to extract and structure the questions")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])

if uploaded_file is not None:
    # Save uploaded file temporarily
    with open("temp_qp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success("File uploaded successfully!")
    
    # Process button
    if st.button("Extract Questions", type="primary"):
        with st.spinner("Processing question paper... This may take a moment."):
            time_start = time.time()
            
            try:
                result = generate_question_paper("temp_qp.pdf")
                time_end = time.time()
                
                st.success(f"✅ Processing completed in {time_end - time_start:.2f} seconds")
                
                # Convert to JSON string
                json_output = result.model_dump_json(indent=2)
                
                # Display sections
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader("Extracted Content")
                    
                    # Display in a text area for easy copying
                    st.text_area(
                        "JSON Output (copyable)",
                        json_output,
                        height=400,
                        key="json_display"
                    )
                
                with col2:
                    st.subheader("Actions")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_output,
                        file_name="question_paper.json",
                        mime="application/json"
                    )
                    
                    # Stats
                    st.metric("Processing Time", f"{time_end - time_start:.2f}s")
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
            
            finally:
                # Cleanup temp file
                if os.path.exists("temp_qp.pdf"):
                    os.remove("temp_qp.pdf")
else:
    st.info("👆 Please upload a PDF file to get started")

# Footer
st.markdown("---")
st.caption("Question Paper Extractor powered by Gemini AI")
