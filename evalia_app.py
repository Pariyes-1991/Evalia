import streamlit as st
import pandas as pd
import requests
import io

# Custom CSS for modern Apple-inspired theme
st.markdown("""
<style>
    .main {
        background-color: #ffffff;
        padding: 40px 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #1d1d1f;
    }
    .stButton>button {
        background: linear-gradient(135deg, #0071e3, #005bb5);
        color: #ffffff;
        border-radius: 12px;
        padding: 10px 20px;
        border: none;
        font-size: 14px;
        font-weight: 600;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0066cc, #004d99);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        transform: translateY(-1px);
    }
    .stFileUploader > div > div > div {
        border-radius: 12px;
        border: 1px solid #d2d2d7;
        padding: 10px;
        background-color: #f5f5f7;
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        background-color: #ffffff;
    }
    h1, h2, h3 {
        color: #1d1d1f;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    .applicant-card {
        background: #f5f5f7;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e5e5ea;
        transition: all 0.2s ease;
    }
    .applicant-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    .header-section {
        text-align: center;
        padding: 30px 0;
        background: linear-gradient(135deg, #ffffff, #f5f5f7);
        border-radius: 12px;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Backend API URL (adjust based on deployment)
API_URL = "http://localhost:8000/analyze"  # Replace with deployed URL (e.g., Replit, Railway)

def analyze_data(file):
    files = {"file": (file.name, file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    response = requests.post(API_URL, files=files, timeout=30)
    if response.status_code == 200:
        return pd.DataFrame(response.json()["data"])
    else:
        st.error(f"Error: {response.json().get('message', 'Failed to analyze data')}")
        return None

def main():
    st.markdown('<div class="header-section"><h1>Evalia</h1><h3>Applicant Analysis Platform</h3></div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    
    if st.button("Analyze Data"):
        if uploaded_file:
            with st.spinner("Analyzing data..."):
                df = analyze_data(uploaded_file)
                if df is not None:
                    st.session_state['applicants'] = df
        else:
            st.error("Please upload an Excel file")

    if 'applicants' in st.session_state:
        df = st.session_state['applicants']
        st.subheader("Applicant Analysis Results")
        
        available_columns = ['ApplicationDate', 'FirstName', 'LastName', 'Position', 'Department', 
                           'Height_cm', 'Weight_kg', 'BMI', 'Level', 'Reason', 'Email']
        display_df = df[[col for col in available_columns if col in df.columns]]
        st.dataframe(display_df, use_container_width=True)
        
        for index, row in df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="applicant-card">
                    <h3>{row.get('FirstName', '')} {row.get('LastName', '')}</h3>
                    <p><strong>Application Date:</strong> {row.get('ApplicationDate', '')}</p>
                    <p><strong>Position:</strong> {row.get('Position', '')}</p>
                    <p><strong>Department:</strong> {row.get('Department', '')}</p>
                    <p><strong>
