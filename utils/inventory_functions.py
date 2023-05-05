import streamlit as st
import pandas as pd
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
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

# A function to use a document loader and text splitter to vectorize the csv data
async def vector_df(df):

    # Load in the dataframe document loader
    from langchain.document_loaders import DataFrameLoader
    loader = DataFrameLoader(df, page_content_column="liquor")
    documents = loader.load()

    # Load in the text splitter
    text_splitter = CharacterTextSplitter(chunk_size=1000)
    documents = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    vectorestore = Chroma.from_documents(documents, embeddings)
    st.session_state.vectorestore = vectorestore

    return vectorestore

# Define a function to create a memory object which can track the state of the conversation
async def create_memory_object():
    from langchain.memory import ConversationBufferMemory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages = True)
    st.session_state.memory = memory

    return memory
    


