import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.title("Extract Data from Text File to Excel")

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
        "s/p perianal tear": "s/p Perianal Tear",  # ✅ FIXED: Now explicitly matches "s/p perianal tear"
        "spina bifida": "Spina bifida"
    }
    
    text_lower = text.lower() if text != "N/A" else ""
    for key, value in indication_options.items():
        if key in text_lower:
            return value
    return "Other"

uploaded_file = st.file_uploader("Upload the text file (e.g. Patient3.txt)", type=["txt"])

if uploaded_file is not None:
    data = uploaded_file.read().decode("utf-8")
    
    # --- Capture Patient Name & Patient ID correctly ---
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
    
    # --- Extract Data ---
    extracted_data = {
        "Patient Name": patient_name,
        "Patient ID": patient_id,

        # ✅ FIXED Gender Extraction (Captures the correct word)
        "Gender": extract_value(r"Gender\s*[:]?[\s]*([\w]+)", data, default="N/A"),

        # ✅ FIXED DOB Extraction (No "Physician" contamination)
        "Date of Birth": extract_value(r"(?:DOB|Date of Birth)\s*[:]?[\s]*([\d/]+)", data, default="N/A"),

        "Physician": extract_value(r"Physician\s*[:]?[\s]*(.*)", data),
        "Operator": extract_value(r"Operator\s*[:]?[\s]*(.*)", data),
        "Referring Physician": extract_value(r"Referring Physician\s*[:]?[\s]*(.*)", data),
        "Examination Date": extract_value(r"Examination Date\s*[:]?[\s]*(.*)", data),
        "Height": extract_value(r"Height\s*[:]?[\s]*(\d{1,3}\.?\d*)", data),
        "Weight": extract_value(r"Weight\s*[:]?[\s]*(\d{1,3}\.?\d*)", data),
        
        "Mean Sphincter Pressure (Rectal ref) (mmHg)": extract_value(
            r"Mean\s*Sphincter\s*Pressure.*?rectal\s*ref.*?\(mmhg\)\s*([\-\d\.]+)",
            data
        ),
        "Max Sphincter Pressure (Rectal ref) (mmHg)": extract_value(
            r"Max\.?\s*Sphincter\s*Pressure.*?rectal\s*ref.*?\(mmhg\)\s*([\-\d\.]+)",
            data
        ),
        "Max Sphincter Pressure (Abs. ref) (mmHg)": extract_value(
            r"Max\.?\s*Sphincter\s*Pressure.*?abs\.?\s*ref.*?\(mmhg\)\s*([\-\d\.]+)",
            data
        ),
        "Mean Sphincter Pressure (Abs. ref) (mmHg)": extract_value(
            r"Mean\s*Sphincter\s*Pressure.*?abs\.?\s*ref.*?\(mmhg\)\s*([\-\d\.]+)",
            data
        ),
        "Length of HPZ (cm)": extract_value(
            r"Length\s*of\s*HPZ.*?\(cm\)\s*([\-\d\.]+)", data
        ),
        "Verge to Center Length (cm)": extract_value(
            r"Length\s*verge\s*to\s*center.*?\(cm\)\s*([\-\d\.]+)", data
        ),
        "Residual Anal Pressure (mmHg)": extract_value(
            r"Residual\s+Anal\s+Pressure.*?\(mmhg\)\s*([\-\d\.]+)", data
        ),
        "Anal Relaxation (%)": extract_value(
            r"Percent\s+anal\s+relaxation.*?\(%\)\s*([\-\d\.]+)",
            data
        ),
        "First Sensation (cc)": extract_value(
            r"First\s+sensation.*?\(cc\)\s*([\-\d\.]+)",
            data
        ),
        "Urge to Defecate (cc)": extract_value(
            r"Urge\s+to\s+defecate.*?\(cc\)\s*([\-\d\.]+)", data
        ),
        "Rectoanal Pressure Differential (mmHg)": extract_value(
            r"Rectoanal\s+pressure\s+differential.*?\(mmhg\)\s*([\-\d\.]+)", data
        ),
        "RAIR": "Present" if "RAIR" in data else "Not Present",

        # ✅ FIXED Indications (Now Detects "s/p perianal tear")
        "Indications": categorize_indications(
            extract_value(r"Indications\s*[:]?[\s]*(.+)", data)
        ),

        "Diagnoses": extract_value(
            r"Diagnoses\s*\(London classification\)\s*(.*)", data
        )
    }
    
    df = pd.DataFrame([extracted_data])
    st.write("## Final Extracted Data")
    st.dataframe(df)

    output_excel = BytesIO()
    df.to_excel(output_excel, index=False, sheet_name="Sheet1")
    output_excel.seek(0)

    st.download_button(
        label="Download Excel File",
        data=output_excel,
        file_name="Book2.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

