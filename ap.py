import pandas as pd
import re
import streamlit as st

st.title("Extract Data from Text File to Excel")

uploaded_file = st.file_uploader("Upload your text file", type=["txt"])
if uploaded_file:
    data = uploaded_file.read().decode("utf-8").splitlines()
    
    def extract_value(pattern, data, default="N/A"):
        for i, line in enumerate(data):
            if re.search(pattern, line):
                # Check if the next line contains the value
                if i + 1 < len(data) and re.match(r'^[0-9.-]+$', data[i + 1].strip()):
                    return data[i + 1].strip()
                return line.split(pattern)[-1].strip()
        return default
    
    # Extract patient details
    patient_name = extract_value(r"Patient:", data)
    gender = extract_value(r"Gender:", data)
    dob = extract_value(r"DOB:", data)
    physician = extract_value(r"Physician:", data)
    exam_date = extract_value(r"Examination Date:", data)
    
    # Extract measurements
    mean_sphincter_pressure_rectal = extract_value(r"Mean Sphincter Pressure\(rectal ref.*\)", data)
    max_sphincter_pressure_rectal = extract_value(r"Max\. Sphincter Pressure\(rectal ref.*\)", data)
    max_sphincter_pressure_abs = extract_value(r"Max\. Sphincter Pressure\(abs\. ref.*\)", data)
    mean_sphincter_pressure_abs = extract_value(r"Mean Sphincter Pressure\(abs\. ref.*\)", data)
    duration_squeeze = extract_value(r"Duration of sustained squeeze.*", data)
    length_hpz = extract_value(r"Length of HPZ.*", data)
    length_verge_center = extract_value(r"Length verge to center.*", data)
    residual_anal_pressure = extract_value(r"Residual Anal Pressure.*", data)
    percent_anal_relaxation = extract_value(r"Percent anal relaxation.*", data)
    first_sensation = extract_value(r"First sensation.*", data)
    intrarectal_pressure = extract_value(r"Intrarectal pressure.*", data)
    urge_to_defecate = extract_value(r"Urge to defecate.*", data)
    rectoanal_pressure_diff = extract_value(r"Rectoanal pressure differential.*", data)
    discomfort = extract_value(r"Discomfort.*", data)
    min_rectal_compliance = extract_value(r"Minimum rectal compliance.*", data)
    max_rectal_compliance = extract_value(r"Maximum rectal compliance.*", data)
    
    # Debugging: Display extracted values
    extracted_values = {
        "Patient Name": patient_name,
        "Gender": gender,
        "Date of Birth": dob,
        "Physician": physician,
        "Examination Date": exam_date,
        "Mean Sphincter Pressure (Rectal ref) (mmHg)": mean_sphincter_pressure_rectal,
        "Max Sphincter Pressure (Rectal ref) (mmHg)": max_sphincter_pressure_rectal,
        "Max Sphincter Pressure (Abs. ref) (mmHg)": max_sphincter_pressure_abs,
        "Mean Sphincter Pressure (Abs. ref) (mmHg)": mean_sphincter_pressure_abs,
        "Duration of Squeeze (sec)": duration_squeeze,
        "Length of HPZ (cm)": length_hpz,
        "Length verge to center (cm)": length_verge_center,
        "Residual Anal Pressure (mmHg)": residual_anal_pressure,
        "Percent Anal Relaxation (%)": percent_anal_relaxation,
        "First Sensation (cc)": first_sensation,
        "Intrarectal Pressure (mmHg)": intrarectal_pressure,
        "Urge to Defecate (cc)": urge_to_defecate,
        "Rectoanal Pressure Differential (mmHg)": rectoanal_pressure_diff,
        "Discomfort (cc)": discomfort,
        "Min Rectal Compliance": min_rectal_compliance,
        "Max Rectal Compliance": max_rectal_compliance
    }
    
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

