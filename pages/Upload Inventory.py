# This is a page to allow the user to upload their bar inventory to be used in the cocktail creation process

# Initial imports
import streamlit as st
from utils.inventory_functions import process_file, vector_df, create_memory_object
from streamlit_chat import message
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
import openai
import asyncio
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

# Get the OpenAI API key and org key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")


# Initialize the session state
def init_inventory_session_variables():
    # Initialize session state variables
    session_vars = [
        'inventory_page', 'inventory_csv_data', 'agent_response', 'history', 'memory', 'chat_messages', 'vectorstore', 'df'
    ]
    default_values = [
        'upload_inventory', None, None, None, None, [], None, pd.DataFrame()
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

async def upload_inventory():
    # Set the page title
    st.markdown('##### Upload your bar inventory below.  The file must be in CSV or Excel format.  Make sure that the first column is your list of\
                spirits, and the second column is the list of amounts.  The name of the column is not as important as the values contained within.')
    # Create a file uploader
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx', 'xls'])
    upload_file_button = st.button('Upload File')
    # If the user clicks the upload file button, process the file
    if upload_file_button:
        with st.spinner('Converting and formatting your file...'):
            # Use the await keyword to wait for the file to be processed
            st.session_state.df = await process_file(uploaded_file)
            '''st.session_state.vectorstore = await vector_df(df)
            st.session_state.memory = await create_memory_object()
            # Once the functions are done processing, set the page to the inventory chat page
            st.session_state.inventory_page = 'inventory_chat'''
            st.session_state.inventory_page = 'agent_chat'
            st.experimental_rerun()

# Define inventory chat function
def inventory_chat():
    i = 0
    # Set the page title
    st.markdown('##### What questions can I answer for you today?')
    # Initialize the ConversationRetrievalChain from langchain
    qa = ConversationalRetrievalChain.from_llm(OpenAI(model_name='gpt-3.5-turbo', temperature=1), st.session_state.vectorstore.as_retriever(), memory = st.session_state.memory)
    # Create a text input box for the user to ask questions
    question = st.text_input('Question: ', value='', key=f'question_{i}')
    # Create a button to submit the question
    if st.button('Submit', key=f'submit_{i}'):
        with st.spinner('Thinking...'):
            # Get the answer from the qa model
            result = qa({"question":question})
            st.write(result['answer'])
            st.write(result)
            # Append a tuple of the question with the role of "user" and the answer with the role of "ai" to the chat_messages list
            #st.session_state.chat_messages.append((question, 'user'))
            #st.session_state.chat_messages.append((result, 'ai'))
            # Display the chat messages
            #for chat_message, role in st.session_state.chat_messages:
                # If the role is "user", set the "is_user" parameter to True and the seed to 'UU'
            #    if role == 'user':
            #        message(chat_message, is_user=True, avatar_style='initials', seed='UU')
            #    else:
            #        message(chat_message, avatar_style='initials', seed='DD')
            #i += 1

def agent_chat():
    from langchain.agents import create_pandas_dataframe_agent
    from langchain.llms import OpenAI
    from langchain.chat_models import ChatOpenAI
    i = 0
    agent = create_pandas_dataframe_agent(ChatOpenAI(model_name='gpt-3.5-turbo', temperature=1), st.session_state.df, verbose=True)
    user_question = st.text_input('Question: ', value='', key=f'question_{i}')
    if st.button('Submit', key=f'submit_{i}'):
        st.write(str(agent.run(user_question)))
init_inventory_session_variables()


if st.session_state.inventory_page == 'upload_inventory':
    asyncio.run(upload_inventory())
elif st.session_state.inventory_page == 'inventory_chat':
    inventory_chat()
elif st.session_state.inventory_page == 'agent_chat':
    agent_chat()

