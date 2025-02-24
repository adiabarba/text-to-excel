import pandas as pd
import re
import streamlit as st

st.title("Extract Data from Text File to Excel")

uploaded_file = st.file_uploader("Upload your text file", type=["txt"])
if uploaded_file:
    data = uploaded_file.read().decode("utf-8").splitlines()
    
    def extract_value(pattern, data, default="N/A"):
        for i, line in enumerate(data):
            if re.search(pattern, line, re.IGNORECASE):
                # Check if the next line contains the value
                if i + 1 < len(data) and re.match(r'^[0-9A-Za-z .-]+$', data[i + 1].strip()):
                    return data[i + 1].strip()
                return re.sub(pattern, '', line).strip()
        return default
    
    def categorize_indications(text):
        categories = {
            "constipation": "Constipation",
            "incontinence": "Incontinence",
            "hirschsprung": "s/p Hirschprung",
            "anorectal malformation": "Anorectal malformation",
            "anal tear": "Anal Tear"
        }
        for key, value in categories.items():
            if key in text.lower():
                return value
        return "Other"
    
    # Extract required fields based on Book2.xlsx headers
    required_fields = [
        "Patient Name", "Patient ID", "Gender", "Date of Birth", "Physician", "Operator", "Referring Physician", "Examination Date", "Date of Procedure",
        "Height", "Weight", "Mean Sphincter Pressure (Rectal ref) (mmHg)", "Max Sphincter Pressure (Rectal ref) (mmHg)", 
        "Max Sphincter Pressure (Abs. ref) (mmHg)", "Mean Sphincter Pressure (Abs. ref) (mmHg)", "Duration of Squeeze (sec)", 
        "Length of HPZ (cm)", "Length verge to center (cm)", "Residual Anal Pressure (mmHg)", "Percent Anal Relaxation (%)", 
        "First Sensation (cc)", "Intrarectal Pressure (mmHg)", "Urge to Defecate (cc)", "Rectoanal Pressure Differential (mmHg)", 
        "Discomfort (cc)", "Min Rectal Compliance", "Max Rectal Compliance", "RAIR", "Indications", "Diagnoses"
    ]
    
    # Extract measurements
    extracted_values = {
        "Patient Name": extract_value(r"Patient:", data),
        "Patient ID": extract_value(r"\d{9}", data),
        "Gender": extract_value(r"Gender:", data),
        "Date of Birth": extract_value(r"DOB:", data),
        "Physician": extract_value(r"Physician:", data),
        "Operator": extract_value(r"Operator:", data),
        "Referring Physician": extract_value(r"Referring Physician:", data),
        "Examination Date": extract_value(r"Examination Date:", data),
        "Date of Procedure": extract_value(r"Examination Date:", data),
        "Height": extract_value(r"Height:", data),
        "Weight": extract_value(r"Weight:", data),
        "Mean Sphincter Pressure (Rectal ref) (mmHg)": extract_value(r"Mean Sphincter Pressure\(rectal ref.*\)", data),
        "Max Sphincter Pressure (Rectal ref) (mmHg)": extract_value(r"Max\. Sphincter Pressure\(rectal ref.*\)", data),
        "Max Sphincter Pressure (Abs. ref) (mmHg)": extract_value(r"Max\. Sphincter Pressure\(abs\. ref.*\)", data),
        "Mean Sphincter Pressure (Abs. ref) (mmHg)": extract_value(r"Mean Sphincter Pressure\(abs\. ref.*\)", data),
        "Duration of Squeeze (sec)": extract_value(r"Duration of sustained squeeze.*", data),
        "Length of HPZ (cm)": extract_value(r"Length of HPZ.*", data),
        "Length verge to center (cm)": extract_value(r"Length verge to center.*", data),
        "Residual Anal Pressure (mmHg)": extract_value(r"Residual Anal Pressure.*", data),
        "Percent Anal Relaxation (%)": extract_value(r"Percent anal relaxation.*", data),
        "First Sensation (cc)": extract_value(r"First sensation.*", data),
        "Intrarectal Pressure (mmHg)": extract_value(r"Intrarectal pressure.*", data),
        "Urge to Defecate (cc)": extract_value(r"Urge to defecate.*", data),
        "Rectoanal Pressure Differential (mmHg)": extract_value(r"Rectoanal pressure differential.*", data),
        "Discomfort (cc)": extract_value(r"Discomfort.*", data),
        "Min Rectal Compliance": extract_value(r"Minimum rectal compliance.*", data),
        "Max Rectal Compliance": extract_value(r"Maximum rectal compliance.*", data),
        "RAIR": "Present" if "RAIR" in data else "Not Present",
        "Indications": categorize_indications(extract_value(r"Indications", data)),
        "Diagnoses": extract_value(r"Diagnoses \(London classification\).*", data)
    }
     # Indication categories
    indication_options = {
        "Constipation": "Constipation",
        "Incontinence": "Incontinence",
        "Hirschsprung": "s/p Hirschprung",
        "Anorectal malformation": "Anorectal malformation",
        "Perianal tear": "Perianal tear",
        "Spina bifida": "Spina bifida"
    }

    for i in range(len(lines)):
        line = lines[i].strip()

        if not line:
            continue

        # Extract specific key-value pairs
        if ":" in line:
            key = line.replace(":", "").strip()
            if key in required_titles:
                current_key = key
                continue  # Move to next line to capture value

        elif current_key:
            # Extract the first numeric value for each title
            number_match = re.search(r"^-?\d+(\.\d+)?$", line)  # Match numbers (including decimals)
            if number_match:
                required_titles[current_key] = number_match.group(0)  # Store only the first value
            else:
                required_titles[current_key] = line  # Store text if it's not a number

            current_key = None  # Reset key to avoid overwriting
    # Keep only required fields
    extracted_values = {k: extracted_values[k] for k in required_fields if k in extracted_values}
    
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
