import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.MCQ_Generator.utils import read_file,get_table_data
from src.MCQ_Generator.logger import logging

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
my_llm = ChatOpenAI(openai_api_key = openai_key, model_name = "gpt-3.5-turbo-0125", temperature = 0.3)

Template ="""
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz  of {number} multiple choice questions for {subject} students in {tone} tone. 
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like  RESPONSE_JSON below  and use it as a guide. \
Ensure to make {number} MCQs
### RESPONSE_JSON
{response_json}

"""
QUIZ_Prompt = PromptTemplate(
    input_variables = ["text", "number", "subject", "tone", "response_json"],
    template = Template
)

QUIZ_Chain = LLMChain(
    llm=my_llm,
    prompt=QUIZ_Prompt,
    output_key="quiz", 
    verbose=True
)

Template2 = """
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity analysis. 
if the quiz is not at per with the cognitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the tone such that it perfectly fits the student abilities
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""

QUIZ_Evaluation_Prompt = PromptTemplate(
    input_variables = ["subject", "quiz"],
    template = Template2
)


Review_Chain = LLMChain(
    llm=my_llm,
    prompt=QUIZ_Evaluation_Prompt,
    output_key="review",  
    verbose=True
)


My_chain = SequentialChain(
    chains=[QUIZ_Chain, Review_Chain],
    input_variables=["text", "number", "subject", "tone", "response_json"],  
    output_variables=["quiz", "review"],  
    verbose=True
)