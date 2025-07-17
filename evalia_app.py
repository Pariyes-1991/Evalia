import streamlit as st
import pandas as pd

st.set_page_config(page_title="Evalia", page_icon="💼", layout="wide")

st.markdown("""
    <h1 style='text-align: center; color: #007BFF;'>Evalia</h1>
    <p style='text-align: center;'>Applicant Analyzer with Extended Rule-Based Keywords for Healthcare Industry</p>
""", unsafe_allow_html=True)

st.divider()

upload_option = st.radio("Choose data input method:", ("Upload Excel File", "Provide Online Excel Link"))

df = None
if upload_option == "Upload Excel File":
    uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
elif upload_option == "Provide Online Excel Link":
    excel_link = st.text_input("🔗 Paste your Microsoft Excel Online Link:")
    if excel_link:
        try:
            df = pd.read_excel(excel_link)
        except Exception as e:
            st.error(f"Error fetching Excel: {e}")

if df is not None:
    st.success("Data loaded successfully!")
    st.dataframe(df)

    def calculate_bmi(row):
        try:
            bmi = row['น้ำหนัก'] / ((row['ส่วนสูง'] / 100) ** 2)
            return round(bmi, 2)
        except:
            return None

    def assign_info_level(bmi):
        if bmi is None:
            return "Unknown", "BMI data is missing"
        elif bmi > 25:
            return "Low", "BMI exceeds 25"
        else:
            return "High", "BMI within normal range"

    def assign_exp_level(exp_years, description):
        keywords_high = [
            "lead", "manager", "senior", "expert", "specialist", "consultant", "director", "chief", "head", "principal",
            "ผู้นำ", "ผู้จัดการ", "อาวุโส", "ผู้เชี่ยวชาญ", "ที่ปรึกษา", "ผู้อำนวยการ", "หัวหน้า", "เจ้าหน้าที่บริหาร",
            "doctor", "physician", "surgeon", "anesthetist", "radiologist", "pediatrician", "neurosurgeon", "cardiologist",
            "แพทย์", "หมอ", "ศัลยแพทย์", "วิสัญญีแพทย์", "รังสีแพทย์", "กุมารแพทย์", "ศัลยแพทย์สมอง", "อายุรแพทย์", "แพทย์ผู้เชี่ยวชาญ",
            "nurse practitioner", "head nurse", "chief nurse",
            "พยาบาลวิชาชีพ", "หัวหน้าพยาบาล", "ผู้บริหารพยาบาล"
        ]
        keywords_mid = [
            "assist", "support", "junior", "operator", "staff", "clerk", "coordinator", "trainee",
            "ผู้ช่วย", "สนับสนุน", "เจ้าหน้าที่", "พนักงาน", "ประสานงาน", "ฝึกงาน", "ปฏิบัติการ",
            "registered nurse", "practical nurse", "medical assistant", "pharmacy technician", "lab technician", "radiographer",
            "พยาบาล", "ผู้ช่วยพยาบาล", "เจ้าหน้าที่เทคนิคการแพทย์", "เภสัชกร", "ผู้ช่วยเภสัช", "เจ้าหน้าที่รังสีเทคนิค", "นักกายภาพบำบัด", "นักจิตวิทยา"
        ]

        desc_lower = str(description).lower()

        if exp_years >= 5:
            return "High", "Experience over 5 years"
        elif exp_years >= 2:
            return "Mid", "Experience between 2 and 5 years"
        else:
            for word in keywords_high:
                if word.lower() in desc_lower:
                    return "Mid", f"Keyword '{word}' found in description"
            for word in keywords_mid:
                if word.lower() in desc_lower:
                    return "Low", f"Keyword '{word}' found in description"
            return "Low", "No significant keywords found, less than 2 years experience"

    df['BMI'] = df.apply(calculate_bmi, axis=1)
    df[['Info Level', 'Info Reason']] = df['BMI'].apply(lambda bmi: pd.Series(assign_info_level(bmi)))
    df[['Exp Level', 'Exp Reason']] = df.apply(lambda row: pd.Series(assign_exp_level(row.get('ประสบการณ์ (ปี)', 0), row.get('รายละเอียดเพิ่มเติม', ''))), axis=1)

    st.subheader("🎯 Analyzed Applicants")
    for idx, row in df.iterrows():
        st.markdown(f"""
            <div style='border:1px solid #ccc; border-radius:10px; padding:10px; margin-bottom:10px;'>
                <h4 style='color:#007BFF;'>{row.get('ชื่อ', 'Unknown')}</h4>
                <ul>
                    <li>BMI: <b>{row['BMI']}</b></li>
                    <li>Info Level: <b>{row['Info Level']}</b> — {row['Info Reason']}</li>
                    <li>Experience Level: <b>{row['Exp Level']}</b> — {row['Exp Reason']}</li>
                </ul>
                <a href="mailto:?subject=Applicant: {row.get('ชื่อ', 'Unknown')}&body=Please review this applicant." target="_blank">
                    <button style='background:#007BFF; color:white; padding:5px 10px; border:none; border-radius:5px;'>📧 Send Email</button>
                </a>
                <a href="https://teams.microsoft.com/l/meeting/new" target="_blank">
                    <button style='background:#28a745; color:white; padding:5px 10px; border:none; border-radius:5px; margin-left:10px;'>📅 Schedule Interview</button>
                </a>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Please upload a file or paste an Excel Online link to begin.")
