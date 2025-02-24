import pandas as pd
import re
import streamlit as st

st.title("Extract Data from Text File to Excel")

uploaded_file = st.file_uploader("Upload your text file", type=["txt"])
if uploaded_file:
    data = uploaded_file.read().decode("utf-8")
    
    def extract_value(pattern, text, default="N/A"):
        # DOTALL allows '.' to match across line breaks
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
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
        "Referring Physician", "Examination Date", "Height", "Weight",
        "Mean Sphincter Pressure (Rectal ref) (mmHg)",
        "Max Sphincter Pressure (Rectal ref) (mmHg)",
        "Max Sphincter Pressure (Abs. ref) (mmHg)",
        "Mean Sphincter Pressure (Abs. ref) (mmHg)",
        "Length of HPZ (cm)", "Verge to Center Length (cm)",
        "Residual Anal Pressure (mmHg)", "Anal Relaxation (%)", "First Sensation (cc)",
        "Urge to Defecate (cc)", "Rectoanal Pressure Differential (mmHg)",
        "RAIR", "Indications", "Diagnoses"
    ]
    
    # Extract values
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
        
        # Matches lines like "Mean Sphincter Pressure(rectal ref.)(mmHg)\n116.2"
        "Mean Sphincter Pressure (Rectal ref) (mmHg)": extract_value(
            r"Mean\s*Sphincter\s*Pressure.*?rectal\s*ref.*?\(mmhg\)\s*([\-\d\.]+)",
            data
        ),

        # Matches lines like "Max. Sphincter Pressure(rectal ref.)(mmHg)\n157.4"
        "Max Sphincter Pressure (Rectal ref) (mmHg)": extract_value(
            r"Max\.?\s*Sphincter\s*Pressure.*?rectal\s*ref.*?\(mmhg\)\s*([\-\d\.]+)",
            data
        ),

        # Matches lines like "Max. Sphincter Pressure(abs. ref.)(mmHg)\n209.4"
        "Max Sphincter Pressure (Abs. ref) (mmHg)": extract_value(
            r"Max\.?\s*Sphincter\s*Pressure.*?abs\.?\s*ref.*?\(mmhg\)\s*([\-\d\.]+)",
            data
        ),
        
        # Matches lines like "Mean Sphincter Pressure(abs. ref.)(mmHg)\n139.3"
        "Mean Sphincter Pressure (Abs. ref) (mmHg)": extract_value(
            r"Mean\s*Sphincter\s*Pressure.*?abs\.?\s*ref.*?\(mmhg\)\s*([\-\d\.]+)",
            data
        ),

        # Matches "Length of HPZ(cm)\n1.5"
        "Length of HPZ (cm)": extract_value(
            r"Length\s*of\s*HPZ.*?\(cm\)\s*([\-\d\.]+)", data
        ),
        
        # Matches "Length verge to center(cm)\n0.7"
        "Verge to Center Length (cm)": extract_value(
            r"Length\s*verge\s*to\s*center.*?\(cm\)\s*([\-\d\.]+)", data
        ),

        # Matches "Residual Anal Pressure(abs. ref.)(mmHg)\n110.7"
        "Residual Anal Pressure (mmHg)": extract_value(
            r"Residual\s+Anal\s+Pressure.*?\(mmhg\)\s*([\-\d\.]+)",
            data
        ),
        
        # Matches "Percent anal relaxation(%)\n15"
        "Anal Relaxation (%)": extract_value(
            r"Percent\s+anal\s+relaxation.*?\(%\)\s*([\-\d\.]+)",
            data
        ),

        # Matches "First sensation(cc)\n30"
        "First Sensation (cc)": extract_value(
            r"First\s+sensation.*?\(cc\)\s*([\-\d\.]+)", 
            data
        ),

        # Matches "Urge to defecate(cc)\n40"
        "Urge to Defecate (cc)": extract_value(
            r"Urge\s+to\s+defecate.*?\(cc\)\s*([\-\d\.]+)",
            data
        ),

        # Matches "Rectoanal pressure differential(mmHg)\n-43.8"
        "Rectoanal Pressure Differential (mmHg)": extract_value(
            r"Rectoanal\s+pressure\s+differential.*?\(mmhg\)\s*([\-\d\.]+)",
            data
        ),

        # RAIR: "Present" if the keyword is anywhere in the text
        "RAIR": "Present" if "RAIR" in data else "Not Present",

        # Matches "Indications\nS/p perineal tear"
        "Indications": categorize_indications(
            extract_value(r"Indications\s*[:]?[\s]*(.*)", data)
        ),

        # Matches "Diagnoses (London classification)\nAnal hypertension"
        "Diagnoses": extract_value(
            r"Diagnoses\s*\(London classification\)\s*(.*)", 
            data
        )
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
        st.download_button(
            "Download Excel File",
            f,
            file_name="Processed_Data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
