import pandas as pd
import streamlit as st
import io
import re

def extract_patient_data(uploaded_file):
    """
    Extracts structured key-value pairs from a text file and organizes them into categories.
    """
    file_content = uploaded_file.read().decode("utf-8")
    lines = file_content.split("\n")

    # Define categories and expected numeric fields
    data = {
        "Patient": None,
        "Procedure Date": None,
        "Resting": None,
        "Squeeze": None,
        "Mean Sphincter Pressure (rectal ref.) (mmHg)": None,
        "Max Sphincter Pressure (rectal ref.) (mmHg)": None,
        "Max Sphincter Pressure (abs. ref.) (mmHg)": None,
        "Mean Sphincter Pressure (abs. ref.) (mmHg)": None,
        "Duration of sustained squeeze (sec)": None,
        "Length of HPZ (cm)": None,
        "Length verge to center (cm)": None,
        "Push (attempted defecation)": None,
        "Balloon Inflation": None,
        "Residual Anal Pressure (abs. ref.) (mmHg)": None,
        "RAIR": None,
        "Percent Anal Relaxation (%)": None,
        "First Sensation (cc)": None,
        "Intrarectal Pressure (mmHg)": None,
        "Urge to Defecate (cc)": None,
        "Rectoanal Pressure Differential (mmHg)": None,
        "Discomfort (cc)": None,
        "Minimum Rectal Compliance": None,
        "Maximum Rectal Compliance": None,
        "Procedure Summary": None,
        "Indications": None,
        "Findings": None
    }

    current_key = None
    current_value = ""

    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        # Detect numbers and match them with categories
        number_match = re.search(r"([\d]+\.\d+|\d+)", line)
        if number_match:
            extracted_number = number_match.group(1)
        
        if ":" in line:  # Detecting keys
            if current_key and current_value:
                data[current_key] = current_value.strip()
            current_key = line.replace(":", "").strip()
            current_value = ""
        elif current_key:
            current_value += " " + line
            if number_match and current_key in data:  # Assign detected numbers
                data[current_key] = extracted_number

    # Store the last key-value pair
    if current_key and current_value:
        data[current_key] = current_value.strip()

    # Extract only the Patient ID (removing the name)
    if "Patient" in data:
        patient_info = data["Patient"].split() if data["Patient"] else []
        patient_id = next((item for item in patient_info if item.isdigit()), None)
        data["Patient"] = patient_id if patient_id else "Unknown"

    # Extract "Procedure Date" from the file
    if "Procedure" in data and data["Procedure"]:
        date_parts = [part for part in data["Procedure"].split() if "/" in part]
        if date_parts:
            data["Procedure Date"] = date_parts[0]

    # Convert to DataFrame
    df = pd.DataFrame([data])
    return df

# Streamlit Web App
st.title("📂 Convert TXT to Excel (Structured with Numbers)")
st.write("Upload your structured text file, and it will be automatically converted into an Excel file with all values correctly assigned.")

uploaded_file = st.file_uploader("Choose a text file", type=["txt"])

if uploaded_file is not None:
    st.success("✅ File uploaded successfully!")
    
    # Call the function with the correct file format
    df = extract_patient_data(uploaded_file)
    
    # Save to Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    
    # Provide a download button
    st.download_button(
        label="📥 Download Structured Excel File with Values",
        data=output,
        file_name="Structured_Patient_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

        
               
            
    
  
      
