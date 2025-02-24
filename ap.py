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
        "perianal tear": "Anal Tear",
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
        "Max Sphincter Pressure (Rectal ref) (mmHg)",
        "Max Sphincter Pressure (Abs. ref) (mmHg)",
        "Mean Sphincter Pressure (Abs. ref) (mmHg)",
        "Length of HPZ (cm)", "Verge to Center Length (cm)",
        "Residual Anal Pressure (mmHg)", "Anal Relaxation (%)", "First Sensation (cc)",
        "Urge to Defecate (cc)", "Rectoanal Pressure Differential (mmHg)",
        "RAIR", "Indications", "Diagnoses"
    ]
    
    # Extract data using regex
    extracted_data = {
        "Patient Name": extract_value(r"Patient\s*[:]?[\s]*(.*)", data),
        "Patient ID": extract_value(r"(?:Patient\s+ID|ID\s+Number)\s*[:]?[\s]*(\w+)", data),
        "Gender": extract_value(r"Gender\s*[:]?[\s]*(.*)", data),
        "Date of Birth": extract_value(r"(?:DOB|Date of Birth)\s*[:]?[\s]*(.*)", data),
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
            r"Urge\s+to\s+defecate.*?\(cc\)\s*([\-\d\.]+)",
            data
        ),
        "Rectoanal Pressure Differential (mmHg)": extract_value(
            r"Rectoanal\s+pressure\s+differential.*?\(mmhg\)\s*([\-\d\.]+)",
            data
        ),
        "RAIR": "Present" if "RAIR" in data else "Not Present",
        "Indications": categorize_indications(
            extract_value(r"Indications\s*[:]?[\s]*(.*)", data)
        ),
        "Diagnoses": extract_value(
            r"Diagnoses\s*\(London classification\)\s*(.*)",
            data
        )
    }
    
    # Convert extracted values to DataFrame
    df = pd.DataFrame([extracted_data], columns=column_names)
    
    # Show a debugging table of extracted values
    st.write("## Extracted Data (Debugging)")
    for key, val in extracted_data.items():
        st.write(f"**{key}:** {val}")
    
    # Show final DataFrame in Streamlit
    st.write("## Final Extracted Data")
    st.dataframe(df)
    
    # Prepare Excel output in memory
    output_excel = BytesIO()
    df.to_excel(output_excel, index=False, sheet_name="Sheet1")
    output_excel.seek(0)

    # Download button
    st.download_button(
        label="Download Excel File",
        data=output_excel,
        file_name="Book2.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

