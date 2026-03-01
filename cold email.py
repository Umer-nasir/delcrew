import streamlit as st
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="CrewAI Cold Email Outreach",
    page_icon="📧",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1E3A8A;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #3B82F6;
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2563EB;
    }
    .email-container {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .status-box {
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    .status-running {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        color: #1D4ED8;
    }
    .status-complete {
        background-color: #ECFDF5;
        border: 1px solid #A7F3D0;
        color: #047857;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>📧 CrewAI Cold Email Outreach</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Research target companies, match services, and prepare outreach emails with AI agents.</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🔑 Configuration")
    api_key = st.text_input("Enter your LLM API Key (Gemini, OpenAI, Anthropic, etc)", type="password", help="The system will try to auto-detect the provider based on your key.")
    serper_key = st.text_input("Enter Serper API Key (Optional)", type="password", placeholder="...", help="Used for finding contact persons")
    
    # Auto-detect model based on API Key
    llm_model = ""
    llm_provider = ""
    if api_key:
        if api_key.startswith("AIzaSy"):
            llm_model = "gemini/gemini-2.5-flash"
            llm_provider = "Google Gemini"
        elif api_key.startswith("sk-ant-"):
            llm_model = "anthropic/claude-3-haiku-20240307"
            llm_provider = "Anthropic Claude"
        elif api_key.startswith("sk-proj-") or api_key.startswith("sk-"):
            llm_model = "openai/gpt-4o-mini"
            llm_provider = "OpenAI"
        elif api_key.startswith("gsk_"):
            llm_model = "groq/llama-3.3-70b-versatile"
            llm_provider = "Groq"
        else:
            # Fallback if we can't detect it, default to attempting OpenAI format with whatever standard model, or ask user 
            llm_model = st.text_input("Provider not recognized. Please enter Model format (e.g. openai/gpt-4o):", value="openai/gpt-4o-mini")
            llm_provider = "Custom/Unknown"
            
        if llm_provider != "Custom/Unknown" and llm_provider != "":
            st.success(f"🤖 Auto-detected Provider: **{llm_provider}** (Using model: `{llm_model}`)")

    st.markdown("---")
    st.header("🏢 Your Agency Services")
    agency_services = st.text_area(
        "Describe your services:",
        height=200,
        placeholder="1. AI Automation: We build agents...\n2. UI/UX: We redesign...",
        value=""
    )

    st.markdown("---")
    with st.expander("📧 Optional: SMTP Email Settings"):
        st.info("Fill these to enable sending emails directly from the app.")
        smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
        smtp_port = st.number_input("SMTP Port", value=587)
        smtp_user = st.text_input("SMTP User (Email)")
        smtp_password = st.text_input("SMTP Password", type="password")
        sender_name = st.text_input("Sender Name", value="Agent Outreach")

    st.markdown("---")
    st.subheader("How it works:")
    st.markdown("""
    1. **Researcher**: Analyzes company website.
    2. **Strategist**: Matches needs with services.
    3. **Writer**: Crafts personalized email.
    4. **Outreach**: Finds contact and prepares final version.
    """)

# Main input area
st.markdown("### 🎯 Target Company")
url = st.text_input(
    "Website URL", 
    placeholder="https://example.com",
    help="Enter the URL of the company you want to research"
)

# Initialize session state
if 'result' not in st.session_state:
    st.session_state.result = None
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# Generate button
col1, col2 = st.columns([1, 1])
with col1:
    generate_btn = st.button("🚀 Run Outreach Crew", disabled=st.session_state.is_running or not url or not api_key, type="primary")
with col2:
    clear_btn = st.button("🗑️ Clear Results")

if clear_btn:
    st.session_state.result = None
    st.session_state.is_running = False
    st.rerun()

def send_email(subject, body, to_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{sender_name} <{smtp_user}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return str(e)

# Main processing logic
if generate_btn and url and api_key:
    if not agency_services or agency_services.strip() == "":
        st.error("❌ Error: Please describe your agency services in the sidebar.")
    else:
        st.session_state.is_running = True
        st.session_state.result = None
        
        try:
            # Status indicator
            status_placeholder = st.empty()
            status_placeholder.markdown(
                '<div class="status-box status-running">🤖 Initializing Crew...</div>', 
                unsafe_allow_html=True
            )
            
            # Initialize LLM
            llm = LLM(
                model=llm_model, 
                api_key=api_key
            )
            
            # Tools
            scrape_tool = ScrapeWebsiteTool(url=url)
            search_tool = SerperDevTool(api_key=serper_key) if serper_key else None
            
            # Agents
            researcher = Agent(
                role='Business Intelligence Analyst',
                goal=f'Analyze {url} and identify their core business and potential weaknesses.',
                backstory="Expert at analyzing businesses from their landing page. You look for what they do and where they might be struggling.",
                tools=[scrape_tool],
                verbose=False,
                memory=True,
                llm=llm
            )
            
            strategist = Agent(
                role='Agency Strategist',
                goal='Match the target company needs with ONE of our agency services.',
                backstory=f"""You work for a top-tier digital agency.
                Pick the best service for this client and explain why.
                
                OUR SERVICES:
                {agency_services}""",
                verbose=False,
                memory=True,
                llm=llm
            )
            
            writer = Agent(
                role='Senior Sales Copywriter',
                goal='Write a personalized cold email that sounds human and professional.',
                backstory="You write emails that get replies. You mention specific details found by the Researcher.",
                verbose=False,
                llm=llm
            )
    
            outreach_specialist = Agent(
                role='Email Outreach Specialist',
                goal='Identify the best person to contact (CEO, Founder, or Marketing Head) and finalize the email.',
                backstory="You are great at finding contact persons. You take the draft email and ensure it is addressed to the right person and follows best outreach practices.",
                tools=[search_tool] if search_tool else [],
                verbose=False,
                llm=llm
            )
            
            # Tasks
            task_analyze = Task(
                description=f"Scrape {url}. Summarize what the company does and identify 1 key area for improvement.",
                expected_output="A summary of the company and their potential pain points.",
                agent=researcher
            )
            
            task_strategize = Task(
                description="Based on the analysis, pick ONE service from our services that solves their problem.",
                expected_output="The selected service and reasoning.",
                agent=strategist
            )
            
            task_write = Task(
                description="Draft a personalized cold email pitching the selected service. Keep it under 150 words.",
                expected_output="A professional cold email draft.",
                agent=writer
            )
    
            task_outreach = Task(
                description=f"Find the likely CEO or Marketing Head of {url}. If tools are missing, use general placeholder [CEO NAME]. Finalize the email draft with this information.",
                expected_output="A final email with recipient name and draft.",
                agent=outreach_specialist
            )
            
            # Run Crew
            status_placeholder.markdown('<div class="status-box status-running">🚀 Crew is working on your outreach...</div>', unsafe_allow_html=True)
            
            sales_crew = Crew(
                agents=[researcher, strategist, writer, outreach_specialist],
                tasks=[task_analyze, task_strategize, task_write, task_outreach],
                process=Process.sequential,
                verbose=False,
                llm=llm
            )
            
            result = sales_crew.kickoff()
            
            st.session_state.result = result
            st.session_state.is_running = False
            status_placeholder.markdown('<div class="status-box status-complete">✅ Outreach plan generated!</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.session_state.is_running = False
            status_placeholder.empty()
            st.error(f"❌ Error: {str(e)}")

# Display results
if st.session_state.result:
    st.markdown("---")
    st.subheader("📧 Final Outreach Plan & Email")
    
    result_str = str(st.session_state.result)
    
    st.markdown(f'<div class="email-container">{result_str}</div>', unsafe_allow_html=True)
    
    # Optional Sending
    if smtp_user and smtp_password:
        st.markdown("### 📤 Send this email?")
        target_email = st.text_input("Recipient Email Address", placeholder="ceo@company.com")
        if st.button("✈️ Send Now"):
            send_res = send_email("Enhancing your website experience", result_str, target_email)
            if send_res is True:
                st.success("✅ Email sent successfully!")
            else:
                st.error(f"❌ Failed to send: {send_res}")
    
    st.download_button(
        label="📋 Download Email Text",
        data=result_str,
        file_name="cold_outreach.txt",
        mime="text/plain"
    )

# Footer
st.markdown("---")
st.caption("Powered by Umer Tech| Automated Outreach Suite")
