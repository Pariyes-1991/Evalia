import streamlit as st
import pandas as pd
import requests
import io
from urllib.parse import quote

# Custom CSS for Apple-inspired design
st.markdown("""
<style>
    .main {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton > button {
        background-color: #007BFF;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #0056b3;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    .stTextInput > div > input, .stFileUploader > div > input, .stSelectbox > div > select {
        border-radius: 8px;
        border: 1px solid #007BFF;
        padding: 10px;
    }
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        color: #333;
    }
    .applicant-card {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Function to fetch Excel data from OneDrive/SharePoint link
def fetch_excel_data(link):
    try:
        # Convert sharing link to direct download link
        download_url = link.replace("/personal/", "/guestaccess.aspx?docid=").replace("/g/", "/r/")
        response = requests.get(download_url, allow_redirects=True)
        if response.status_code == 200:
            df = pd.read_excel(io.BytesIO(response.content))
            return df
        else:
            st.error(f"Failed to fetch Excel file. Status code: {response.status_code}. Ensure the link is publicly accessible.")
            return None
    except Exception as e:
        st.error(f"Error fetching Excel data: {str(e)}. Please check the link or file permissions.")
        return None

# Function to read uploaded Excel file
def read_uploaded_excel(file):
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"Error reading uploaded Excel file: {str(e)}. Ensure the file is a valid Excel format.")
        return None

# Function to analyze applicants
def analyze_applicants(df, name_col, bmi_col, years_col, desc_col, email_col):
    results = []
    for index, row in df.iterrows():
        # BMI Analysis
        bmi = float(row.get(bmi_col, 0))
        level = "Low" if bmi > 25 else "High"  # Default to High if BMI <= 25

        # Experience Analysis (rule-based)
        years = float(row.get(years_col, 0))
        description = str(row.get(desc_col, ''))

        # Simple rule-based scoring
        experience_score = 0
        if years > 5:
            experience_score += 50
        elif years > 2:
            experience_score += 30
        else:
            experience_score += 10

        # Keyword-based scoring for description
        keywords = ['leadership', 'management', 'project', 'team', 'development']
        description_score = sum(10 for keyword in keywords if keyword.lower() in description.lower())
        total_score = experience_score + description_score

        # Adjust level based on experience score
        if total_score < 30:
            level = "Low"
            reason = f"Low experience score ({total_score}): Limited years ({years}) and few relevant keywords in description."
        elif total_score < 60:
            level = "Mid"
            reason = f"Moderate experience score ({total_score}): {years} years with some relevant experience."
        else:
            level = "High"
            reason = f"High experience score ({total_score}): {years} years with strong relevant experience."

        # Prepare action buttons
        email = row.get(email_col, '')
        name = row.get(name_col, 'Applicant')
        email_subject = quote(f"Application Review for {name}")
        email_body = quote(f"Dear {name},\n\nWe have reviewed your application. Your assigned level is {level}.\nReason: {reason}\n\nBest regards,\nEvalia Team")
        email_link = f"mailto:{email}?subject={email_subject}&body={email_body}"
        
        teams_link = "https://teams.microsoft.com/l/meeting/new"

        results.append({
            'Name': name,
            'Level': level,
            'Reason': reason,
            'Email_Link': email_link,
            'Teams_Link': teams_link
        })
    
    return results

# Streamlit app layout
st.title("Evalia - Applicant Evaluation")
st.markdown("A clean, modern applicant analysis tool.")

# Input options
st.subheader("Provide Excel Data")
input_method = st.radio("Choose input method:", ("Paste SharePoint/OneDrive Link", "Upload Excel File"))

df = None
if input_method == "Paste SharePoint/OneDrive Link":
    excel_link = st.text_input("Paste Microsoft Excel Online (OneDrive/SharePoint) Link", 
                             value="https://bdmsgroup-my.sharepoint.com/:x:/g/personal/recruitment_bdms_co_th/EemR4Mg1E_pFr41PR8vBKPEB2GM_vy3iSfXv6BqWKQE58A?e=6z7iNg")
    if st.button("Fetch & Analyze"):
        if excel_link:
            with st.spinner("Fetching and analyzing data..."):
                df = fetch_excel_data(excel_link)
else:
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
    if uploaded_file and st.button("Analyze Uploaded File"):
        with st.spinner("Reading and analyzing uploaded file..."):
            df = read_uploaded_excel(uploaded_file)

# Process and display results if data is available
if df is not None:
    # Display available columns
    available_columns = df.columns.tolist()
    st.subheader("Column Mapping")
    st.write("The Excel file contains the following columns:")
    st.write(available_columns)
    st.write("Please map the columns to the required fields below:")

    # Column mapping interface
    name_col = st.selectbox("Select column for Name", [""] + available_columns)
    bmi_col = st.selectbox("Select column for BMI", [""] + available_columns)
    years_col = st.selectbox("Select column for Years of Experience", [""] + available_columns)
    desc_col = st.selectbox("Select column for Experience Description", [""] + available_columns)
    email_col = st.selectbox("Select column for Email", [""] + available_columns)

    if st.button("Analyze with Selected Columns"):
        if all([name_col, bmi_col, years_col, desc_col, email_col]):
            if len(set([name_col, bmi_col, years_col, desc_col, email_col])) == 5:  # Ensure unique columns
                results = analyze_applicants(df, name_col, bmi_col, years_col, desc_col, email_col)
                if results:
                    st.subheader("Applicant Analysis Results")
                    for applicant in results:
                        st.markdown(f"""
                        <div class="applicant-card">
                            <h3>{applicant['Name']}</h3>
                            <p><strong>Level:</strong> {applicant['Level']}</p>
                            <p><strong>Reason:</strong> {applicant['Reason']}</p>
                            <a href="{applicant['Email_Link']}" target="_blank"><button>Send Email</button></a>
                            <a href="{applicant['Teams_Link']}" target="_blank"><button>Schedule Interview</button></a>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("Please select unique columns for each field.")
        else:
            st.error("Please select a column for each required field.")

# Add some padding at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)
