# This is a page to allow the user to upload their bar inventory to be used in the cocktail creation process

# Initial imports
import streamlit as st
from utils.inventory_functions import process_file, create_spirits_list
import openai
import pandas as pd
import os
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
import asyncio
load_dotenv()

# Get the OpenAI API key and org key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")



# Initialize the session state
def init_inventory_session_variables():
    # Initialize session state variables
    session_vars = [
        'inventory_page', 'inventory_csv_data', 'df', 'inventory_list'
    ]
    default_values = [
        'upload_inventory', [], pd.DataFrame(), []
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

init_inventory_session_variables()

async def upload_inventory():
    # Set the page title
    st.markdown('''
    <div style = text-align:center>
    <h3 style = "color: black;">Upload your inventory</h3>
    <h5 style = "color: #7b3583;">The first column of your file should contain the name of the spirit\
        and the second column should contain the quantity of that spirit that you have in stock.\
        By uploading your inventory, you are allowing the model to prioritize using up ingredients you already have on hand when suggesting cocktails.</h5>
    </div>
    ''', unsafe_allow_html=True)
    # Create a file uploader
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx', 'xls'])
    upload_file_button = st.button('Upload File and Continue to Cocktail Creation', use_container_width=True, type = 'secondary')
    # If the user clicks the upload file button, process the file
    if upload_file_button:
        with st.spinner('Converting and formatting your file...'):
            # Use the await keyword to wait for the file to be processed
            st.session_state.df = await process_file(uploaded_file)
            st.session_state.inventory_list = await create_spirits_list(st.session_state.df)
            # Switch to the cocktail creation page
            st.session_state.cocktail_page = "get_inventory_cocktail_info"
            switch_page('Create Cocktails')
            st.experimental_rerun()


if st.session_state.inventory_page == 'upload_inventory':
    asyncio.run(upload_inventory())


