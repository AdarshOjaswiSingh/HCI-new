import streamlit as st
import pandas as pd
import os
import random

DB_PATH = "End-to-End-AI-driven-pipeline-with-real-time-interview-insights-main/compliance-checker/src/Adarsh_Generated_Candidate_Data.xlsx"

def load_database():
    try:
        if os.path.exists(DB_PATH):
            df = pd.read_excel(DB_PATH)
            required_columns = ["Role", "Question"]
            if not all(col in df.columns for col in required_columns):
                st.error("Database format is incorrect. Ensure it has 'Role' and 'Question' columns.")
                return pd.DataFrame(columns=required_columns)
            return df
        else:
            st.warning("Database not found! Initializing a new database.")
            empty_df = pd.DataFrame(columns=["Role", "Question"])  # Ensure correct format
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

def ask_question(role):
    try:
        database = load_database()
        if not database.empty:
            questions = database[database["Role"] == role]["Question"].dropna().tolist()
            if questions:
                return random.choice(questions)
            else:
                return "No questions available for this role."
        else:
            return "Database is empty or incorrectly formatted."
    except Exception as e:
        st.error(f"Error fetching question: {e}")
        return ""

def main():
    st.title("Contract Analysis System")
    st.sidebar.header("Navigation")
    options = st.sidebar.radio("Select a page:", ["Home", "Data Upload", "Database", "Interview Mode", "About"])

    if options == "Home":
        st.header("Welcome to the Infosys Project Dashboard")
        st.write("This app is designed to showcase the key features and outputs of my project.")
        st.write("Use the sidebar to navigate through the app.")

    elif options == "Database":
        st.header("Permanent Database")
        database = load_database()
        st.dataframe(database)

    elif options == "Interview Mode":
        st.header("Interview Question Mode")
        database = load_database()
        roles = database["Role"].dropna().unique().tolist()
        if not roles:
            roles = ["No roles available"]
        role = st.selectbox("Select the role you are applying for:", roles)
        
        if st.button("Start Interview"):
            if role and role != "No roles available":
                question = ask_question(role)
                st.session_state.question = question
        
        if "question" in st.session_state:
            st.write(f"**Question:** {st.session_state.question}")
            answer = st.text_area("Your Answer:")
            if st.button("Submit Answer"):
                if answer.strip():
                    st.success("Answer submitted successfully!")
                else:
                    st.warning("Please provide an answer before submitting.")

    elif options == "About":
        st.header("About This App")
        st.write("The End-to-End AI-Driven Recruitment Pipeline streamlines hiring by automating key processes like resume screening, skill assessment, and interview analysis. Using NLP, it delivers real-time insights into candidate communication and expertise, while a cultural fit scoring system evaluates alignment with organizational values. This scalable, AI-powered solution ensures faster, data-driven hiring decisions with improved precision.")
        st.write("Author: Adarsh Ojaswi Singh")

if __name__ == "__main__":
    main()
