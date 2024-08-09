import streamlit as st
import io
import base64
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# Configure the Gemini API
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Set up the model
model = genai.GenerativeModel('gemini-1.5-pro')

# check for pdf
def is_pdf(file):
    return file.name.lower().endswith('.pdf')

# check for image
def is_image(file):
    return file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))

# Get the response
def get_gemini_response(input_text, content):
    if content is None:
        content = ""
    response = model.generate_content([input_text, content])
    return response.text

# Encode the image
def encode_image(image_file):
    with Image.open(image_file) as img:
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return base64.b64encode(img_byte_arr).decode('utf-8')

# Extract text from pdf
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(io.BytesIO(pdf_file.getvalue()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Construct the prompt
prompt = """
Extract the following information from the given invoice:
1. Customer details
2. Products
3. Total Amount

Please format the output as follows:
Customer Details:
[Extracted customer details]

Products:
[List of extracted products]

Total Amount:
[Extracted total amount]
"""

# process file 
def process_file(uploaded_file):
    # process pdf
    if is_pdf(uploaded_file):
        content = extract_text_from_pdf(uploaded_file)
        print(content)
        return get_gemini_response(prompt + "\n\nHere's the extracted text from the PDF:\n" + content, None)
    # process image
    elif is_image(uploaded_file):
        encoded_image = encode_image(uploaded_file)
        image_part = {
            "mime_type": f"image/{uploaded_file.name.split('.')[-1]}",
            "data": encoded_image
        }
        return get_gemini_response(prompt, image_part)
    else:
        raise ValueError("Unsupported file type. Please provide a PDF or image file.")

st.title("Invoice Details Extractor")

uploaded_file = st.file_uploader("Choose a PDF or image file", type=["pdf", "png", "jpg", "jpeg", "bmp", "gif"])

if uploaded_file is not None:
    st.write("File uploaded successfully!")
    
    if st.button("Extract Details"):
        try:
            details = process_file(uploaded_file)
            st.subheader("Extracted Invoice Details:")
            st.write(details)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")