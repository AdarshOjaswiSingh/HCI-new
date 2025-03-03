import streamlit as st
import pandas as pd
import os
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
    
    summary_sections = {
        "Skills": ["Skills", "Technical Skills", "Core Competencies"],
        "Achievements": ["Achievements", "Accomplishments", "Key Highlights"],
        "Experience": ["Experience", "Work Experience", "Professional Experience"],
        "Projects": ["Projects", "Key Projects", "Academic Projects"]
    }
    
    extracted_info = {key: [] for key in summary_sections}
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        for section, keywords in summary_sections.items():
            if any(line.lower().startswith(keyword.lower()) for keyword in keywords):
                current_section = section
                break
        else:
            if current_section:
                extracted_info[current_section].append(line)
    
    formatted_output = {key: "\n".join(value) for key, value in extracted_info.items() if value}
    
    if not formatted_output:
        return "No structured data found. Please ensure your resume has clearly labeled sections."
    
    return formatted_output

def upload_data():
    st.header("Upload Resume for Summary")
    uploaded_file = st.file_uploader("Upload a file (PDF, DOCX, or Excel)", type=["pdf", "docx", "xlsx"])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".pdf"):
                text = extract_pdf_text(uploaded_file)
                summary = extract_resume_details(text)
                st.session_state.resume_summary = summary
                st.subheader("Resume Summary")
                st.write(summary)

            elif uploaded_file.name.endswith(".docx"):
                text = extract_word_text(uploaded_file)
                summary = extract_resume_details(text)
                st.session_state.resume_summary = summary
                st.subheader("Resume Summary")
                st.write(summary)
                
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
                st.write("Data loaded successfully! Here is a preview of the first few rows:")
                st.dataframe(df.head())  # Display first 5 rows of the uploaded Excel file
                
                # Display some statistics about the data
                st.write("Data Overview:")
                st.write(f"Total rows: {len(df)}")
                st.write(f"Columns: {', '.join(df.columns)}")
                
                st.write("Note: You can also upload resumes (PDF or DOCX) for further analysis.")
                
            else:
                st.error("Unsupported file type!")
                return

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
    # Initialize session state for the first time
    if "resume_summary" not in st.session_state:
        st.session_state.resume_summary = None

    st.title("End-to-End AI-Driven Recruitment Pipeline with Real-Time Insights")
    
    # Sidebar navigation
    st.sidebar.header("Navigation")
    options = st.sidebar.radio("Select a page:", ["Home", "Data Upload", "Download Conversation", "About"])

    if options == "Home":
        st.header("Welcome to the Infosys Project Dashboard")
        st.write("This app is designed to showcase the key features and outputs of my project.")
        st.write("Use the sidebar to navigate through the app.")

    elif options == "About":
        st.header("About This App")
        st.write("The End-to-End AI-Driven Recruitment Pipeline streamlines hiring by automating key processes like resume screening, skill assessment, and interview analysis.")
        st.write("Author: Adarsh Ojaswi Singh")

    elif options == "Data Upload":
        # Data Upload section
        st.header("Upload Resume for Summary")
        uploaded_file = st.file_uploader("Upload a file (PDF, DOCX, or Excel)", type=["pdf", "docx", "xlsx"])
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith(".pdf"):
                    text = extract_pdf_text(uploaded_file)
                    summary = extract_resume_details(text)
                    st.session_state.resume_summary = summary
                    st.subheader("Resume Summary")
                    st.write(summary)

                elif uploaded_file.name.endswith(".docx"):
                    text = extract_word_text(uploaded_file)
                    summary = extract_resume_details(text)
                    st.session_state.resume_summary = summary
                    st.subheader("Resume Summary")
                    st.write(summary)

                elif uploaded_file.name.endswith(".xlsx"):
                    df = pd.read_excel(uploaded_file)
                    st.write("Data loaded successfully! Here is a preview of the first few rows:")
                    st.dataframe(df.head())  # Display first 5 rows of the uploaded Excel file
                    
                    # Display some statistics about the data
                    st.write("Data Overview:")
                    st.write(f"Total rows: {len(df)}")
                    st.write(f"Columns: {', '.join(df.columns)}")
                    
                    st.write("Note: You can also upload resumes (PDF or DOCX) for further analysis.")
                    
                else:
                    st.error("Unsupported file type!")
                    return

            except Exception as e:
                st.error(f"Error processing file: {e}")

    elif options == "Download Conversation":
        st.header("Download Interview Transcript and Resume Summary")
        if "resume_summary" in st.session_state and st.session_state.resume_summary:
            resume_summary_text = ""
            if isinstance(st.session_state.resume_summary, dict):
                # Convert the dictionary to a string format
                for section, content in st.session_state.resume_summary.items():
                    resume_summary_text += f"{section}:\n{content}\n\n"
            else:
                resume_summary_text = str(st.session_state.resume_summary)
            
            # Button for downloading the resume summary
            st.download_button(label="Download Resume Summary Only", 
                               data=resume_summary_text, 
                               file_name="resume_summary.txt", 
                               mime="text/plain")

        else:
            st.warning("No resume summary available to download.")

if __name__ == "__main__":
    main()
