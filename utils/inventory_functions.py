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
def process_file(uploaded_file):
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
    for row in df.iterrows():
        spirits_list.append((row[0], row[1]))
    return spirits_list

# Here we want to access the newly created dataframe and run calculations for Cost per ml,Cost per oz,Total Amount (ml),Total Amount (oz),Total Value.  This will 
# involve running the calculations on the dataframe and then returning the dataframe with the new columns added.
def format_inventory(df):
    # Divide the total cost by the total amount to get the cost per ml
    df['Cost per ml'] = df['Total Cost'] / df['Total Amount (ml)']
    # Convert the cost per ml to cost per oz
    df['Cost per oz'] = df['Cost per ml'] * 0.033814
    # Calculate the total value of the inventory
    df['Total Value'] = df['Total Amount (ml)'] * df['Cost per ml']

    # Return the dataframe with the new columns
    return df