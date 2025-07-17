import streamlit as st
import pandas as pd
import requests
import re
from urllib.parse import quote
import math

# Page configuration
st.set_page_config(
    page_title="Evalia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Apple-inspired design
st.markdown("""
<style>
    /* Import Apple-style font */
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #ffffff;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header */
    .main-header {
        background: linear-gradient(135deg, #007BFF 0%, #0056b3 100%);
        padding: 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(0, 123, 255, 0.15);
    }
    
    .main-title {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .main-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2rem;
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Input section */
    .input-section {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 2px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
        border: 1px solid rgba(0, 123, 255, 0.1);
    }
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(135deg, #007BFF 0%, #0056b3 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(0, 123, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.4);
    }
    
    /* Applicant cards */
    .applicant-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0, 123, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .applicant-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.1);
    }
    
    .level-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .level-high { background-color: #d4edda; color: #155724; }
    .level-mid { background-color: #fff3cd; color: #856404; }
    .level-low { background-color: #f8d7da; color: #721c24; }
    
    .action-buttons {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .action-btn {
        flex: 1;
        padding: 0.6rem 1rem;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        text-decoration: none;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .email-btn {
        background-color: #007BFF;
        color: white;
    }
    
    .email-btn:hover {
        background-color: #0056b3;
        transform: translateY(-1px);
    }
    
    .teams-btn {
        background-color: #6264A7;
        color: white;
    }
    
    .teams-btn:hover {
        background-color: #4B4D8C;
        transform: translateY(-1px);
    }
    
    /* Stats section */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 123, 255, 0.1);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #007BFF;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #666;
        font-size: 0.9rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def calculate_bmi(weight, height_cm):
    """Calculate BMI from weight (kg) and height (cm)"""
    if weight and height_cm:
        height_m = height_cm / 100
        return weight / (height_m ** 2)
    return None

def analyze_experience(experience_years, experience_desc):
    """Simple rule-based experience analysis"""
    score = 0
    reasons = []
    
    # Years of experience scoring
    if experience_years >= 5:
        score += 3
        reasons.append(f"Extensive experience ({experience_years} years)")
    elif experience_years >= 3:
        score += 2
        reasons.append(f"Good experience ({experience_years} years)")
    elif experience_years >= 1:
        score += 1
        reasons.append(f"Some experience ({experience_years} years)")
    else:
        reasons.append("Limited experience")
    
    # Experience description analysis (simple keyword matching)
    if experience_desc:
        desc_lower = experience_desc.lower()
        keywords = {
            'leadership': 1, 'management': 1, 'senior': 1, 'lead': 1,
            'project': 0.5, 'team': 0.5, 'strategic': 1, 'innovative': 0.5,
            'certified': 0.5, 'expert': 1, 'advanced': 0.5, 'skilled': 0.5
        }
        
        for keyword, weight in keywords.items():
            if keyword in desc_lower:
                score += weight
                if weight >= 1:
                    reasons.append(f"Strong {keyword} background")
    
    # Determine level based on score
    if score >= 4:
        level = "High"
    elif score >= 2:
        level = "Mid"
    else:
        level = "Low"
    
    return level, ", ".join(reasons) if reasons else "Basic qualifications"

def create_email_link(name, email, level):
    """Create mailto link with pre-filled content"""
    subject = f"Application Status - {name}"
    body = f"""Dear {name},

Thank you for your application. After reviewing your profile, we have assessed your application as {level} priority.

We will be in touch soon regarding next steps.

Best regards,
Recruitment Team"""
    
    mailto_link = f"mailto:{email}?subject={quote(subject)}&body={quote(body)}"
    return mailto_link

def create_teams_link(name, email):
    """Create Teams meeting scheduler link"""
    # This would typically integrate with Microsoft Graph API
    # For now, we'll create a generic Teams link
    return f"https://teams.microsoft.com/l/meeting/new?subject=Interview%20with%20{quote(name)}&attendees={quote(email)}"

def process_excel_data(df):
    """Process the Excel data and analyze applicants"""
    processed_applicants = []
    
    for index, row in df.iterrows():
        # Extract basic info
        name = row.get('Name', f'Applicant {index + 1}')
        email = row.get('Email', '')
        weight = row.get('Weight (kg)', None)
        height = row.get('Height (cm)', None)
        experience_years = row.get('Experience Years', 0)
        experience_desc = row.get('Experience Description', '')
        
        # Calculate BMI
        bmi = calculate_bmi(weight, height)
        
        # Determine level based on BMI first
        if bmi and bmi > 25:
            level = "Low"
            reason = f"BMI {bmi:.1f} exceeds threshold (>25)"
        else:
            # Use experience analysis
            level, reason = analyze_experience(experience_years, experience_desc)
            if bmi:
                reason = f"BMI {bmi:.1f} (acceptable), {reason}"
        
        processed_applicants.append({
            'name': name,
            'email': email,
            'weight': weight,
            'height': height,
            'bmi': bmi,
            'experience_years': experience_years,
            'experience_desc': experience_desc,
            'level': level,
            'reason': reason
        })
    
    return processed_applicants

# Main app
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">Evalia</h1>
        <p class="main-subtitle">AI-Powered Applicant Analysis & Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input section
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.subheader("📊 Excel Data Input")
    
    excel_link = st.text_input(
        "Paste your Microsoft Excel Online link here:",
        placeholder="https://bdmsgroup-my.sharepoint.com/:x:/g/personal/...",
        help="Paste the SharePoint/OneDrive Excel link to analyze applicant data"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_button = st.button("🔍 Fetch & Analyze", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sample data for demonstration (since we can't access the actual SharePoint link)
    if analyze_button and excel_link:
        st.info("Note: This is a demo with sample data. In production, this would fetch data from your Excel link.")
        
        # Sample data
        sample_data = {
            'Name': ['John Smith', 'Sarah Johnson', 'Mike Chen', 'Emily Brown', 'David Wilson'],
            'Email': ['john.smith@email.com', 'sarah.j@email.com', 'mike.chen@email.com', 'emily.brown@email.com', 'david.wilson@email.com'],
            'Weight (kg)': [75, 68, 85, 62, 90],
            'Height (cm)': [175, 165, 180, 158, 175],
            'Experience Years': [3, 7, 2, 5, 8],
            'Experience Description': [
                'Junior developer with React experience',
                'Senior manager with team leadership and strategic planning',
                'Recent graduate with internship experience',
                'Project lead with certified scrum master background',
                'Expert consultant with advanced technical skills and management'
            ]
        }
        
        df = pd.DataFrame(sample_data)
        
        # Process the data
        applicants = process_excel_data(df)
        
        # Display statistics
        st.subheader("📈 Analysis Summary")
        
        total_applicants = len(applicants)
        high_level = len([a for a in applicants if a['level'] == 'High'])
        mid_level = len([a for a in applicants if a['level'] == 'Mid'])
        low_level = len([a for a in applicants if a['level'] == 'Low'])
        
        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-number">{total_applicants}</div>
                <div class="stat-label">Total Applicants</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{high_level}</div>
                <div class="stat-label">High Priority</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{mid_level}</div>
                <div class="stat-label">Mid Priority</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{low_level}</div>
                <div class="stat-label">Low Priority</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display applicants
        st.subheader("👥 Applicant Analysis")
        
        for applicant in applicants:
            level_class = f"level-{applicant['level'].lower()}"
            
            st.markdown(f"""
            <div class="applicant-card">
                <h3>{applicant['name']} <span class="level-badge {level_class}">{applicant['level']} Priority</span></h3>
                <p><strong>Email:</strong> {applicant['email']}</p>
                <p><strong>BMI:</strong> {applicant['bmi']:.1f if applicant['bmi'] else 'N/A'} | 
                   <strong>Experience:</strong> {applicant['experience_years']} years</p>
                <p><strong>Analysis:</strong> {applicant['reason']}</p>
                
                <div class="action-buttons">
                    <a href="{create_email_link(applicant['name'], applicant['email'], applicant['level'])}" 
                       class="action-btn email-btn" target="_blank">
                        📧 Send Email
                    </a>
                    <a href="{create_teams_link(applicant['name'], applicant['email'])}" 
                       class="action-btn teams-btn" target="_blank">
                        📅 Schedule Interview
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    elif analyze_button:
        st.warning("Please paste an Excel link to analyze applicant data.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Evalia - Streamlining your recruitment process with AI-powered insights</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
