import pandas as pd
import streamlit as st
import io
import re
from collections import defaultdict

def extract_patient_data(uploaded_file):
    """
    Extracts structured key-value pairs from a text file and correctly maps them to their headers.
    """
    file_content = uploaded_file.read().decode("utf-8")
    lines = file_content.split("\n")

    # Define categories and expected numeric fields
    data = defaultdict(list)  # Using list to handle multiple values for same key
    current_key = None

    for i in range(len(lines)):
        line = lines[i].strip()

        if not line:
            continue

        # Detect category titles
        if ":" in line or "(" in line or "Procedure" in line or "Findings" in line:
            current_key = re.sub(r"[:\(\)]", "", line).strip()  # Remove colons and parentheses
        elif current_key:
            # Store the corresponding value under the last detected key
            number_match = re.match(r"^-?\d+(\.\d+)?$", line)  # Match numbers (including negative & decimals)
            if number_match:
                data[current_key].append(line)  # Store all values under the correct key
            else:
                # Handle multi-line fields like "Procedure Summary"
                if current_key in ["Procedure", "Findings", "Indications"]:
                    data[current_key].append(line)

    # Convert lists to strings (if multiple values exist, join them)
    formatted_data = {key: ", ".join(values) if values else None for key, values in data.items()}

    # Extract only the Patient ID (removing the name)
    if "Patient" in formatted_data:
        patient_info = formatted_data["Patient"].split() if formatted_data["Patient"] else []
        patient_id = next((item for item in patient_info if item.isdigit()), None)
        formatted_data["Patient"] = patient_id if patient_id else "Unknown"

    # Extract "Procedure Date" from the file
    for line in lines:
        if "/" in line and len(line.split("/")) == 3:  # Looking for DD/MM/YYYY format
            formatted_data["Procedure Date"] = line.strip()
            break

    # Convert to DataFrame
    df = pd.DataFrame([formatted_data])
    return df

# Streamlit Web App
st.title("📂 Convert TXT to Excel (Fully Fixed Version)")
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
        label="📥 Download Fixed Structured Excel File",
        data=output,
        file_name="Structured_Patient_Data_Fixed.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

       
   
          
       

   
    
        
        
     
    
  
