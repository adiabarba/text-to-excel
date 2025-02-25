import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.title("Extract Data from Multiple Text Files to Excel")

def extract_value(pattern, text, default="N/A"):
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else default

def categorize_indications(text):
    indication_options = {
        "constipation": "Constipation",
        "incontinence": "Incontinence",
        "hirschsprung": "s/p Hirschprung",
        "anorectal malformation": "Anorectal malformation",
        "anal tear": "Anal Tear",
        "perianal tear": "Perianal Tear",
        "s/p perianal tear": "s/p Perianal Tear",
        "spina bifida": "Spina bifida"
    }
    
    text_lower = text.lower() if text != "N/A" else ""
    
    for key in indication_options.keys():
        if key in text_lower:
            return indication_options[key]  
    return "Other"

# Allow multiple file uploads
uploaded_files = st.file_uploader("Upload text files", type=["txt"], accept_multiple_files=True)

if uploaded_files:
    all_data = []  # List to store all extracted patient data

    for uploaded_file in uploaded_files:
        data = uploaded_file.read().decode("utf-8")
        
        # Capture Patient Name & Patient ID
        patient_name, patient_id = "N/A", "N/A"
        pat_match = re.search(r"(?i)Patient:\s*(.+?)\s*\n\s*(\d{6,})", data)

        if
