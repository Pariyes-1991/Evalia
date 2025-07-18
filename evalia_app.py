import streamlit as st
import pandas as pd
import requests
import io

# กำหนดการตั้งค่าแอป
st.set_page_config(
    page_title="Project Evalia",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# สไตล์ CSS ธีมขาวดำ
st.markdown(
    """
    <style>
    .stApp {
        background-color: #333333;
        color: #FFFFFF;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stHeader {
        background-color: #000000;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    .stButton>button {
        background-color: #FFFFFF;
        color: #000000;
        border: 1px solid #000000;
        padding: 8px 16px;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #000000;
        color: #FFFFFF;
        transform: scale(1.05);
    }
    .card {
        background: #444444;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
    }
    h1, h2, h3, h4 {
        color: #FFFFFF;
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
    .high { color: #00FF00; }
    .low { color: #FF0000; }
    </style>
    """,
    unsafe_allow_html=True
)

# หัวข้อและคำอธิบาย
st.markdown('<div class="stHeader"><h1>Project Evalia</h1><h3>Evalute + AI Applicant Analyzer with Extended Rule-Based Keywords</h3></div>', unsafe_allow_html=True)
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
    excel_link = st.text_input("Paste your Microsoft Excel Online Link:")
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

            keywords_high = ["lead", "manager", "senior", "expert", "specialist", "consultant", "director", "chief", "head", "principal"]
            keywords_mid = ["assist", "support", "junior", "operator", "staff", "clerk", "coordinator", "trainee"]

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

    # Summary (อยู่ด้านบน)
    st.subheader("Summary")
    st.write("### Number of Applicants by Position")
    position_counts = df['ตำแหน่งงานที่ท่านสนใจ'].value_counts().reset_index()
    position_counts.columns = ['Position', 'Count']
    st.write(position_counts)

    st.write("### Experience Distribution")
    exp_counts = df['Experience_Years'].value_counts().reset_index()
    exp_counts.columns = ['Experience', 'Count']
    st.write(exp_counts)

    st.write("### BMI Level Distribution")
    bmi_counts = df['Info Level'].value_counts().reset_index()
    bmi_counts.columns = ['BMI Level', 'Count']
    st.write(bmi_counts)

    # ส่วนการกรองข้อมูล
    st.subheader("Filter Applicants")
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
    st.subheader("Analyzed Applicants")
    for idx, row in filtered_df.iterrows():
        experience = row.get('ช่วยเล่าประสบการณ์การทำงานของท่านโดยละเอียด', 'N/A')
        name = f"{row.get('ชื่อ (Name)', 'Unknown')} {row.get('ชื่อสกุล (Surname)', '')}"
        position = row.get('ตำแหน่งงานที่ท่านสนใจ', 'N/A')
        date = "20 July"  # สามารถปรับได้
        time = "10:00 AM"  # สามารถปรับได้
        meeting_link = "https://teams.microsoft.com/l/meeting/new"  # สามารถปรับได้
        your_name = "HR Team"  # สามารถปรับได้

        # ข้อความสำหรับ Outlook
        mailto_link = f"mailto:?subject=Interview%20Invite%20-%20B%2B%20Hospital&body=เรียน%20{name},%0D%0Aขอบคุณที่สมัครงานในตำแหน่ง%20{position}%20กับทาง%20B%2B%20Hospital%0D%0Aทางเราได้รับใบสมัครของคุณเรียบร้อยแล้ว%20และขอเรียนเชิญเข้าร่วมสัมภาษณ์งาน%0D%0Aวัน/เวลา:%20{date}%20—%20{time}%0D%0Aสถานที่/ช่องทาง:%20Microsoft%20Teams%20({meeting_link})%0D%0Aผู้สัมภาษณ์:%20ผู้จัดการฝ่ายทรัพยากรบุคคล%0D%0Aกรุณายืนยันการเข้าร่วมสัมภาษณ์โดยการตอบกลับอีเมลนี้%0D%0Aหากมีข้อสงสัยหรือต้องการเปลี่ยนแปลงกำหนดการ%20กรุณาติดต่อ%2002-XXXXXXX%0D%0Aหวังว่าจะได้พบและพูดคุยกับคุณเร็วๆ%20นี้%0D%0Aขอแสดงความนับถือ%0D%0A{your_name}%0D%0Aฝ่ายทรัพยากรบุคคล%20B%2B%20Hospital"

        st.markdown(f"""
            <div class="card">
                <h4>{name}</h4>
                <ul>
                    <li><b>BMI:</b> {row['BMI'] if pd.notna(row['BMI']) else 'N/A'}</li>
                    <li><b>Info Level:</b> <span class="{row['Info Level'].lower()}">{row['Info Level']}</span> — {row['Info Reason']}</li>
                    <li><b>Experience Level:</b> <span class="{row['Exp Level'].lower()}">{row['Exp Level']}</span> — {row['Exp Reason']}</li>
                    <li><b>Position:</b> {position}</li>
                    <li><b>Department:</b> {row.get('กลุ่มแผนกที่ท่านสนใจ', 'N/A')}</li>
                    <li><b>TOEIC Score:</b> {row.get('TOEIC Score (ถ้ามี)', 'N/A')}</li>
                    <li><b>Experience Details:</b> {experience}</li>
                </ul>
                <a href="{mailto_link}" target="_blank" onClick="if(!window.location.href.includes('mailto')) alert('Failed to open Outlook. Please ensure Outlook is set as your default email client.');">
                    <button>Send Interview Invite</button>
                </a>
                <a href="{meeting_link}" target="_blank">
                    <button style='background:#FFFFFF; color:#000000; margin-left:10px;'>Schedule Interview</button>
                </a>
            </div>
        """, unsafe_allow_html=True)

else:
    st.info("Please upload a file or paste an Excel Online link to begin.")
