import streamlit as st
import pandas as pd
import io
import requests
import re
from transformers import pipeline

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
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 1px solid #d2d2d7;
        padding: 10px;
        font-size: 14px;
        background-color: #f5f5f7;
        color: #1d1d1f;
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

# Load pipeline for distilbert-base-uncased (fill-mask task)
@st.cache_resource
def load_pipeline():
    try:
        pipe = pipeline("fill-mask", model="distilbert/distilbert-base-uncased")
        return pipe
    except Exception as e:
        st.error(f"Error loading pipeline: {str(e)}. Falling back to rule-based analysis.")
        return None

pipe = load_pipeline()

# Function to fetch Excel data from SharePoint link
def fetch_excel_data(link):
    try:
        if not link.startswith('https://'):
            st.error("Invalid URL format. Please use a full HTTPS link.")
            return None
        
        download_url = re.sub(r"(\?e=.*)$", "?download=1", link)
        st.write(f"Attempting to fetch from: {download_url}")
        
        response = requests.get(download_url, timeout=10)
        response.raise_for_status()
        
        excel_data = io.BytesIO(response.content)
        df = pd.read_excel(excel_data)
        return df
    except requests.exceptions.ConnectionError as e:
        st.error(f"Connection error: {str(e)}. Please ensure the link is publicly accessible or check your network.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error: {str(e)}. The link may require authentication or is invalid.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again later.")
        return None
    except Exception as e:
        st.error(f"Error fetching Excel data: {str(e)}. Ensure the SharePoint link is valid and accessible.")
        return None

# Function to analyze applicant with AI or rule-based fallback
def analyze_applicant(row):
    try:
        height_m = float(row.get('Height_cm', 0)) / 100
        weight = float(row.get('Weight_kg', 0))
        bmi = weight / (height_m ** 2) if height_m > 0 else 0
        
        position = str(row.get('Position', '')).lower()
        experience_years = float(row.get('Experience_Years', 0))
        input_text = f"Position: {position}, Experience: {experience_years} years, [MASK] suitability"
        
        level = "Mid"
        reason = "Analysis based on fallback logic"
        
        if pipe:
            # Use fill-mask to infer suitability
            result = pipe(input_text)
            top_prediction = result[0]['token_str'] if result and len(result) > 0 else "moderate"
            if 'high' in top_prediction.lower() or experience_years >= 5:
                level = "High"
            elif 'low' in top_prediction.lower() or bmi > 25:
                level = "Low"
            else:
                level = "Mid"
            reason = f"AI predicted suitability as {top_prediction} (experience: {experience_years} years)"
        
        if bmi > 25:
            level = "Low"
            reason = "BMI exceeds 25, indicating potential health concerns"
        elif not pipe:
            # Fallback rule-based logic
            if 'senior' in position or experience_years >= 5:
                level = "High"
            elif experience_years >= 2:
                level = "Mid"
            else:
                level = "Low"
            reason = "Rule-based analysis due to pipeline loading failure"
        
        return pd.Series({
            'BMI': round(bmi, 1),
            'Level': level,
            'Reason': reason
        })
    except Exception as e:
        return pd.Series({
            'BMI': 0,
            'Level': 'Low',
            'Reason': f'Error in analysis: {str(e)}'
        })

# Main app
def main():
    st.markdown('<div class="header-section"><h1>Evalia</h1><h3>Applicant Analysis Platform</h3></div>', unsafe_allow_html=True)
    
    excel_link = st.text_input(
        "Paste Microsoft Excel Online Link",
        placeholder="https://yourdomain.sharepoint.com/:x:/...",
        value="https://bdmsgroup-my.sharepoint.com/:x:/g/personal/recruitment_bdms_co_th/EemR4Mg1E_pFr41PR8vBKPEB2GM_vy3iSfXv6BqWKQE58A?e=SN2YUk",
        help="Enter a valid OneDrive or SharePoint Excel link"
    )

    if st.button("Fetch & Analyze"):
        if excel_link:
            with st.spinner("Fetching and analyzing data..."):
                df = fetch_excel_data(excel_link)
                if df is not None:
                    st.write("Available columns in the Excel file:", df.columns.tolist())
                    # Analyze applicants
                    analysis_results = df.apply(analyze_applicant, axis=1)
                    df = pd.concat([df, analysis_results], axis=1)
                    st.session_state['applicants'] = df
        else:
            st.error("Please provide a valid Excel link")

    if 'applicants' in st.session_state:
        df = st.session_state['applicants']
        st.subheader("Applicant Analysis Results")
        
        available_columns = ['ApplicationDate', 'FirstName', 'LastName', 'Position', 'Department', 
                           'Height_cm', 'Weight_kg', 'BMI', 'Level', 'Reason']
        display_df = df[[col for col in available_columns if col in df.columns]]  # Corrected syntax
        st.dataframe(display_df, use_container_width=True)
        
        for index, row in df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="applicant-card">
                    <h3>{row.get('FirstName', '')} {row.get('LastName', '')}</h3>
                    <p><strong>Application Date:</strong> {row.get('ApplicationDate', '')}</p>
                    <p><strong>Position:</strong> {row.get('Position', '')}</p>
                    <p><strong>Department:</strong> {row.get('Department', '')}</p>
                    <p><strong>Height:</strong> {row.get('Height_cm', 0)} cm</p>
                    <p><strong>Weight:</strong> {row.get('Weight_kg', 0)} kg</p>
                    <p><strong>BMI:</strong> {row.get('BMI', 0)}</p>
                    <p><strong>Level:</strong> {row.get('Level', '')}</p>
                    <p><strong>Reason:</strong> {row.get('Reason', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    email = row.get('Email', 'applicant@example.com')
                    subject = f"Evalia: Application Review - {row.get('FirstName', '')} {row.get('LastName', '')}"
                    body = f"Dear {row.get('FirstName', '')},\n\nThank you for your application for {row.get('Position', '')}..."
                    mailto_link = f"mailto:{email}?subject={subject}&body={body}"
                    st.markdown(f'<a href="{mailto_link}" target="_blank"><button>Send Email</button></a>', 
                              unsafe_allow_html=True)
                
                with col2:
                    teams_link = "https://teams.microsoft.com/l/meeting/new"
                    st.markdown(f'<a href="{teams_link}" target="_blank"><button>Schedule Interview</button></a>', 
                              unsafe_allow_html=True)

if __name__ == "__main__":
    main()
