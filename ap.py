import pandas as pd
import streamlit as st
import io
import re

def extract_patient_data(uploaded_file):
    """
    Extracts structured key-value pairs from a text file and maps them to the specified headers.
    """
    file_content = uploaded_file.read().decode("utf-8")
    lines = file_content.split("\n")

    # Define the exact titles to extract (from the spreadsheet)
    required_titles = {
        "Patient": None,
        "Gender": None,
        "DOB": None,
        "Procedure Date": None,
        "Physician": None,
        "Weight": None,
        "Height": None,
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
        "RAIR": None,  # Will be "Present" or "Not Present"
        "Percent Anal Relaxation (%)": None,
        "First Sensation (cc)": None,
        "Intrarectal Pressure (mmHg)": None,
        "Urge to Defecate (cc)": None,
        "Rectoanal Pressure Differential (mmHg)": None,
        "Discomfort (cc)": None,
        "Minimum Rectal Compliance": None,
        "Maximum Rectal Compliance": None,
        "Indications": None,  # Will be categorized
        "Findings": None  # Only "Diagnoses (London classification)"
    }

    current_key = None
    capture_findings = False  # Flag for capturing "Findings"

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

        # Extract key-value pairs, even when values are on the next line
        if ":" in line or "(" in line:
            key = re.sub(r"[:\(\)]", "", line).strip()  # Remove special characters
            if key in required_titles:
                current_key = key
                continue  # Move to next line to capture value

        if current_key:
            # Capture numeric values
            number_match = re.search(r"^-?\d+(\.\d+)?$", line)  # Match numbers (including decimals)
            if number_match:
                required_titles[current_key] = number_match.group(0)  # Store first number
            else:
                required_titles[current_key] = line  # Store text if it's not a number
            current_key = None  # Reset key to avoid overwriting

        # Extract RAIR as "Present" or "Not Present"
        if "RAIR" in line:
            if "present" in line.lower():
                required_titles["RAIR"] = "Present"
            elif "not present" in line.lower() or "absent" in line.lower():
                required_titles["RAIR"] = "Not Present"

        # Extract indications (categorizing them)
        for keyword, label in indication_options.items():
            if keyword.lower() in line.lower():
                required_titles["Indications"] = label

        # If no matching indication is found, set to "Other"
        if required_titles["Indications"] is None:
            required_titles["Indications"] = "Other"

        # Capture "Findings" under "Diagnoses (London classification)"
        if "Diagnoses (London classification)" in line:
            capture_findings = True  # Start capturing findings
            required_titles["Findings"] = ""  # Initialize findings
            continue

        if capture_findings:
            if "Additional findings" in line:  # Stop capturing
                capture_findings = False
                continue
            required_titles["Findings"] += line + " "  # Store findings

    # Extract only the Patient ID (removing the name)
    if "Patient" in required_titles and required_titles["Patient"]:
        patient_info = required_titles["Patient"].split()
        patient_id = next((item for item in patient_info if item.isdigit()), None)
        required_titles["Patient"] = patient_id if patient_id else "Unknown"

    # Extract "Procedure Date"
    for line in lines:
        if "/" in line and len(line.split("/")) == 3:  # Looking for DD/MM/YYYY format
            required_titles["Procedure Date"] = line.strip()
            break

    # Ensure missing values remain empty (not "None")
    for key in required_titles:
        if required_titles[key] is None:
            required_titles[key] = ""

    # Convert to DataFrame
    df = pd.DataFrame([required_titles])
    return df

# Streamlit Web App
st.title("📂 Convert TXT to Excel (Fully Fixed for Missing Values)")
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
        label="📥 Download Fully Fixed Excel File",
        data=output,
        file_name="Fully_Fixed_Patient_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

   
          
       

   
    
        
        
     
    
  
