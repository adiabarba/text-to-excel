import streamlit as st
import pandas as pd
import re
import codecs  # ✅ No need for external libraries
from io import BytesIO

st.title("Extract Data from Multiple Text Files to Excel")

def extract_value(pattern, text, default="N/A"):
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else default

def extract_max_pressure(pattern, text, default="N/A"):
    matches = re.findall(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if matches:
        numeric_values = [float(m) for m in matches if m.replace('.', '', 1).isdigit()]
        return str(max(numeric_values)) if numeric_values else default
    return default

def categorize_indications(text):
    indication_options = {
        "constipation": "Constipation",
        "incontinence": "Incontinence",
        "hirschsprung": "s/p Hirschprung",
        "anorectal malformation": "Anorectal malformation",
        "anal tear": "Anal Tear",
        "perianal tear": "Perianal Tear",
        "s/p perianal tear": "s/p Perianal Tear",
        "spina bifida": "Spina bifida",
        
        # ✅ Hebrew translations
        "עצירות": "Refractory Constipation",
        "מגהרקטום": "Megarectum",
        "לחץ בסיס גבוה": "High Basal Pressure"
    }
    
    text_lower = text.lower() if text != "N/A" else ""
    
    for key, value in indication_options.items():
        if key in text_lower or key in text:
            return value  
    return "Other"

# Allow multiple file uploads
uploaded_files = st.file_uploader("Upload text files", type=["txt"], accept_multiple_files=True)

if uploaded_files:
    all_data = []  # Store extracted data

    for uploaded_file in uploaded_files:
        # ✅ Automatically handle encoding without `chardet`
        raw_data = uploaded_file.read()
        try:
            data = raw_data.decode("utf-8")  # Try UTF-8 first
        except UnicodeDecodeError:
            try:
                data = raw_data.decode("windows-1255")  # Try Windows-1255 (Hebrew)
            except UnicodeDecodeError:
                data = raw_data.decode("ISO-8859-8", errors="replace")  # Default to Hebrew encoding

        # Capture Patient Name & Patient ID
        patient_name, patient_id = "N/A", "N/A"
        pat_match = re.search(r"(?i)Patient:\s*(.+?)\s*\n\s*(\d{6,})", data)

        if pat_match:
            patient_name = pat_match.group(1).strip()
            patient_id = pat_match.group(2).strip()
        else:
            fallback_name = re.search(r"(?i)^Patient:\s*(.+)$", data, flags=re.MULTILINE)
            if fallback_name:
                patient_name = fallback_name.group(1).strip()
            fallback_id = re.search(r"(?i)(?:Patient\s+ID|ID\s+Number)\s*[:]?[\s]*(\w+)", data)
            if fallback_id:
                patient_id = fallback_id.group(1).strip()

        # Extract data
        extracted_data = {
            "Patient Name": patient_name,
            "Patient ID": patient_id,
            "Gender": extract_value(r"Gender\s*[:]?[\s]*([\w]+)", data, default="N/A"),
            "Date of Birth": extract_value(r"(?:DOB|Date of Birth)\s*[:]?[\s]*([\d/]+)", data, default="N/A"),
            "Physician": extract_value(r"Physician\s*[:]?[\s]*(.*)", data),
            "Operator": extract_value(r"Operator\s*[:]?[\s]*(.*)", data),
            "Referring Physician": extract_value(r"Referring Physician\s*[:]?[\s]*(.*)", data),
            "Examination Date": extract_value(r"Examination Date\s*[:]?[\s]*(.*)", data),
            "Height": extract_value(r"Height\s*[:]?[\s]*(\d{1,3}\.?\d*)", data),
            "Weight": extract_value(r"Weight\s*[:]?[\s]*(\d{1,3}\.?\d*)", data),

            # ✅ Fixed duplicate max pressure values
            "Mean Sphincter Pressure (Rectal ref) (mmHg)": extract_max_pressure(
                r"Mean\s*Sphincter\s*Pressure.*?rectal\s*ref.*?\(mmhg\)\s*([\-\d\.]+)", data),
            "Max Sphincter Pressure (Rectal ref) (mmHg)": extract_max_pressure(
                r"Max\.?\s*Sphincter\s*Pressure.*?rectal\s*ref.*?\(mmhg\)\s*([\-\d\.]+)", data),
            "Max Sphincter Pressure (Abs. ref) (mmHg)": extract_max_pressure(
                r"Max\.?\s*Sphincter\s*Pressure.*?abs\.?\s*ref.*?\(mmhg\)\s*([\-\d\.]+)", data),
            "Mean Sphincter Pressure (Abs. ref) (mmHg)": extract_max_pressure(
                r"Mean\s*Sphincter\s*Pressure.*?abs\.?\s*ref.*?\(mmhg\)\s*([\-\d\.]+)", data),

            "Length of HPZ (cm)": extract_value(
                r"Length\s*of\s*HPZ.*?\(cm\)\s*([\-\d\.]+)", data),
            "Verge to Center Length (cm)": extract_value(
                r"Length\s*verge\s*to\s*center.*?\(cm\)\s*([\-\d\.]+)", data),
            "Residual Anal Pressure (mmHg)": extract_value(
                r"Residual\s+Anal\s+Pressure.*?\(mmhg\)\s*([\-\d\.]+)", data),
            "Anal Relaxation (%)": extract_value(
                r"Percent\s+anal\s+relaxation.*?\(%\)\s*([\-\d\.]+)", data),
            "First Sensation (cc)": extract_value(
                r"First\s+sensation.*?\(cc\)\s*([\-\d\.]+)", data),
            "Urge to Defecate (cc)": extract_value(
                r"Urge\s+to\s+defecate.*?\(cc\)\s*([\-\d\.]+)", data),
            "Rectoanal Pressure Differential (mmHg)": extract_value(
                r"Rectoanal\s+pressure\s+differential.*?\(mmhg\)\s*([\-\d\.]+)", data),
            "RAIR": "Present" if "RAIR" in data else "Not Present",

            # ✅ Now correctly detects Hebrew Indications
            "Indications": categorize_indications(
                extract_value(r"(?i)Indications\s*[:]?[\s]*(.*?)(?:\n[A-Z]|[\u0590-\u05FF]+\n|$)", data)
            ),

            "Diagnoses": extract_value(
                r"Diagnoses\s*\(London classification\)\s*(.*)", data)
        }

        all_data.append(extracted_data)

    # Convert all extracted data into a single DataFrame
    df = pd.DataFrame(all_data)

    # Display all extracted data
    st.write("## Final Extracted Data")
    st.dataframe(df)

    # Save to Excel
    output_excel = BytesIO()
    df.to_excel(output_excel, index=False, sheet_name="Sheet1")
    output_excel.seek(0)

    # Download button
    st.download_button(
        label="Download Consolidated Excel File",
        data=output_excel,
        file_name="Combined_Patient_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
