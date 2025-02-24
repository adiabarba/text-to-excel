import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.title("Extract Data from Text File to Excel")

def extract_value(pattern, text, default="N/A"):
    """
    Searches for the first match of `pattern` in `text`, ignoring case and
    allowing multiline matching (DOTALL). If not found, returns `default`.
    """
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else default

def categorize_indications(text):
    """
    Categorizes the indication based on keywords. If none are found,
    returns "Other".
    """
    indication_options = {
        "constipation": "Constipation",
        "incontinence": "Incontinence",
        "hirschsprung": "s/p Hirschprung",
        "anorectal malformation": "Anorectal malformation",
        "anal tear": "Anal Tear",
        "perianal tear": "Perianal Tear",  # Fixed the missing value
        "spina bifida": "Spina bifida"
    }
    
    text_lower = text.lower() if text != "N/A" else ""
    for key, value in indication_options.items():
        if key in text_lower:
            return value
    return "Other"

uploaded_file = st.file_uploader("Upload the text file (e.g. Patient3.txt)", type=["txt"])

if uploaded_file is not None:
    # Read the file content
    data = uploaded_file.read().decode("utf-8")
    
    # Define the column names you want in your final Excel file
    column_names = [
        "Patient Name", "Patient ID", "Gender", "Date of Birth", "Physician", 
        "Operator", "Referring Physician", "Examination Date", "Height", 
        "Weight", "Mean Sphincter Pressure (Rectal ref) (mmHg)",
        "Max Sphincter Pressure (Rect

