import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
from docx import Document

DB_PATH = "End-to-End-AI-driven-pipeline-with-real-time-interview-insights-main/compliance-checker/src/subject_books_database.xlsx"

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

def load_database():
    try:
        if os.path.exists(DB_PATH):
            df = pd.read_excel(DB_PATH)
            df.columns = df.columns.str.strip()
            required_columns = ["Summary", "Important Questions"]
            if not all(col in df.columns for col in required_columns):
                st.error("Database format is incorrect. Ensure it has 'Summary' and 'Important Questions' columns.")
                return pd.DataFrame(columns=required_columns)
            return df
        else:
            st.warning("Database not found! Initializing a new database.")
            return pd.DataFrame(columns=["Summary", "Important Questions"])
    except Exception as e:
        st.error(f"Failed to load database: {e}")
        return pd.DataFrame()

def main():
    st.title("The Adaptive Learning Platform for Dyslexic Students!")
    
    st.sidebar.header("Navigation")
    options = st.sidebar.radio("Select a page:", ["Home", "Data Upload", "Study Mode", "Download Study Material", "About"])

    if options == "Home":
        st.header("Welcome to the HCI Project Dashboard")
        st.write("This app is designed to showcase the key features and outputs of my project.")
        st.write("Use the sidebar to navigate through the app.")

    elif options == "About":
        st.header("About This App")
        st.write("An AI-powered adaptive learning platform designed to personalize education for dyslexic students.")
        st.write("Author: Adarsh Ojaswi Singh")

    elif options == "Data Upload":
        st.header("Upload Book for Summary")
        uploaded_file = st.file_uploader("Upload a file (PDF, DOCX, or Excel)", type=["pdf", "docx", "xlsx"])
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith(".pdf"):
                    text = extract_pdf_text(uploaded_file)
                    st.session_state.book_summary = text
                    st.subheader("Extracted Book Summary")
                    st.write(text)

                elif uploaded_file.name.endswith(".docx"):
                    text = extract_word_text(uploaded_file)
                    st.session_state.book_summary = text
                    st.subheader("Extracted Book Summary")
                    st.write(text)
                    
                elif uploaded_file.name.endswith(".xlsx"):
                    df = pd.read_excel(uploaded_file)
                    st.write("Data loaded successfully! Here is a preview of the first few rows:")
                    st.dataframe(df.head())
                else:
                    st.error("Unsupported file type!")
                    return
            except Exception as e:
                st.error(f"Error processing file: {e}")

    elif options == "Study Mode":
        st.header("Study Mode")
        database = load_database()
        if database.empty:
            st.warning("No data available in the database.")
        else:
            summaries = database["Summary"].dropna().unique().tolist()
            selected_summary = st.selectbox("Select a summary to study:", summaries)
            
            if st.button("Start Study Session"):
                st.session_state.study_session = selected_summary
                st.session_state.questions = database[database["Summary"] == selected_summary]["Important Questions"].dropna().tolist()
                st.session_state.current_question = st.session_state.questions.pop(0) if st.session_state.questions else None
                st.session_state.conversation = [("System", f"Studying: {selected_summary}")]

            if "current_question" in st.session_state and st.session_state.current_question:
                st.write(f"**Question:** {st.session_state.current_question}")
                answer = st.text_area("Your Answer:")
                if st.button("Submit Answer"):
                    if answer.strip():
                        st.session_state.conversation.append(("User", answer))
                        if st.session_state.questions:
                            st.session_state.current_question = st.session_state.questions.pop(0)
                        else:
                            st.success("Study session completed!")
                    else:
                        st.warning("Please provide an answer before submitting.")

    elif options == "Download Study Material":
        st.header("Download Study Material")
        if "conversation" in st.session_state and st.session_state.conversation:
            study_text = "\n".join([f"{speaker}: {text}" for speaker, text in st.session_state.conversation])
            st.download_button(label="Download Study Session", data=study_text, file_name="study_session.txt", mime="text/plain")
        else:
            st.warning("No study session available to download.")

if __name__ == "__main__":
    main()
