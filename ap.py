import pandas as pd
import streamlit as st
import io
import re

def extract_patient_data(uploaded_file):
    """
    Extracts structured key-value pairs from a text file and maps them only to the specified headers.
    """
    file_content = uploaded_file.read().decode("utf-8")
    lines = file_content.split("\n")

    # Define the exact titles to extract
    required_titles = {
        "Patient": None,
        "Gender": None,
        "DOB": None,
        "Procedure date": None,
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
        "RAIR": None,
        "Percent Anal Relaxation (%)": None,
        "First Sensation (cc)": None,
        "Intrarectal Pressure (mmHg)": None,
        "Urge to Defecate (cc)": None,
        "Rectoanal Pressure Differential (mmHg)": None,
        "Discomfort (cc)": None,
        "Minimum Rectal Compliance": None,
        "Maximum Rectal Compliance": None,
        "Indications": None,
        "Findings": None,
        "Balloon expulsion test": None
    }

    current_key = None
    capture_findings = False  

    # Define multiple Indications to check
    indication_options = {
        "Constipation": "Constipation",
        "Incontinence": "Incontinence",
        "Hirschsprung": "s/p Hirschprung",
        "Anorectal malformation": "Anorectal malformation",
        "Perianal tear": "Perianal tear",
        "Spina bifida": "Spina bifida"
    }

    indications_found = []
    rair_found = False  # Track RAIR status

    for i in range(len(lines)):
        line = lines[i].strip()

        if not line:
            continue

        # Extract Patient ID (only numbers)
        if "Patient:" in line:
            patient_info = re.findall(r"\d+", lines[i + 1])
            required_titles["Patient"] = patient_info[0] if patient_info else ""

        # Extract Physician (skip "Referring Physician" and "Operator")
        if "Physician:" in line:
            required_titles["Physician"] = lines[i + 1].strip()
        if "Operator:" in line:
            required_titles["Physician"] = lines[i + 1].strip()  

        # Extract Procedure Date
        if "Examination Date:" in line or "Procedure Date:" in line:
            required_titles["Procedure date"] = lines[i + 1].strip()

        # Extract Gender
        if "Gender:" in line:
            required_titles["Gender"] = lines[i + 1].strip()

        # Extract DOB
        if "DOB:" in line:
            required_titles["DOB"] = lines[i + 1].strip()

        # Extract Indications (matching multiple options)
        for keyword, label in indication_options.items():
            if keyword.lower() in line.lower():
                indications_found.append(label)

        # Extract Findings (Diagnoses)
        if "Diagnoses (London classification)" in line:
            capture_findings = True
            required_titles["Findings"] = ""
            continue

        if capture_findings:
            if "Additional findings" in line:  
                capture_findings = False
                continue
            required_titles["Findings"] += line + " "

        # Extract numerical values for measurements
        for key in required_titles.keys():
            if key in line:
                current_key = key
                continue

        if current_key and re.match(r"^-?\d+(\.\d+)?$", line):
            required_titles[current_key] = line.strip()
            current_key = None  

        # Extract RAIR status properly
        if "RAIR" in line:
            if "present" in line.lower():
                required_titles["RAIR"] = "Present"
                rair_found = True
            elif "not present" in line.lower() or "absent" in line.lower():
                required_titles["RAIR"] = "Not Present"
                rair_found = True

        # Extract Balloon Expulsion Test
        if "Balloon expulsion test" in line.lower():
            required_titles["Balloon expulsion test"] = line.split(":")[1].strip()

    # Store Indications (combine multiple found options or use "Other" if none found)
    required_titles["Indications"] = ", ".join(indications_found) if indications_found else "Other"

    # Ensure RAIR is marked "Not Present" if no mention was found
    if not rair_found:
        required_titles["RAIR"] = "Not Present"

    # Convert None values to empty strings
    for key in required_titles:
        if required_titles[key] is None:
            required_titles[key] = ""

    # Convert to DataFrame
    df = pd.DataFrame([required_titles])
    return df

# Streamlit Web App
st.title("📂 Convert TXT to Excel (Final Version with All Data)")
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
        label="📥 Download Final Excel File with All Data",
        data=output,
        file_name="Final_Patient_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
