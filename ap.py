import pandas as pd
import re
import streamlit as st

st.title("Extract Data from Text File to Excel")

uploaded_file = st.file_uploader("Upload your text file", type=["txt"])
if uploaded_file:
    data = uploaded_file.read().decode("utf-8").splitlines()
    
    def extract_value(pattern, data, default="N/A"):
        for line in data:
            match = re.search(pattern, line)
            if match:
                return match.group(1).strip()
        return default
    
    # Extract patient details
    patient_name = extract_value(r"Patient:\s*(.*)", data)
    gender = extract_value(r"Gender:\s*(.*)", data)
    dob = extract_value(r"DOB:\s*(.*)", data)
    physician = extract_value(r"Physician:\s*(.*)", data)
    exam_date = extract_value(r"Examination Date:\s*(.*)", data)
    
    # Extract measurements
    mean_sphincter_pressure_rectal = extract_value(r"Mean Sphincter Pressure\(rectal ref.\)\(mmHg\)\s*(\d+\.\d+)", data)
    max_sphincter_pressure_rectal = extract_value(r"Max. Sphincter Pressure\(rectal ref.\)\(mmHg\)\s*(\d+\.\d+)", data)
    max_sphincter_pressure_abs = extract_value(r"Max. Sphincter Pressure\(abs. ref.\)\(mmHg\)\s*(\d+\.\d+)", data)
    mean_sphincter_pressure_abs = extract_value(r"Mean Sphincter Pressure\(abs. ref.\)\(mmHg\)\s*(\d+\.\d+)", data)
    duration_squeeze = extract_value(r"Duration of sustained squeeze\(sec\)\s*(\d+\.\d+)", data)
    length_hpz = extract_value(r"Length of HPZ\(cm\)\s*(\d+\.\d+)", data)
    length_verge_center = extract_value(r"Length verge to center\(cm\)\s*(\d+\.\d+)", data)
    residual_anal_pressure = extract_value(r"Residual Anal Pressure\(abs. ref.\)\(mmHg\)\s*(\d+\.\d+)", data)
    percent_anal_relaxation = extract_value(r"Percent anal relaxation\(%\)\s*(\d+)", data)
    first_sensation = extract_value(r"First sensation\(cc\)\s*(\d+)", data)
    intrarectal_pressure = extract_value(r"Intrarectal pressure\(mmHg\)\s*(\d+\.\d+)", data)
    urge_to_defecate = extract_value(r"Urge to defecate\(cc\)\s*(\d+)", data)
    rectoanal_pressure_diff = extract_value(r"Rectoanal pressure differential\(mmHg\)\s*(-?\d+\.\d+)", data)
    discomfort = extract_value(r"Discomfort\(cc\)\s*(\d+)", data)
    min_rectal_compliance = extract_value(r"Minimum rectal compliance\s*(\d+\.\d+)", data)
    max_rectal_compliance = extract_value(r"Maximum rectal compliance\s*(\d+\.\d+)", data)
    
    # Create a dataframe with extracted data
    df = pd.DataFrame({
        "Patient Name": [patient_name],
        "Gender": [gender],
        "Date of Birth": [dob],
        "Physician": [physician],
        "Examination Date": [exam_date],
        "Mean Sphincter Pressure (Rectal ref) (mmHg)": [mean_sphincter_pressure_rectal],
        "Max Sphincter Pressure (Rectal ref) (mmHg)": [max_sphincter_pressure_rectal],
        "Max Sphincter Pressure (Abs. ref) (mmHg)": [max_sphincter_pressure_abs],
        "Mean Sphincter Pressure (Abs. ref) (mmHg)": [mean_sphincter_pressure_abs],
        "Duration of Squeeze (sec)": [duration_squeeze],
        "Length of HPZ (cm)": [length_hpz],
        "Length verge to center (cm)": [length_verge_center],
        "Residual Anal Pressure (mmHg)": [residual_anal_pressure],
        "Percent Anal Relaxation (%)": [percent_anal_relaxation],
        "First Sensation (cc)": [first_sensation],
        "Intrarectal Pressure (mmHg)": [intrarectal_pressure],
        "Urge to Defecate (cc)": [urge_to_defecate],
        "Rectoanal Pressure Differential (mmHg)": [rectoanal_pressure_diff],
        "Discomfort (cc)": [discomfort],
        "Min Rectal Compliance": [min_rectal_compliance],
        "Max Rectal Compliance": [max_rectal_compliance]
    })
    
    # Display the dataframe in Streamlit
    st.write("### Extracted Data")
    st.dataframe(df)
    
    # Provide option to download Excel file
    output_excel_path = "Processed_Data.xlsx"
    df.to_excel(output_excel_path, index=False)
    with open(output_excel_path, "rb") as f:
        st.download_button("Download Excel File", f, file_name="Processed_Data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


