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

# สไตล์ CSS ธีมพื้นหลังดำ ใช้ฟอนต์ "Fira Code" สีอ่านง่าย
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code&display=swap');
    .stApp {
        background-color: #000000;
        color: #d1d5db;
        font-family: 'Fira Code', monospace;
    }
    .stHeader {
        background-color: #1a202c;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    .stButton>button {
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .send-outlook {
        background-color: #1e40af;
        color: #ffffff;
        border: 1px solid #1e40af;
        padding: 8px 16px;
    }
    .send-outlook:hover {
        background-color: #1e3a8a;
        color: #ffffff;
        transform: scale(1.05);
    }
    .schedule-teams {
        background-color: #6b21a8;
        color: #ffffff;
        border: 1px solid #6b21a8;
        padding: 8px 16px;
        margin-left: 10px;
    }
    .schedule-teams:hover {
        background-color: #5b1a99;
        color: #ffffff;
        transform: scale(1.05);
    }
    .send-passed {
        background-color: #10b981;
        color: #ffffff;
        border: 1px solid #10b981;
        padding: 8px 16px;
        margin-left: 10px;
    }
    .send-passed:hover {
        background-color: #059669;
        color: #ffffff;
        transform: scale(1.05);
    }
    .card {
        background: #2d3748;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    h1, h2, h3, h4 {
        color: #e2e8f0;
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
    .mid { color: #FFFF00; }
    .summary-total {
        font-size: 32px;
        font-weight: bold;
        color: #e2e8f0;
        margin-bottom: 10px;
    }
    .analyzed-total {
        font-size: 20px;
        font-weight: bold;
        color: #e2e8f0;
        margin-top: 10px;
    }
    .logo-container {
        width: 100%;
        text-align: center;
        margin-bottom: 10px;
    }
    .logo-container img {
        width: 100%;
        max-height: 600px;
        object-fit: contain;
        image-rendering: -webkit-optimize-contrast;
        image-rendering: crisp-edges;
    }
    .description {
        color: #e2e8f0;
        padding: 20px;
        background-color: #1a202c;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .description a {
        color: #93c5fd;
        text-decoration: underline;
    }
    .description ul {
        list-style-type: "✅ ";
        padding-left: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# แสดงโลโก้
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.image("Evalia_logo.png", width=1920)
st.markdown('</div>', unsafe_allow_html=True)

# คำอธิบายหน้าแรก
st.markdown(
    """
    <div class="description">
        <h2>EVALIA — AI-Powered Applicant Analyzer for BHQ HR</h2>
        <p><a href="https://project-evalia.streamlit.app/" target="_blank">https://project-evalia.streamlit.app/</a></p>
        <h3>Key Features:</h3>
        <ul>
            <li>BMI Check — Automatically calculates BMI and classifies applicants' health status for BHQ HR.</li>
            <li>Experience Analyzer — Assesses candidates using keyword detection in job descriptions.</li>
            <li>Position & Skill Filter — Filter applicants by position, BMI threshold, and TOEIC scores.</li>
            <li>Interview Tools — One-click buttons to send invites via Outlook or schedule on Microsoft Teams.</li>
            <li>User-Friendly Dashboard — Clean, intuitive UI powered by Streamlit for BHQ HR teams.</li>
        </ul>
        <p>EVALIA is a cutting-edge Applicant Analyzer designed to enhance decision-making for BHQ HR by providing a comprehensive Dashboard.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# การเลือกวิธีการนำเข้าข้อมูล
upload_option = st.radio("Choose data input method:", ("Upload Excel File", "Provide Online Excel Link"), horizontal=True)

df = None
if upload_option == "Upload Excel File":
    uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.success("Data loaded successfully from uploaded file!")
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")
elif upload_option == "Provide Online Excel Link":
    excel_link = st.text_input("Paste your Microsoft Excel Online Link:")
    if excel_link:
        try:
            response = requests.get(excel_link, stream=True, timeout=10)
            response.raise_for_status()
            df = pd.read_excel(io.BytesIO(response.content))
            st.success("Data loaded successfully from online link!")
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
            return "Low", "BMI exceeds 25, health concern noted"
        else:
            return "High", "BMI within normal range, suitable for BHQ HR"

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
                "executive", "supervisor", "team leader", "project manager", "architect", "strategist", "advisor", "partner",
                "vice president", "general manager", "coordinator lead", "master", "professor", "engineer lead", "analyst senior"
            ]
            keywords_mid = [
                "assist", "support", "junior", "operator", "staff", "clerk", "coordinator", "trainee", "associate", "assistant",
                "technician", "helper", "intern", "apprentice", "administrator", "analyst", "officer", "representative",
                "executive assistant", "data entry", "customer service", "field assistant", "junior developer", "team member"
            ]

            desc_lower = str(description).lower()

            if years >= 5 or any(word in desc_lower for word in keywords_high):
                return "High", "Experience over 5 years or senior role detected"
            elif years >= 2 or any(word in desc_lower for word in keywords_mid):
                return "Mid", "Experience between 2-5 years or mid-level role"
            else:
                return "Low", "Less than 2 years or no significant keywords"
        except Exception as e:
            return "Unknown", f"Error processing experience: {e}"

    # คำนวณ BMI และระดับ
    df['BMI'] = df.apply(calculate_bmi, axis=1)
    df[['Info Level', 'Info Reason']] = df['BMI'].apply(lambda bmi: pd.Series(assign_info_level(bmi)))
    df[['Exp Level', 'Exp Reason']] = df.apply(
        lambda row: pd.Series(assign_exp_level(
            row.get('Experience_Years', 0),
            row.get('ช่วยเล่าประสบการณ์การทำงานของท่านโดยละเอียด', '')
        )), axis=1
    )

    # ฟังก์ชันกำหนด Rank
    def assign_rank(row):
        info_level = row['Info Level']
        exp_level = row['Exp Level']
        high_count = sum(1 for level in [info_level, exp_level] if level == "High")
        mid_count = sum(1 for level in [info_level, exp_level] if level in ["High", "Mid"])
        low_count = sum(1 for level in [info_level, exp_level] if level == "Low")

        if high_count >= 2:
            return "High Rank"
        elif mid_count >= 2:
            return "Mid Rank"
        elif low_count >= 2:
            return "Low Rank"
        return "Unranked"

    df['Rank'] = df.apply(assign_rank, axis=1)

    # Summary
    st.subheader("Summary")
    total_applicants = len(df)
    st.markdown(f'<div class="summary-total">Total Applicants: {total_applicants}</div>', unsafe_allow_html=True)
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

    # Status Summary
    st.subheader("Status Summary")
    if 'applicant_statuses' not in st.session_state:
        st.session_state['applicant_statuses'] = {}
    status_counts = {status: list(st.session_state['applicant_statuses'].values()).count(status) for status in ['ไม่ผ่านคัดเลือก', 'นัดสัมภาษณ์แล้ว', 'ผ่านสัมภาษณ์', 'ไม่ผ่านสัมภาษณ์']}
    status_df = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
    st.write(status_df)

    # Filter Applicants
    st.subheader("Filter Applicants")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        selected_date = st.date_input("Select Date", value=None)
    with col2:
        rank_options = ['All', 'High Rank', 'Mid Rank', 'Low Rank']
        selected_rank = st.selectbox("Rank", rank_options)
    with col3:
        position_options = ['All'] + list(df['ตำแหน่งงานที่ท่านสนใจ'].dropna().unique())
        selected_position = st.selectbox("Position", position_options)
    with col4:
        exp_options = ['All', 'มากกว่า 10ปี', '7-10 ปี', '4-6 ปี', '1-3 ปี']
        selected_exp = st.selectbox("Experience", exp_options)
    with col5:
        toeic_min = st.number_input("Minimum TOEIC Score", min_value=0, max_value=990, value=0)
    with col6:
        bmi_max = st.number_input("Maximum BMI", min_value=0.0, value=25.0)

    # กรองข้อมูล
    filtered_df = df.copy()
    if selected_date:
        if 'Application Date' in df.columns:
            filtered_df = filtered_df[filtered_df['Application Date'] == pd.Timestamp(selected_date)]
    if selected_rank != 'All':
        filtered_df = filtered_df[filtered_df['Rank'] == selected_rank]
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

    # Analyzed Applicants
    st.subheader("Analyzed Applicants")
    total_analyzed = len(filtered_df)
    st.markdown(f'<div class="analyzed-total">Total Analyzed: {total_analyzed}</div>', unsafe_allow_html=True)
    for idx, row in filtered_df.iterrows():
        experience = row.get('ช่วยเล่าประสบการณ์การทำงานของท่านโดยละเอียด', 'N/A')
        name = f"{row.get('ชื่อ (Name)', 'Unknown')} {row.get('ชื่อสกุล (Surname)', '')}"
        position = row.get('ตำแหน่งงานที่ท่านสนใจ', 'N/A')
        expected_salary = row.get('เงินเดือนที่คาดหวัง', 'N/A')
        email = row.get('Email', f"{name.replace(' ', '.')}@example.com").replace(' ', '.')
        status_key = f"{name}_{idx}"
        current_status = st.session_state['applicant_statuses'].get(status_key, 'None')

        date = "23 July 2025"
        time = "09:00 AM"
        meeting_link = "https://teams.microsoft.com/l/meeting/new"
        your_name = "BHQ HR Team"

        mailto_link = f"mailto:?subject=Interview%20Invitation%20-%20{name}&body=Dear%20{name},%0D%0AWe%20are%20pleased%20to%20invite%20you%20for%20an%20interview%20for%20{position}%20on%20{date}%20at%20{time}.%20Please%20confirm%20your%20availability.%0D%0ARegards,%0A{your_name}"
        passed_mailto_link = f"mailto:{email}?subject=Congratulations%20-%20You%20Have%20Passed%20the%20Interview%20for%20{position}&body=Dear%20{name},%0D%0AWe%20are%20delighted%20to%20inform%20you%20that%20you%20have%20passed%20the%20interview%20for%20{position}.%20Please%20contact%20us%20for%20next%20steps.%0D%0ARegards,%0A{your_name}"

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
                    <li><b>Expected Salary:</b> {expected_salary}</li>
                    <li><b>Experience Details:</b> {experience}</li>
                </ul>
                <a href="{mailto_link}" target="_blank" onclick="if(!window.location.href.includes('mailto')) alert('Failed to open Outlook. Ensure Outlook is your default email client.');">
                    <button class="send-outlook">Send Interview Invite via Outlook</button>
                </a>
                <a href="{meeting_link}" target="_blank">
                    <button class="schedule-teams">Schedule Interview via Teams</button>
                </a>
            </div>
        """, unsafe_allow_html=True)

        selected_status = st.selectbox(f"Status: {name}", ['ไม่ผ่านคัดเลือก', 'นัดสัมภาษณ์แล้ว', 'ผ่านสัมภาษณ์', 'ไม่ผ่านสัมภาษณ์'], 
                                      index=['ไม่ผ่านคัดเลือก', 'นัดสัมภาษณ์แล้ว', 'ผ่านสัมภาษณ์', 'ไม่ผ่านสัมภาษณ์'].index(current_status) if current_status in ['ไม่ผ่านคัดเลือก', 'นัดสัมภาษณ์แล้ว', 'ผ่านสัมภาษณ์', 'ไม่ผ่านสัมภาษณ์'] else 0, 
                                      key=f"status_{idx}", on_change=lambda: (st.session_state.update({status_key: st.session_state[f"status_{idx}"]},), st.rerun()))

        if st.session_state.get(status_key, 'None') == 'ผ่านสัมภาษณ์':
            st.markdown(f"""
                <a href="{passed_mailto_link}" target="_blank">
                    <button class="send-passed">Send Passed Notification</button>
                </a>
            """, unsafe_allow_html=True)

else:
    st.info("Please upload a file or paste an Excel Online link to begin.")
