import streamlit as st
import pandas as pd
import requests
import io

# กำหนดการตั้งค่าแอป
st.set_page_config(
    page_title="Evalute + AI",
    page_icon=":rocket:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# สไตล์ CSS ทันสมัยแบบ Grok
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stHeader {
        background-color: #0a0a1a;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    .stButton>button {
        background-color: #00aaff;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0088cc;
        transform: scale(1.05);
    }
    .card {
        background: #2a2a3e;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    h1, h2, h3, h4 {
        color: #00d4ff;
        font-weight: 600;
    }
    ul {
        list-style-type: none;
        padding-left: 0;
    }
    ul li {
        margin: 5px 0;
    }
    a {
        text-decoration: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# หัวข้อและคำอธิบาย
st.markdown('<div class="stHeader"><h1>Evalute + AI</h1><p>Applicant Analyzer with Extended Rule-Based Keywords</p></div>', unsafe_allow_html=True)
st.divider()

# การเลือกวิธีการนำเข้าข้อมูล
upload_option = st.radio("Choose data input method:", ("Upload Excel File", "Provide Online Excel Link"), horizontal=True)

df = None
if upload_option == "Upload Excel File":
    uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")
elif upload_option == "Provide Online Excel Link":
    excel_link = st.text_input("🔗 Paste your Microsoft Excel Online Link:")
    if excel_link:
        try:
            response = requests.get(excel_link, stream=True, timeout=10)
            response.raise_for_status()
            df = pd.read_excel(io.BytesIO(response.content))
        except Exception as e:
            st.error(f"Error fetching Excel from link: {e}. The SharePoint link may require authentication. Please upload the file directly or ensure the link is publicly accessible.")

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
        except Exception as e:
            st.warning(f"Error calculating BMI for a row: {e}")
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
        position_options = ['All'] + list(df['ตำแหน่งงานที่ท่านสนใจ'].dropna().unique())
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
        experience = row.get('ช่วยเล่าประสบการณ์การทำงานของท่านโดยละเอียด', 'N/A')
        st.markdown(f"""
            <div class="card">
                <h4 style='color:#00d4ff;'>{row.get('ชื่อ (Name)', 'Unknown')} {row.get('ชื่อสกุล (Surname)', '')}</h4>
                <ul>
                    <li><b>BMI:</b> {row['BMI'] if pd.notna(row['BMI']) else 'N/A'}</li>
                    <li><b>Info Level:</b> {row['Info Level']} — {row['Info Reason']}</li>
                    <li><b>Experience Level:</b> {row['Exp Level']} — {row['Exp Reason']}</li>
                    <li><b>Position:</b> {row.get('ตำแหน่งงานที่ท่านสนใจ', 'N/A')}</li>
                    <li><b>Department:</b> {row.get('กลุ่มแผนกที่ท่านสนใจ', 'N/A')}</li>
                    <li><b>TOEIC Score:</b> {row.get('TOEIC Score (ถ้ามี)', 'N/A')}</li>
                    <li><b>Experience Details:</b> {experience}</li>
                </ul>
                <a href="mailto:?subject=แจ้งนัดสัมภาษณ์งานกับ BDMS&body=เรียนคุณ {row.get('ชื่อ (Name)', 'Unknown')} {row.get('ชื่อสกุล (Surname)', '')}%0D%0A%0D%0Aขอบคุณที่สนใจและสมัครงานในตำแหน่ง {row.get('ตำแหน่งงานที่ท่านสนใจ', 'N/A')} กับทาง BDMS%0D%0Aทางเราได้รับใบสมัครของคุณแล้ว และขอเชิญคุณเข้าร่วมสัมภาษณ์งาน%0D%0A%0D%0Aวัน/เวลา: 20 กรกฎาคม 2568, 10:00 น.%0D%0Aสถานที่/ช่องทางสัมภาษณ์: Microsoft Teams%0D%0Aผู้สัมภาษณ์: HR Manager%0D%0A%0D%0Aกรุณายืนยันการเข้าร่วมสัมภาษณ์โดยการตอบกลับอีเมลนี้%0D%0Aหากมีข้อสงสัยหรือต้องการเปลี่ยนแปลงเวลา กรุณาติดต่อ 123-456-7890%0D%0A%0D%0Aขอขอบคุณและหวังว่าจะได้พบคุณในวันสัมภาษณ์%0D%0A%0D%0Aขอแสดงความนับถือ," target="_blank">
                    <button>📧 Send Interview Invite</button>
                </a>
                <a href="https://teams.microsoft.com/l/meeting/new" target="_blank">
                    <button style='background:#28a745; margin-left:10px;'>📅 Schedule Interview</button>
                </a>
            </div>
        """, unsafe_allow_html=True)

    # กราฟ (ใช้ st.write แทนชั่วคราว)
    st.subheader("📊 Data Visualizations")
    st.write("### Number of Applicants by Position")
    position_counts = filtered_df['ตำแหน่งงานที่ท่านสนใจ'].value_counts().reset_index()
    position_counts.columns = ['Position', 'Count']
    st.write(position_counts)

    st.write("### Experience Distribution")
    exp_counts = filtered_df['Experience_Years'].value_counts().reset_index()
    exp_counts.columns = ['Experience', 'Count']
    st.write(exp_counts)

    st.write("### BMI Level Distribution")
    bmi_counts = filtered_df['Info Level'].value_counts().reset_index()
    bmi_counts.columns = ['BMI Level', 'Count']
    st.write(bmi_counts)

else:
    st.info("Please upload a file or paste an Excel Online link to begin.")
