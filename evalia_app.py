import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(
    page_title="Project Evalia",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Sci-fi Theme
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
.stApp {
    background: radial-gradient(circle at top left, #0f172a, #000000);
    color: #e0f2fe;
    font-family: 'Orbitron', sans-serif;
}
.stHeader {
    background: linear-gradient(90deg, #06b6d4, #3b82f6, #9333ea);
    color: #ffffff;
    padding: 20px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 0 20px #06b6d4;
}
.stButton>button {
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 700;
    transition: all 0.3s ease;
    background: #06b6d4;
    color: white;
    border: none;
}
.stButton>button:hover {
    transform: scale(1.05);
    background: #0ea5e9;
    box-shadow: 0 0 10px #06b6d4;
}
.send-outlook {
    background: #3b82f6;
    color: #ffffff;
    border: none;
    padding: 10px 20px;
    font-weight: 700;
    border-radius: 12px;
    box-shadow: 0 0 10px #3b82f6;
}
.send-outlook:hover {
    background: #2563eb;
    transform: scale(1.05);
}
.schedule-teams {
    background: #9333ea;
    color: #ffffff;
    border: none;
    padding: 10px 20px;
    font-weight: 700;
    border-radius: 12px;
    margin-left: 10px;
    box-shadow: 0 0 10px #9333ea;
}
.schedule-teams:hover {
    background: #7e22ce;
    transform: scale(1.05);
}
.card {
    background: rgba(30, 41, 59, 0.85);
    padding: 20px;
    border-radius: 20px;
    margin-bottom: 20px;
    box-shadow: 0 0 15px rgba(6, 182, 212, 0.5);
    transition: all 0.3s ease;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 25px rgba(6, 182, 212, 0.8);
}
h1, h2, h3, h4 {
    color: #e0f2fe;
    font-weight: 700;
}
.summary-total {
    font-size: 36px;
    font-weight: 700;
    color: #facc15;
    text-shadow: 0 0 10px #facc15;
    margin-bottom: 15px;
}
.analyzed-total {
    font-size: 24px;
    font-weight: 700;
    color: #67e8f9;
    text-shadow: 0 0 8px #67e8f9;
    margin-top: 15px;
}
.high { color: #22c55e; font-weight: 700; text-shadow: 0 0 5px #22c55e; }
.mid { color: #facc15; font-weight: 700; text-shadow: 0 0 5px #facc15; }
.low { color: #ef4444; font-weight: 700; text-shadow: 0 0 5px #ef4444; }
.logo-container img {
    width: 100%;
    max-height: 500px;
    object-fit: contain;
    filter: drop-shadow(0 0 12px #06b6d4);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.image("Evalia_logo.png", use_column_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="stHeader"><h1>Project Evalia</h1><h3>Free AI Applicant Analyzer for BHQ HR</h3></div>', unsafe_allow_html=True)
st.divider()

upload_option = st.radio("Choose data input method:", ("Upload Excel File", "Provide Online Excel Link"), horizontal=True)

df = None
if upload_option == "Upload Excel File":
    uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
elif upload_option == "Provide Online Excel Link":
    excel_link = st.text_input("Paste your Microsoft Excel Online Link:")
    if excel_link:
        try:
            response = requests.get(excel_link, timeout=10)
            response.raise_for_status()
            df = pd.read_excel(io.BytesIO(response.content))
        except Exception as e:
            st.error(f"Error fetching Excel: {e}")

if df is not None:
    st.success("Data loaded successfully!")

    def calculate_bmi(row):
        try:
            weight = row['Weight_kg']
            height = row['Height_cm']
            if pd.isna(weight) or pd.isna(height) or height == 0:
                return None
            return round(weight / ((height / 100) ** 2), 2)
        except:
            return None

    def assign_info_level(bmi):
        if bmi is None:
            return "Unknown", "BMI data missing"
        elif bmi > 25:
            return "Low", "BMI exceeds 25"
        else:
            return "High", "BMI normal"

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

            desc_lower = str(description).lower()
            keywords_high = ["lead", "manager", "senior", "expert", "specialist", "consultant", "director", "chief", "head", "principal"]
            keywords_mid = ["assist", "support", "junior", "operator", "staff", "clerk", "coordinator", "trainee"]

            if years >= 5:
                return "High", "Over 5 years experience"
            elif years >= 2:
                return "Mid", "2-5 years experience"
            else:
                for kw in keywords_high:
                    if kw in desc_lower:
                        return "Mid", f"Keyword '{kw}' found"
                for kw in keywords_mid:
                    if kw in desc_lower:
                        return "Low", f"Keyword '{kw}' found"
                return "Low", "Less than 2 years, no keywords"
        except:
            return "Unknown", "Error in experience check"

    df['BMI'] = df.apply(calculate_bmi, axis=1)
    df[['Info Level', 'Info Reason']] = df['BMI'].apply(lambda x: pd.Series(assign_info_level(x)))
    df[['Exp Level', 'Exp Reason']] = df.apply(
        lambda row: pd.Series(assign_exp_level(
            row.get('Experience_Years', 0),
            row.get('ช่วยเล่าประสบการณ์การทำงานของท่านโดยละเอียด', '')
        )), axis=1)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Applicants", len(df))
    col2.metric("Unique Positions", df['ตำแหน่งงานที่ท่านสนใจ'].nunique())
    col3.metric("Analyzed Records", df.shape[0])

    st.subheader("Applicants Data")
    st.dataframe(df, use_container_width=True)

    st.subheader("Filters")
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        position_filter = st.selectbox("Filter by Position", ['All'] + df['ตำแหน่งงานที่ท่านสนใจ'].dropna().unique().tolist())
    with fcol2:
        bmi_filter = st.slider("Max BMI", min_value=0.0, max_value=40.0, value=25.0)

    filtered_df = df.copy()
    if position_filter != 'All':
        filtered_df = filtered_df[filtered_df['ตำแหน่งงานที่ท่านสนใจ'] == position_filter]
    filtered_df = filtered_df[fi]()
