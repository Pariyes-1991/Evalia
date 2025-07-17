import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Evalia", page_icon="💼", layout="wide")

st.markdown("""
    <h1 style='text-align: center; color: #007BFF;'>Evalia</h1>
    <p style='text-align: center;'>Applicant Analyzer with Extended Rule-Based Keywords for Healthcare Industry</p>
""", unsafe_allow_html=True)

st.divider()

# การเลือกวิธีการนำเข้าข้อมูล
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
            response = requests.get(excel_link, stream=True)
            response.raise_for_status()
            df = pd.read_excel(io.BytesIO(response.content))
        except Exception as e:
            st.error(f"Error fetching Excel: {e}. Please ensure the link is publicly accessible or upload the file directly.")

if df is not None:
    st.success("Data loaded successfully!")
    st.dataframe(df)

    # ฟังก์ชันคำนวณ BMI
    def calculate_bmi(row):
        try:
            weight = row['Weight_kg']
            height = row['Height_cm']
            if pd.isna(weight) or pd.isna(height) or height == 0:
                return None
            bmi = weight / ((height / 100) ** 2)
            return round(bmi, 2)
        except:
            return None

    # ฟังก์ชันกำหนดระดับ BMI
    def assign_info_level(bmi):
        if bmi is None:
            return "Unknown", "BMI data is missing"
        elif bmi > 25:
            return "Low", "BMI exceeds 25"
        else:
            return "High", "BMI within normal range"

    # ฟังก์ชันกำหนดระดับประสบการณ์
    def assign_exp_level(exp_years, description):
        try:
            exp_str = str(exp_years).strip()
            if exp_str == "มากกว่า 10ปี":
                years = 10
            elif exp_str == "7-10 ปี":
                years = 7
            elif exp_str == "4-6 ปี":
                years = 4
            elif exp_str == "1-3 ปี":
                years = 1
            else:
                years = 0

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

            if years >= 5:
                return "High", "Experience over 5 years"
            elif years >= 2:
                return "Mid", "Experience between 2 and 5 years"
            else:
                for word in keywords_high:
                    if word.lower() in desc_lower:
                        return "Mid", f"Keyword '{word}' found in description"
                for word in keywords_mid:
                    if word.lower() in desc_lower:
                        return "Low", f"Keyword '{word}' found in description"
                return "Low", "No significant keywords found, less than 2 years experience"
        except Exception as e:
            return "Unknown", f"Error processing experience: {e}"

    # คำนวณ BMI และระดับประสบการณ์
    df['BMI'] = df.apply(calculate_bmi, axis=1)
    df[['Info Level', 'Info Reason']] = df['BMI'].apply(lambda bmi: pd.Series(assign_info_level(bmi)))
    df[['Exp Level', 'Exp Reason']] = df.apply(
        lambda row: pd.Series(assign_exp_level(
            row.get('Experience_Years', 0),
            row.get('ช่วยเล่าประสบการณ์การทำงานของท่านโดยละเอียด', '')
        )), axis=1
    )

    # ส่วนการกรองข้อมูล
    st.subheader("🔍 Filter Applicants")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        position_options = ['All'] + list(df['ตำแหน่งงานที่ท่านสนใจ'].unique())
        selected_position = st.selectbox("Position", position_options)
    with col2:
        exp_options = ['All', 'มากกว่า 10ปี', '7-10 ปี', '4-6 ปี', '1-3 ปี']
        selected_exp = st.selectbox("Experience", exp_options)
    with col3:
        toeic_min = st.number_input("Minimum TOEIC Score", min_value=0, max_value=990, value=0)
    with col4:
        bmi_max = st.number_input("Maximum BMI", min_value=0.0, value=25.0)

    # กรองข้อมูล
    filtered_df = df.copy()
    if selected_position != 'All':
        filtered_df = filtered_df[filtered_df['ตำแหน่งงานที่ท่านสนใจ'] == selected_position]
    if selected_exp != 'All':
        filtered_df = filtered_df[filtered_df['Experience_Years'] == selected_exp]
    if toeic_min > 0:
        filtered_df = filtered_df[filtered_df['TOEIC Score (ถ้ามี)'].fillna(0) >= toeic_min]
    if bmi_max > 0:
        filtered_df = filtered_df[filtered_df['BMI'].fillna(100) <= bmi_max]

    st.write(f"Found {len(filtered_df)} applicants after filtering")
    st.dataframe(filtered_df)

    # แสดงผลผู้สมัครที่กรองแล้ว
    st.subheader("🎯 Analyzed Applicants")
    for idx, row in filtered_df.iterrows():
        st.markdown(f"""
            <div style='border:1px solid #ccc; border-radius:10px; padding:10px; margin-bottom:10px;'>
                <h4 style='color:#007BFF;'>{row.get('ชื่อ (Name)', 'Unknown')} {row.get('ชื่อสกุล (Surname)', '')}</h4>
                <ul>
                    <li>BMI: <b>{row['BMI'] if pd.notna(row['BMI']) else 'N/A'}</b></li>
                    <li>Info Level: <b>{row['Info Level']}</b> — {row['Info Reason']}</li>
                    <li>Experience Level: <b>{row['Exp Level']}</b> — {row['Exp Reason']}</li>
                    <li>Position: <b>{row.get('ตำแหน่งงานที่ท่านสนใจ', 'N/A')}</b></li>
                    <li>Department: <b>{row.get('กลุ่มแผนกที่ท่านสนใจ', 'N/A')}</b></li>
                    <li>TOEIC Score: <b>{row.get('TOEIC Score (ถ้ามี)', 'N/A')}</b></li>
                </ul>
                <a href="mailto:?subject=Applicant: {row.get('ชื่อ (Name)', 'Unknown')} {row.get('ชื่อสกุล (Surname)', '')}&body=Please review this applicant." target="_blank">
                    <button style='background:#007BFF; color:white; padding:5px 10px; border:none; border-radius:5px;'>📧 Send Email</button>
                </a>
                <a href="https://teams.microsoft.com/l/meeting/new" target="_blank">
                    <button style='background:#28a745; color:white; padding:5px 10px; border:none; border-radius:5px; margin-left:10px;'>📅 Schedule Interview</button>
                </a>
            </div>
        """, unsafe_allow_html=True)

    # กราฟ
    st.subheader("📊 Data Visualizations")

    # กราฟ 1: จำนวนผู้สมัครตามตำแหน่งงาน
    position_counts = filtered_df['ตำแหน่งงานที่ท่านสนใจ'].value_counts().reset_index()
    position_counts.columns = ['Position', 'Count']
    fig1 = px.bar(position_counts, x='Position', y='Count', title="Number of Applicants by Position",
                  color='Position', color_discrete_sequence=px.colors.qualitative.Plotly)
    st.plotly_chart(fig1, use_container_width=True)

    # กราฟ 2: การกระจายของประสบการณ์
    exp_counts = filtered_df['Experience_Years'].value_counts().reset_index()
    exp_counts.columns = ['Experience', 'Count']
    fig2 = px.pie(exp_counts, names='Experience', values='Count', title="Experience Distribution",
                  color_discrete_sequence=px.colors.qualitative.Pastel1)
    st.plotly_chart(fig2, use_container_width=True)

    # กราฟ 3: การกระจายของ BMI Level
    bmi_counts = filtered_df['Info Level'].value_counts().reset_index()
    bmi_counts.columns = ['BMI Level', 'Count']
    fig3 = px.bar(bmi_counts, x='BMI Level', y='Count', title="BMI Level Distribution",
                  color='BMI Level', color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.info("Please upload a file or paste an Excel Online link to begin.")
