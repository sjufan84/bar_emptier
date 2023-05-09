import streamlit as st
import pandas as pd
import openai

import os
from dotenv import load_dotenv
load_dotenv()

# Get the OpenAI API key and org key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")

# Define the function to process the file
async def process_file(uploaded_file):
    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith('csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.lower().endswith(('xlsx', 'xls')):
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            else:
                st.error('Invalid file type. Please upload a CSV or Excel file.')
                return

           
            return df
        
        except Exception as e:
            st.error(f'Error processing file: {e}')
            return

# A function to convert the dataframe into a list of tuples containing the spirit and amount
# The first column of the dataframe should be the spirit, and the second column should be the amount
async def create_spirits_list(df):
    spirits_list = []
    for index, row in df.iterrows():
        spirits_list.append((row[0], row[1]))
    return spirits_list