import streamlit as st
import pandas as pd
import io
import requests
import re

# Custom CSS for black-white theme with cool font
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #ffffff 0%, #000000 100%);
        padding: 30px;
        font-family: 'Arial Black', 'Impact', sans-serif;
        color: #ffffff;
    }
    .stButton>button {
        background: linear-gradient(45deg, #333333, #666666);
        color: #ffffff;
        border-radius: 20px;
        padding: 12px 24px;
        border: 2px solid #ffffff;
        font-size: 16px;
        font-weight: bold;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #666666, #999999);
        box-shadow: 0 6px 20px rgba(255, 255, 255, 0.5);
        transform: translateY(-2px);
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #ffffff;
        padding: 12px;
        font-size: 16px;
        background-color: #222222;
        color: #ffffff;
    }
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 20px rgba(255, 255, 255, 0.2);
        background-color: #1a1a1a;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 900;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.7);
    }
    .applicant-card {
        background: #2d2d2d;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 5px 20px rgba(255, 255, 255, 0.1);
        border: 1px solid #444444;
        transition: all 0.3s ease;
    }
    .applicant-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(255, 255, 255, 0.2);
    }
    .sci-fi-header {
        text-align: center;
        padding: 20px;
        background: #333333;
        border-radius: 15px;
        color: #ffffff;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.8);
    }
</style>
""", unsafe_allow_html=True)

# Function to fetch Excel data from SharePoint link
def fetch_excel_data(link):
    try:
        # Ensure the URL is valid and includes the full domain
        if not link.startswith('https://'):
            st.error("Invalid URL format. Please use a full HTTPS link.")
            return None
        
        # Attempt to convert to download link
        download_url = re.sub(r"(\?e=.*)$", "?download=1", link)
        st.write(f"Attempting to fetch from: {download_url}")  # Debug output
        
        response = requests.get(download_url, timeout=10)
        response.raise_for_status()
        
        excel_data = io.BytesIO(response.content)
        df = pd.read_excel(excel_data)
        return df
    except requests.exceptions.ConnectionError as e:
        st.error(f"Connection error: {str(e)}. Please check the URL and ensure the file is publicly accessible.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again later.")
        return None
    except Exception as e:
        st.error(f"Error fetching Excel data: {str(e)}. Ensure the SharePoint link is valid and accessible.")
        return None

# Function to analyze applicant and assign score
def analyze_applicant(row):
    try:
        # Calculate BMI (Height in cm to meters)
        height_m = float(row.get('Height_cm', 0)) / 100
        weight = float(row.get('Weight_kg', 0))
        bmi = weight / (height_m ** 2) if height_m > 0 else 0
        
        # Rule-based scoring
        score = "Low"
        reason = "Initial assessment"
        
        if bmi > 25:
            score = "Low"
            reason = "BMI exceeds 25, indicating potential health concerns"
        else:
            experience_years = float(row.get('Experience_Years', 0))
            position = str(row.get('Position', '')).lower()
            
            if 'senior' in position or experience_years >= 5:
                score = "High"
                reason = "Significant experience or senior position detected"
            elif experience_years >= 2:
                score = "Mid"
                reason = "Moderate experience level"
            else:
                score = "Low"
                reason = "Limited experience or junior position"
        
        return pd.Series({
            'BMI': round(bmi, 1),
            'Score': score,
            'Reason': reason
        })
    except Exception as e:
        return pd.Series({
            'BMI': 0,
            'Score': 'Low',
            'Reason': f'Error in analysis: {str(e)}'
        })

# Main app
def main():
    st.markdown('<div class="sci-fi-header"><h1>Evalia: Applicant Analysis Platform</h1></div>', unsafe_allow_html=True)
    
    # Input for Excel link
    excel_link = st.text_input(
        "Paste SharePoint Excel Link",
        placeholder="https://bdmsgroup-my.sharepoint.com/:x:/...",
        value="https://bdmsgroup-my.sharepoint.com/:x:/g/personal/recruitment_bdms_co_th/EemR4Mg1E_pFr41PR8vBKPEB2GM_vy3iSfXv6BqWKQE58A?e=Bm1TdX"
    )

    if st.button("Fetch & Analyze"):
        if excel_link:
            with st.spinner("Fetching and analyzing data..."):
                df = fetch_excel_data(excel_link)
                if df is not None:
                    # Analyze applicants
                    analysis_results = df.apply(analyze_applicant, axis=1)
                    df = pd.concat([df, analysis_results], axis=1)
                    st.session_state['applicants'] = df
        else:
            st.error("Please provide a valid Excel link")

    # Display results
    if 'applicants' in st.session_state:
        df = st.session_state['applicants']
        st.subheader("Applicant Analysis Results")
        
        # Display DataFrame with specified columns
        display_df = df[['ApplicationDate', 'FirstName', 'LastName', 'Position', 'Department', 
                        'Height_cm', 'Weight_kg', 'BMI', 'Score', 'Reason']]
        st.dataframe(display_df, use_container_width=True)
        
        # Display individual applicant cards
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
                    <p><strong>Score:</strong> {row.get('Score', '')}</p>
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
                    st.markdown(f'<a href="{teams_link}" target="_blank"><button>Schedule Teams Meeting</button></a>', 
                              unsafe_allow_html=True)

if __name__ == "__main__":
    main()
