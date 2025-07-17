import streamlit as st
import pandas as pd
import requests
import io

# กำหนดการตั้งค่าแอป
st.set_page_config(
    page_title="Evalia : Evalute + AI Applicant Analyzer with Extended Rule-Based Keywords",
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
    </style>
    """,
    unsafe_allow_html=True
)

# หัวข้อและคำอธิบาย
st.markdown('<div class="stHeader"><h1>Evalia : Evalute + AI Applicant Analyzer with Extended Rule-Based Keywords</h1></div>', unsafe_allow_html=True)
st.divider()

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
                "supervisor", "executive", "administrator", "coordinator", "overseer", "leader", "authority", "master",
                "physician", "surgeon", "anesthetist", "radiologist", "pediatrician", "neurosurgeon", "cardiologist",
                "orthopedist", "dermatologist", "endocrinologist", "gastroenterologist", "hematologist", "neurologist",
                "oncologist", "ophthalmologist", "otolaryngologist", "pathologist", "psychiatrist", "urologist",
                "doctor", "medic", "clinician", "therapist", "practitioner", "specialist", "consultant",
                "nurse", "registered nurse", "licensed nurse", "practical nurse", "head nurse", "chief nurse",
                "nursing supervisor", "clinical nurse", "emergency nurse", "pediatric nurse", "surgical nurse",
                "pharmacist", "pharmacy manager", "drug specialist", "dispensing chemist", "clinical pharmacist",
                "technologist", "medical technologist", "lab technician", "radiographer", "ultrasound technician",
                "x-ray technician", "mri technologist", "ct technologist", "sonographer", "echocardiographer",
                "therapist", "physical therapist", "occupational therapist", "speech therapist", "respiratory therapist",
                "rehabilitation specialist", "counselor", "psychologist", "social worker", "case manager",
                "administrator", "healthcare administrator", "hospital administrator", "medical director",
                "chief medical officer", "chief nursing officer", "operations manager", "hr manager", "recruiter",
                "trainer", "educator", "instructor", "mentor", "coach", "advisor", "guide", "facilitator",
                "assistant", "medical assistant", "nursing assistant", "pharmacy assistant", "lab assistant",
                "junior", "trainee", "intern", "apprentice", "beginner", "novice", "associate", "aide",
                "support", "helper", "attendant", "orderly", "caregiver", "aide-de-camp", "backup", "relief",
                "operator", "technician", "specialist", "expert", "professional", "practitioner", "clinician",
                "surgeon", "anesthesiologist", "radiologist", "pathologist", "cardiologist", "dermatologist",
                "endocrinologist", "gastroenterologist", "hematologist", "neurologist", "oncologist",
                "ophthalmologist", "otolaryngologist", "psychiatrist", "urologist", "orthopedist",
                "podiatrist", "geriatrician", "pulmonologist", "rheumatologist", "nephrologist",
                "hepatologist", "allergist", "immunologist", "infectious disease specialist",
                "critical care specialist", "emergency medicine specialist", "family medicine",
                "internal medicine", "preventive medicine", "sports medicine", "occupational medicine",
                "public health", "epidemiologist", "biostatistician", "health informatics specialist",
                "health policy analyst", "quality assurance manager", "risk manager", "compliance officer",
                "patient advocate", "health educator", "community health worker", "nutritionist",
                "dietitian", "genetic counselor", "reproductive endocrinologist", "perinatologist",
                "neonatologist", "pediatric surgeon", "pediatric cardiologist", "pediatric neurologist",
                "pediatric oncologist", "pediatric ophthalmologist", "pediatric otolaryngologist",
                "pediatric urologist", "pediatric orthopedist", "pediatric pulmonologist",
                "pediatric rheumatologist", "pediatric nephrologist", "pediatric hepatologist",
                "pediatric allergist", "pediatric immunologist", "pediatric infectious disease specialist",
                "geriatric psychiatrist", "geriatric neurologist", "geriatric oncologist",
                "geriatric ophthalmologist", "geriatric otolaryngologist", "geriatric urologist",
                "geriatric orthopedist", "geriatric pulmonologist", "geriatric rheumatologist",
                "geriatric nephrologist", "geriatric hepatologist", "geriatric allergist",
                "geriatric immunologist", "geriatric infectious disease specialist",
                "adult nurse practitioner", "family nurse practitioner", "acute care nurse practitioner",
                "gerontological nurse practitioner", "psychiatric nurse practitioner",
                "women’s health nurse practitioner", "neonatal nurse practitioner",
                "pediatric nurse practitioner", "orthopedic nurse practitioner",
                "cardiovascular nurse practitioner", "oncology nurse practitioner",
                "emergency nurse practitioner", "surgical nurse practitioner",
                "pharmacy technician", "pharmaceutical sales representative",
                "clinical research coordinator", "clinical trial manager",
                "data analyst", "biomedical engineer", "medical device specialist",
                "healthcare IT specialist", "telemedicine coordinator", "patient navigator",
                "care coordinator", "discharge planner", "utilization review coordinator",
                "case management supervisor", "home health aide", "hospice worker",
                "palliative care specialist", "wound care specialist", "infection control nurse",
                "sterile processing technician", "endoscopy technician", "cardiac catheterization technician",
                "electroneurodiagnostic technologist", "polysomnographic technologist",
                "vascular technologist", "nuclear medicine technologist",
                "radiation therapist", "dosimetrist", "medical physicist",
                "healthcare consultant", "hospital planner", "facility manager",
                "supply chain manager", "procurement specialist", "inventory manager",
                "billing specialist", "coding specialist", "reimbursement analyst",
                "revenue cycle manager", "patient account representative", "financial counselor",
                "insurance coordinator", "claims adjuster", "peer review coordinator",
                "quality improvement coordinator", "patient safety officer",
                "risk management coordinator", "compliance auditor", "ethics officer",
                "privacy officer", "security officer", "emergency preparedness coordinator",
                "disaster response coordinator", "public relations officer", "marketing manager",
                "business development manager", "strategic planner", "project manager",
                "program director", "executive director", "chief executive officer",
                "chief operating officer", "chief financial officer", "chief information officer",
                "chief strategy officer", "chief compliance officer", "chief risk officer",
                "chief innovation officer", "chief medical information officer",
                "chief nursing information officer", "chief patient experience officer",
                "chief quality officer", "chief transformation officer",
                "vice president", "director of nursing", "director of pharmacy",
                "director of laboratory services", "director of radiology",
                "director of surgery", "director of emergency services",
                "director of critical care", "director of rehabilitation",
                "director of outpatient services", "director of inpatient services",
                "director of behavioral health", "director of women’s services",
                "director of pediatric services", "director of geriatric services",
                "director of oncology services", "director of cardiology services",
                "director of neurology services", "director of orthopedics services",
                "director of urology services", "director of gastroenterology services",
                "director of endocrinology services", "director of dermatology services",
                "director of hematology services", "director of ophthalmology services",
                "director of otolaryngology services", "director of psychiatry services",
                "director of infectious disease services", "director of allergy services",
                "director of immunology services", "director of rheumatology services",
                "director of nephrology services", "director of hepatology services",
                "director of pulmonology services", "director of critical care services",
                "director of emergency medicine services", "director of family medicine services",
                "director of internal medicine services", "director of preventive medicine services",
                "director of sports medicine services", "director of occupational medicine services",
                "director of public health services", "director of epidemiology services",
                "director of biostatistics services", "director of health informatics services",
                "director of health policy services", "director of quality assurance services",
                "director of risk management services", "director of compliance services",
                "director of patient advocacy services", "director of health education services",
                "director of community health services", "director of nutrition services",
                "director of genetic counseling services", "director of reproductive endocrinology services",
                "director of perinatology services", "director of neonatology services",
                "director of pediatric surgery services", "director of pediatric cardiology services",
                "director of pediatric neurology services", "director of pediatric oncology services",
                "director of pediatric ophthalmology services", "director of pediatric otolaryngology services",
                "director of pediatric urology services", "director of pediatric orthopedics services",
                "director of pediatric pulmonology services", "director of pediatric rheumatology services",
                "director of pediatric nephrology services", "director of pediatric hepatology services",
                "director of pediatric allergy services", "director of pediatric immunology services",
                "director of pediatric infectious disease services", "director of geriatric psychiatry services",
                "director of geriatric neurology services", "director of geriatric oncology services",
                "director of geriatric ophthalmology services", "director of geriatric otolaryngology services",
                "director of geriatric urology services", "director of geriatric orthopedics services",
                "director of geriatric pulmonology services", "director of geriatric rheumatology services",
                "director of geriatric nephrology services", "director of geriatric hepatology services",
                "director of geriatric allergy services", "director of geriatric immunology services",
                "director of geriatric infectious disease services"
            ]
            keywords_mid = [
                "assist", "support", "junior", "operator", "staff", "clerk", "coordinator", "trainee",
                "helper", "attendant", "orderly", "caregiver", "aide", "backup", "relief", "associate",
                "novice", "apprentice", "intern", "beginner", "aide-de-camp", "assistant", "deputy",
                "subordinate", "understudy", "protégé", "learner", "student", "candidate", "applicant",
                "registered nurse", "practical nurse", "medical assistant", "pharmacy technician",
                "lab technician", "radiographer", "ultrasound technician", "x-ray technician",
                "mri technologist", "ct technologist", "sonographer", "echocardiographer",
                "physical therapist", "occupational therapist", "speech therapist",
                "respiratory therapist", "rehabilitation assistant", "counseling assistant",
                "psychology intern", "social work intern", "case management assistant",
                "healthcare support worker", "nursing aide", "pharmacy aide", "lab aide",
                "radiology aide", "therapy aide", "rehab aide", "counseling aide",
                "social work aide", "case aide", "support staff", "junior staff",
                "trainee nurse", "trainee pharmacist", "trainee technologist",
                "junior therapist", "junior counselor", "junior social worker",
                "junior case manager", "entry-level nurse", "entry-level pharmacist",
                "entry-level technologist", "entry-level therapist", "entry-level counselor",
                "entry-level social worker", "entry-level case manager", "assistant nurse",
                "assistant pharmacist", "assistant technologist", "assistant therapist",
                "assistant counselor", "assistant social worker", "assistant case manager",
                "support nurse", "support pharmacist", "support technologist",
                "support therapist", "support counselor", "support social worker",
                "support case manager", "junior nurse", "junior pharmacist",
                "junior technologist", "junior therapist", "junior counselor",
                "junior social worker", "junior case manager", "trainee assistant",
                "trainee support", "trainee operator", "trainee clerk",
                "trainee coordinator", "trainee helper", "trainee attendant",
                "trainee orderly", "trainee caregiver", "trainee aide",
                "trainee backup", "trainee relief", "trainee associate",
                "trainee novice", "trainee apprentice", "trainee intern",
                "trainee beginner", "trainee candidate", "trainee applicant",
                "junior assistant", "junior support", "junior operator",
                "junior clerk", "junior coordinator", "junior helper",
                "junior attendant", "junior orderly", "junior caregiver",
                "junior aide", "junior backup", "junior relief",
                "junior associate", "junior novice", "junior apprentice",
                "junior intern", "junior beginner", "junior candidate",
                "junior applicant", "entry-level assistant", "entry-level support",
                "entry-level operator", "entry-level clerk", "entry-level coordinator",
                "entry-level helper", "entry-level attendant", "entry-level orderly",
                "entry-level caregiver", "entry-level aide", "entry-level backup",
                "entry-level relief", "entry-level associate", "entry-level novice",
                "entry-level apprentice", "entry-level intern", "entry-level beginner",
                "entry-level candidate", "entry-level applicant"
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

    # Summary (อยู่ด้านบน)
    st.subheader("Summary")
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
        st.markdown(f"""
            <div class="card">
                <h4>{row.get('ชื่อ (Name)', 'Unknown')} {row.get('ชื่อสกุล (Surname)', '')}</h4>
                <ul>
                    <li><b>BMI:</b> {row['BMI'] if pd.notna(row['BMI']) else 'N/A'}</li>
                    <li><b>Info Level:</b> {row['Info Level']} — {row['Info Reason']}</li>
                    <li><b>Experience Level:</b> {row['Exp Level']} — {row['Exp Reason']}</li>
                    <li><b>Position:</b> {row.get('ตำแหน่งงานที่ท่านสนใจ', 'N/A')}</li>
                    <li><b>Department:</b> {row.get('กลุ่มแผนกที่ท่านสนใจ', 'N/A')}</li>
                    <li><b>TOEIC Score:</b> {row.get('TOEIC Score (ถ้ามี)', 'N/A')}</li>
                    <li><b>Experience Details:</b> {experience}</li>
                </ul>
                <a href="mailto:?subject=แจ้งนัดสัมภาษณ์งานกับ BDMS&body=เรียนคุณ {row.get('ชื่อ (Name)', 'Unknown')}%20{row.get('ชื่อสกุล (Surname)', '')}%0D%0A%0D%0Aขอบคุณที่สนใจและสมัครงานในตำแหน่ง%20{row.get('ตำแหน่งงานที่ท่านสนใจ', 'N/A')}%20กับทาง%20BDMS%0D%0Aทางเราได้รับใบสมัครของคุณแล้ว%20และขอเชิญคุณเข้าร่วมสัมภาษณ์งาน%0D%0A%0D%0Aวัน/เวลา:%2020%20กรกฎาคม%202568,%2010:00%20น.%0D%0Aสถานที่/ช่องทางสัมภาษณ์:%20Microsoft%20Teams%0D%0Aผู้สัมภาษณ์:%20HR%20Manager%0D%0A%0D%0Aกรุณายืนยันการเข้าร่วมสัมภาษณ์โดยการตอบกลับอีเมลนี้%0D%0Aหากมีข้อสงสัยหรือต้องการเปลี่ยนแปลงเวลา%20กรุณาติดต่อ%20123-456-7890%0D%0A%0D%0Aขอขอบคุณและหวังว่าจะได้พบคุณในวันสัมภาษณ์%0D%0A%0D%0Aขอแสดงความนับถือ" target="_blank">
                    <button>Send Interview Invite</button>
                </a>
                <a href="https://teams.microsoft.com/l/meeting/new" target="_blank">
                    <button style='background:#FFFFFF; color:#000000; margin-left:10px;'>Schedule Interview</button>
                </a>
            </div>
        """, unsafe_allow_html=True)

else:
    st.info("Please upload a file or paste an Excel Online link to begin.")
