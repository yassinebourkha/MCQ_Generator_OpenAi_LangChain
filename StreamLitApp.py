import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv

from src.MCQ_Generator.utils import read_file, get_table_data
import streamlit as st
from langchain.callbacks import get_openai_callback
from src.MCQ_Generator.MCQGenerator import My_chain
from src.MCQ_Generator.logger import logging

with open('/workspaces/MCQ_Generator/Response.json') as file:
    RESPONSE_JSON = json.load(file)

st.title("📝 AI-Powered Multiple Choice Question Generator")
st.subheader("Generate custom multiple-choice questions based on uploaded documents using OpenAI and LangChain")
st.markdown("Upload a **PDF** or **TXT** file and provide the necessary information to generate a set of MCQs.")

col1, col2 = st.columns([1, 2])
with st.form("user_inputs"):
    with col1:
        uploaded_file = st.file_uploader("📄 Upload a PDF or txt file", type=["pdf", "txt"], help="Supported formats: PDF, TXT")
    
    with col2:
        st.write("### Options")
        mcq_count = st.number_input("🔢 Number of MCQs", min_value=3, max_value=50, help="Choose the number of MCQs to generate")
        subject = st.text_input("📚 Subject", max_chars=20, help="Provide the subject/topic for the MCQs")
        tone = st.text_input("📊 Complexity Level", max_chars=20, placeholder="Simple", help="Define the complexity level of the questions (e.g., Simple, Intermediate, Advanced)")
    
    # Submit button
    button = st.form_submit_button("🚀 Generate MCQs")

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text = read_file(uploaded_file)
                with get_openai_callback() as cb:
                    response = My_chain(
                        {
                            "text": text,
                            "number": mcq_count,
                            "subject": subject,
                            "tone": tone,
                            "response_json": json.dumps(RESPONSE_JSON)
                        }
                    )
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
            else:
                print(f"Total tokens: {cb.total_tokens}")
                print(f"Prompt tokens: {cb.prompt_tokens}")
                print(f"Completion tokens: {cb.completion_tokens}")
                print(f"Total cost: {cb.total_cost}")
                if isinstance(response, dict):
                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            try:
                                df = pd.DataFrame(table_data)
                                df.index = df.index + 1
                                st.table(df)
                                st.text_area(label="Review", value=response["review"])
                            except ValueError as e:
                                st.error(f"Error creating DataFrame: {e}")
                        else:
                            st.error("Error in the table data")
                    else:
                        st.write(response)
