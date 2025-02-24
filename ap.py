import pandas as pd
import re
import streamlit as st

st.title("Extract Data from Text File to Excel")

uploaded_file = st.file_uploader("Upload your text file", type=["txt"])
if uploaded_file:
    data = uploaded_file.read().decode("utf-8")
    lines = data.splitlines()
    
    def extract_value(pattern, text, default="N/A"):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else default
    
    # Define indication categories with improved keyword matching
    indication_options = {
        "constipation": "Constipation",
        "incontinence": "Incontinence",
        "hirschsprung": "s/p Hirschprung",
        "anorectal malformation": "Anorectal malformation",
        "anal tear": "Anal Tear",
        "perianal tear": "Anal Tear",
        "spina bifida": "Spina bifida"
    }
    
    def categorize_indications(text):
        text_lower = text.lower() if text != "N/A" else ""
        for key, value in indication_options.items():
            if key in text_lower:
                return value
        return "Other"
    
    # Define column names exactly as in Book2.xlsx
    column_names = [
        "Patient Name", "Patient ID", "Gender", "Date of Birth", "Physician", "Operator",
        "Referring Physician", "Examination Date", "Height", "Weight", "Mean Sphincter Pressure (Rectal ref) (mmHg)",
        "Max Sphincter Pressure (Rectal ref) (mmHg)", "Max Sphincter Pressure (Abs. ref) (mmHg)",
        "Mean Sphincter Pressure (Abs. ref) (mmHg)", "Length of HPZ (cm)", "Verge to Center Length (cm)",
        "Residual Anal Pressure (mmHg)", "Anal Relaxation (%)", "First Sensation (cc)", "Urge to Defecate (cc)",
        "Rectoanal Pressure Differential (mmHg)", "RAIR", "Indications", "Diagnoses"
    ]
    
    # Extract values
    extracted_data = {
        "Patient Name": extract_value(r"Patient[:\s]*(.*)", data),
        "Patient ID": extract_value(r"(?:Patient ID|ID Number)[:\s]*(\w+)", data),
        "Gender": extract_value(r"Gender[:\s]*(.*)", data),
        "Date of Birth": extract_value(r"(?:DOB|Date of Birth)[:\s]*(.*)", data),
        "Physician": extract_value(r"Physician[:\s]*(.*)", data),
        "Operator": extract_value(r"Operator[:\s]*(.*)", data),
        "Referring Physician": extract_value(r"Referring Physician[:\s]*(.*)", data),
        "Examination Date": extract_value(r"Examination Date[:\s]*(.*)", data),
        "Height": extract_value(r"Height[:\s]*(\d{1,3}\.?\d*)", data),
        "Weight": extract_value(r"Weight[:\s]*(\d{1,3}\.?\d*)", data),
        "Mean Sphincter Pressure (Rectal ref) (mmHg)": extract_value(r"Mean Sphincter Pressure.*?rectal ref.*?[:\s]*(\d+\.?\d*)", data),
        "Max Sphincter Pressure (Rectal ref) (mmHg)": extract_value(r"Max\. Sphincter Pressure.*?rectal ref.*?[:\s]*(\d+\.?\d*)", data),
        "Max Sphincter Pressure (Abs. ref) (mmHg)": extract_value(r"Max\. Sphincter Pressure.*?abs\. ref.*?[:\s]*(\d+\.?\d*)", data),
        "Mean Sphincter Pressure (Abs. ref) (mmHg)": extract_value(r"Mean Sphincter Pressure.*?abs\. ref.*?[:\s]*(\d+\.?\d*)", data),
        "Length of HPZ (cm)": extract_value(r"Length of HPZ[:\s]*(\d+\.?\d*)", data),
        "Verge to Center Length (cm)": extract_value(r"Verge to center[:\s]*(\d+\.?\d*)", data),
        "Residual Anal Pressure (mmHg)": extract_value(r"Residual anal pressure[:\s]*(\d+\.?\d*)", data),
        "Anal Relaxation (%)": extract_value(r"Anal relaxation[:\s]*(\d+\.?\d*)", data),
        "First Sensation (cc)": extract_value(r"First sensation[:\s]*(\d+\.?\d*)", data),
        "Urge to Defecate (cc)": extract_value(r"Urge to defecate[:\s]*(\d+\.?\d*)", data),
        "Rectoanal Pressure Differential (mmHg)": extract_value(r"Rectoanal pressure differential[:\s]*(\d+\.?\d*)", data),
        "RAIR": "Present" if "RAIR" in data else "Not Present",
        "Indications": categorize_indications(extract_value(r"Indications[:\s]*(.*)", data)),
        "Diagnoses": extract_value(r"Diagnoses \(London classification\)[:\s]*(.*)", data)
    }
    
    # Debugging: Print extracted values in Streamlit
    st.write("### Extracted Data (Debugging)")
    for key, value in extracted_data.items():
        st.write(f"✅ {key}: {value}")
    
    # Convert extracted values to DataFrame
    df = pd.DataFrame([extracted_data], columns=column_names)
    
    # Display extracted data in Streamlit
    st.write("### Final Extracted Data")
    st.dataframe(df)
    
    # Provide download option
    output_excel_path = "Processed_Data.xlsx"
    df.to_excel(output_excel_path, index=False)
    with open(output_excel_path, "rb") as f:
        st.download_button("Download Excel File", f, file_name="Processed_Data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
