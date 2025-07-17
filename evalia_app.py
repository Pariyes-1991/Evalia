import streamlit as st
import pandas as pd
import io
import requests
import re

# Custom CSS for Apple-inspired design
st.markdown("""
<style>
    .main {
        background-color: #f5f5f7;
        padding: 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .stButton>button {
        background-color: #0071e3;
        color: white;
        border-radius: 18px;
        padding: 10px 20px;
        border: none;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #005bb5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #d2d2d7;
        padding: 10px;
        font-size: 16px;
    }
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #1d1d1f;
        font-weight: 600;
    }
    .applicant-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Function to extract Excel data from OneDrive/SharePoint link
def fetch_excel_data(link):
    try:
        # Convert sharing link to direct download link
        download_url = link.replace("sharepoint.com/:x:/", "sharepoint.com/personal/")
        download_url = re.sub(r"(\?s=.*)$", "?download=1", download_url)
        
        response = requests.get(download_url)
        response.raise_for_status()
        
        # Read Excel data
        excel_data = io.BytesIO(response.content)
        df = pd.read_excel(excel_data)
        return df
    except Exception as e:
        st.error(f"Error fetching Excel data: {str(e)}")
        return None

# Function to calculate BMI and assign level
def analyze_applicant(row):
    try:
        # Calculate BMI (assuming weight in kg, height in meters)
        weight = float(row.get('Weight_kg', 0))
        height = float(row.get('Height_m', 0))
        bmi = weight / (height ** 2) if height > 0 else 0
        
        # Rule-based logic for level assignment
        if bmi > 25:
            return "Low"
        
        # Experience-based scoring
        experience_years = float(row.get('Experience_Years', 0))
        if experience_years >= 5:
            return "High"
        elif experience_years >= 2:
            return "Mid"
        else:
            return "Low"
    except:
        return "Low"

# Main app
def main():
    st.title("Evalia")
    st.subheader("Applicant Analysis Platform")
    
    # Input for Excel link
    excel_link = st.text_input("Paste Microsoft Excel Online (OneDrive/SharePoint) Link", 
                             placeholder="https://1drv.ms/x/s!...")

    if st.button("Fetch & Analyze"):
        if excel_link:
            with st.spinner("Fetching and analyzing data..."):
                df = fetch_excel_data(excel_link)
                if df is not None:
                    # Analyze applicants
                    df['Level'] = df.apply(analyze_applicant, axis=1)
                    st.session_state['applicants'] = df
        else:
            st.error("Please provide a valid Excel link")

    # Display results
    if 'applicants' in st.session_state:
        df = st.session_state['applicants']
        st.subheader("Applicant Analysis Results")
        
        # Display DataFrame
        st.dataframe(df, use_container_width=True)
        
        # Display individual applicant cards
        for index, row in df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="applicant-card">
                    <h3>{row.get('Name', 'Applicant ' + str(index + 1))}</h3>
                    <p><strong>Level:</strong> {row['Level']}</p>
                    <p><strong>Experience:</strong> {row.get('Experience_Years', 0)} years</p>
                    <p><strong>BMI:</strong> {row.get('Weight_kg', 0) / (row.get('Height_m', 1) ** 2):.1f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    email = row.get('Email', 'applicant@example.com')
                    subject = f"Evalia: Application Review - {row.get('Name', 'Applicant')}"
                    body = f"Dear {row.get('Name', 'Applicant')},\n\nThank you for your application..."
                    mailto_link = f"mailto:{email}?subject={subject}&body={body}"
                    st.markdown(f'<a href="{mailto_link}" target="_blank"><button>Send Email</button></a>', 
                              unsafe_allow_html=True)
                
                with col2:
                    teams_link = "https://teams.microsoft.com/l/meeting/new"
                    st.markdown(f'<a href="{teams_link}" target="_blank"><button>Schedule Interview</button></a>', 
                              unsafe_allow_html=True)

if __name__ == "__main__":
    main()