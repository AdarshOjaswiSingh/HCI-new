import streamlit as st
import pandas as pd
import os
import random
from PyPDF2 import PdfReader
from docx import Document

DB_PATH = "End-to-End-AI-driven-pipeline-with-real-time-interview-insights-main/compliance-checker/src/Adarsh_Generated_Candidate_Data.xlsx"
CONVERSATION_HISTORY = []

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
            empty_df = pd.DataFrame(columns=["Role", "Transcript"])
            save_database(empty_df)
            return empty_df
    except Exception as e:
        st.error(f"Failed to load database: {e}")
        return pd.DataFrame()

def save_database(data):
    try:
        data.to_excel(DB_PATH, index=False)
        st.success("Database updated successfully!")
    except Exception as e:
        st.error(f"Failed to save the database: {e}")

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

def upload_data():
    st.header("Upload New Data")
    uploaded_file = st.file_uploader("Upload a file (CSV, XLSX, PDF, DOCX)", type=["csv", "xlsx", "pdf", "docx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                data = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                data = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith(".pdf"):
                text = extract_pdf_text(uploaded_file)
                data = pd.DataFrame([["Unknown", text]], columns=["Role", "Transcript"])
            elif uploaded_file.name.endswith(".docx"):
                text = extract_word_text(uploaded_file)
                data = pd.DataFrame([["Unknown", text]], columns=["Role", "Transcript"])
            else:
                st.error("Unsupported file type!")
                return
            
            if "Role" in data.columns and "Transcript" in data.columns:
                save_database(data)
                st.success("Data uploaded and saved successfully!")
            else:
                st.error("Invalid file format. Ensure the file has 'Role' and 'Transcript' columns.")
        except Exception as e:
            st.error(f"Error processing file: {e}")

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

    elif options == "Interview":
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

    elif options == "Download Final Transcript":
        st.header("Download Interview Transcript")
        if "conversation" in st.session_state and st.session_state.conversation:
            conversation_text = "\n".join([f"{speaker}: {text}" for speaker, text in st.session_state.conversation])
            st.download_button(label="Download Transcript", data=conversation_text, file_name="interview_transcript.txt", mime="text/plain")
        else:
            st.warning("No conversation available to download.")
    
    elif options == "About":
        st.header("About This App")
        st.write("The End-to-End AI-Driven Recruitment Pipeline streamlines hiring by automating key processes like resume screening, skill assessment, and interview analysis. Using NLP, it delivers real-time insights into candidate communication and expertise, while a cultural fit scoring system evaluates alignment with organizational values. This scalable, AI-powered solution ensures faster, data-driven hiring decisions with improved precision.")
        st.write("Author: Adarsh Ojaswi Singh")

if __name__ == "__main__":
    main()
