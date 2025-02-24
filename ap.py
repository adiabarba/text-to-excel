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
                return match.group(1).strip()
            if pattern in line.lower():  # Handle cases where value is on next line
                return data[i + 1].strip() if i + 1 < len(data) else default
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
        if text == "N/A":
            return "Other"
        text_lower = text.lower()
        for key, value in indication_options.items():
            if key in text_lower:
                return value
        return "Other"
    
    # Extract required fields
    extracted_values = {
        "Patient Name": extract_value(r"Patient:", data),
        "Patient ID": extract_value(r"\b\d{9}\b", data),
        "Gender": extract_value(r"Gender:", data),
        "Date of Birth": extract_value(r"DOB:", data),
        "Physician": extract_value(r"Physician:", data),
        "Operator": extract_value(r"Operator:", data),
        "Referring Physician": extract_value(r"Referring Physician:", data),
        "Examination Date": extract_value(r"Examination Date:", data),
        "Height": extract_value(r"Height:", data),
        "Weight": extract_value(r"Weight:", data),
        "Mean Sphincter Pressure (Rectal ref) (mmHg)": extract_value(r"Mean Sphincter Pressure\(rectal ref.*?\)", data),
        "Max Sphincter Pressure (Rectal ref) (mmHg)": extract_value(r"Max\. Sphincter Pressure\(rectal ref.*?\)", data),
        "Max Sphincter Pressure (Abs. ref) (mmHg)": extract_value(r"Max\. Sphincter Pressure\(abs\. ref.*?\)", data),
        "Mean Sphincter Pressure (Abs. ref) (mmHg)": extract_value(r"Mean Sphincter Pressure\(abs\. ref.*?\)", data),
        "Duration of Squeeze (sec)": extract_value(r"Duration of sustained squeeze", data),
        "Length of HPZ (cm)": extract_value(r"Length of HPZ", data),
        "Length verge to center (cm)": extract_value(r"Length verge to center", data),
        "Residual Anal Pressure (mmHg)": extract_value(r"Residual Anal Pressure", data),
        "Percent Anal Relaxation (%)": extract_value(r"Percent anal relaxation", data),
        "First Sensation (cc)": extract_value(r"First sensation", data),
        "Intrarectal Pressure (mmHg)": extract_value(r"Intrarectal pressure", data),
        "Urge to Defecate (cc)": extract_value(r"Urge to defecate", data),
        "Rectoanal Pressure Differential (mmHg)": extract_value(r"Rectoanal pressure differential", data),
        "Discomfort (cc)": extract_value(r"Discomfort", data),
        "Min Rectal Compliance": extract_value(r"Minimum rectal compliance", data),
        "Max Rectal Compliance": extract_value(r"Maximum rectal compliance", data),
        "RAIR": "Present" if "RAIR" in data else "Not Present",
        "Indications": categorize_indications(extract_value(r"Indications", data)),
        "Diagnoses": extract_value(r"Diagnoses \(London classification\):", data)
    }
    
    # Debugging: Display extracted values before writing to Excel
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
