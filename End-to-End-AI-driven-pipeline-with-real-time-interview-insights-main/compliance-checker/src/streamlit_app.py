import streamlit as st
import pandas as pd
import os
import random
from PyPDF2 import PdfReader
from docx import Document

DB_PATH = "End-to-End-AI-driven-pipeline-with-real-time-interview-insights-main/compliance-checker/src/Adarsh_Generated_Candidate_Data.xlsx"

def extract_pdf_text(file):
    try:
        reader = PdfReader(file)
        return '\n'.join([page.extract_text() for page in reader.pages if page.extract_text()])
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def extract_word_text(file):
    try:
        doc = Document(file)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error reading Word document: {e}")
        return ""

def extract_resume_details(text):
    """Extracts only Skills, Achievements, Experiences, and Projects."""
    lines = text.split("\n")
    summary_sections = ["Skills", "Achievements", "Experience", "Projects"]
    extracted_info = {section: [] for section in summary_sections}

    current_section = None
    for line in lines:
        line = line.strip()
        if any(line.lower().startswith(sec.lower()) for sec in summary_sections):
            current_section = line
        elif current_section:
            extracted_info[current_section].append(line)

    return {key: "\n".join(value) for key, value in extracted_info.items() if value}

def upload_data():
    st.header("Upload Resume for Summary")
    uploaded_file = st.file_uploader("Upload a file (PDF, DOCX)", type=["pdf", "docx"])
    if uploaded_file:
        try:
            text = extract_pdf_text(uploaded_file) if uploaded_file.name.endswith(".pdf") else extract_word_text(uploaded_file)
            summary = extract_resume_details(text)
            
            st.subheader("Resume Summary")
            for section, content in summary.items():
                st.write(f"**{section}**")
                st.write(content)
            
            # Store summary in session for download
            st.session_state.resume_summary = summary
        except Exception as e:
            st.error(f"Error processing file: {e}")

def load_database():
    try:
        if os.path.exists(DB_PATH):
            df = pd.read_excel(DB_PATH)
            df.columns = df.columns.str.strip()
            required_columns = ["Role", "Transcript"]
            if not all(col in df.columns for col in required_columns):
                st.error("Database format is incorrect. Ensure it has 'Role' and 'Transcript' columns.")
                return pd.DataFrame(columns=required_columns)
            return df
        else:
            st.warning("Database not found! Initializing a new database.")
            return pd.DataFrame(columns=["Role", "Transcript"])
    except Exception as e:
        st.error(f"Failed to load database: {e}")
        return pd.DataFrame()

def main():
    st.title("End-to-End AI-Driven Recruitment Pipeline with Real-Time Insights")
    st.sidebar.header("Navigation")
    options = st.sidebar.radio("Select a page:", ["Home", "Data Upload", "Database", "Interview Mode", "Download Conversation", "About"])

    if options == "Home":
        st.header("Welcome to the Infosys Project Dashboard")
        st.write("This app is designed to showcase the key features and outputs of my project.")
        st.write("Use the sidebar to navigate through the app.")

    elif options == "Data Upload":
        upload_data()
    
    elif options == "Database":
        st.header("Permanent Database")
        database = load_database()
        st.dataframe(database)

    elif options == "Interview Mode":
        st.header("Interview Mode: Conversational Format")
        database = load_database()
        roles = database["Role"].dropna().unique().tolist() if not database.empty else []
        if not roles:
            roles = ["No roles available"]
        role = st.selectbox("Select the role you are applying for:", roles)
        
        if st.button("Start Interview"):
            if role and role != "No roles available":
                st.session_state.role = role
                st.session_state.conversation = []
                st.session_state.transcripts = database[database["Role"] == role]["Transcript"].dropna().tolist()
                if st.session_state.transcripts:
                    st.session_state.current_question = st.session_state.transcripts.pop(0)
                    st.session_state.conversation.append(("Interviewer", st.session_state.current_question))

        if "current_question" in st.session_state:
            st.write(f"**Interviewer:** {st.session_state.current_question}")
            answer = st.text_area("Your Response:")
            if st.button("Submit Answer"):
                if answer.strip():
                    st.session_state.conversation.append(("Candidate", answer))
                    if st.session_state.transcripts:
                        st.session_state.current_question = st.session_state.transcripts.pop(0)
                        st.session_state.conversation.append(("Interviewer", st.session_state.current_question))
                    else:
                        st.success("Interview completed!")
                else:
                    st.warning("Please provide an answer before submitting.")

    elif options == "Download Conversation":
        st.header("Download Interview Transcript")

        # Prepare interview transcript
        conversation_text = "\n".join([f"{speaker}: {text}" for speaker, text in st.session_state.get("conversation", [])])
        
        # Prepare resume summary if available
        resume_summary = st.session_state.get("resume_summary", {})
        resume_text = "\n\n".join([f"**{key}**:\n{value}" for key, value in resume_summary.items()])

        # Combine interview transcript and resume summary
        full_text = f"### Resume Summary:\n{resume_text}\n\n### Interview Transcript:\n{conversation_text}" if resume_summary else f"### Interview Transcript:\n{conversation_text}"
        
        if full_text.strip():
            st.download_button(label="Download Full Report", data=full_text, file_name="recruitment_report.txt", mime="text/plain")
        else:
            st.warning("No data available to download.")

    elif options == "About":
        st.header("About This App")
        st.write("The End-to-End AI-Driven Recruitment Pipeline streamlines hiring by automating key processes like resume screening, skill assessment, and interview analysis. Using NLP, it delivers real-time insights into candidate communication and expertise, while a cultural fit scoring system evaluates alignment with organizational values. This scalable, AI-powered solution ensures faster, data-driven hiring decisions with improved precision.")
        st.write("Author: Adarsh Ojaswi Singh")

if __name__ == "__main__":
    main()
