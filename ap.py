import pandas as pd
import re
import streamlit as st

st.title("Extract Data from Text File to Excel")

uploaded_file = st.file_uploader("Upload your text file", type=["txt"])
if uploaded_file:
    data = uploaded_file.read().decode("utf-8").splitlines()
    
    def extract_value(pattern, data, default="N/A"):
        for i, line in enumerate(data):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if value:
                    return value
        return default
    
    # Indication categories
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
        text_lower = text.lower()
        for key, value in indication_options.items():
            if key in text_lower:
                return value
        return "Other"
    
    # Extract required fields
    extracted_values = {
        "Patient Name": extract_value(r"Patient:\s*(.*)", data),
        "Patient ID": extract_value(r"Patient ID:\s*(\d{9})", data),
        "Gender": extract_value(r"Gender:\s*(.*)", data),
        "Date of Birth": extract_value(r"DOB:\s*(.*)", data),
        "Physician": extract_value(r"Physician:\s*(.*)", data),
        "Operator": extract_value(r"Operator:\s*(.*)", data),
        "Referring Physician": extract_value(r"Referring Physician:\s*(.*)", data),
        "Examination Date": extract_value(r"Examination Date:\s*(.*)", data),
        "Height": extract_value(r"Height:\s*(.*)", data),
        "Weight": extract_value(r"Weight:\s*(.*)", data),
        "Mean Sphincter Pressure (Rectal ref) (mmHg)": extract_value(r"Mean Sphincter Pressure.*?\(rectal ref.*?\)\s*(\d+\.?\d*)", data),
        "Max Sphincter Pressure (Rectal ref) (mmHg)": extract_value(r"Max\. Sphincter Pressure.*?\(rectal ref.*?\)\s*(\d+\.?\d*)", data),
        "Max Sphincter Pressure (Abs. ref) (mmHg)": extract_value(r"Max\. Sphincter Pressure.*?\(abs\. ref.*?\)\s*(\d+\.?\d*)", data),
        "Mean Sphincter Pressure (Abs. ref) (mmHg)": extract_value(r"Mean Sphincter Pressure.*?\(abs\. ref.*?\)\s*(\d+\.?\d*)", data),
        "Duration of Squeeze (sec)": extract_value(r"Duration of sustained squeeze.*?\s*(\d+\.?\d*)", data),
        "Length of HPZ (cm)": extract_value(r"Length of HPZ.*?\s*(\d+\.?\d*)", data),
        "Length verge to center (cm)": extract_value(r"Length verge to center.*?\s*(\d+\.?\d*)", data),
        "Residual Anal Pressure (mmHg)": extract_value(r"Residual Anal Pressure.*?\s*(\d+\.?\d*)", data),
        "Percent Anal Relaxation (%)": extract_value(r"Percent anal relaxation.*?\s*(\d+\.?\d*)", data),
        "First Sensation (cc)": extract_value(r"First sensation.*?\s*(\d+\.?\d*)", data),
        "Intrarectal Pressure (mmHg)": extract_value(r"Intrarectal pressure.*?\s*(\d+\.?\d*)", data),
        "Urge to Defecate (cc)": extract_value(r"Urge to defecate.*?\s*(\d+\.?\d*)", data),
        "Rectoanal Pressure Differential (mmHg)": extract_value(r"Rectoanal pressure differential.*?\s*(-?\d+\.?\d*)", data),
        "Discomfort (cc)": extract_value(r"Discomfort.*?\s*(\d+\.?\d*)", data),
        "Min Rectal Compliance": extract_value(r"Minimum rectal compliance.*?\s*(\d+\.?\d*)", data),
        "Max Rectal Compliance": extract_value(r"Maximum rectal compliance.*?\s*(\d+\.?\d*)", data),
        "RAIR": "Present" if "RAIR" in data else "Not Present",
        "Indications": categorize_indications(extract_value(r"Indications:\s*(.*)", data)),
        "Diagnoses": extract_value(r"Diagnoses \(London classification\):\s*(.*)", data)
    }
    
    # Display extracted data for debugging
    st.write("### Extracted Data (Debugging)")
    st.json(extracted_values)
    
    # Create a dataframe
    df = pd.DataFrame([extracted_values])
    
    # Display the dataframe in Streamlit
    st.write("### Final Extracted Data")
    st.dataframe(df)
    
    # Provide option to download Excel file
    output_excel_path = "Processed_Data.xlsx"
    df.to_excel(output_excel_path, index=False)
    with open(output_excel_path, "rb") as f:
        st.download_button("Download Excel File", f, file_name="Processed_Data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

