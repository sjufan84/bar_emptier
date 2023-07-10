import streamlit as st
import pandas as pd
import openai
from redis import Redis as RedisStore
import uuid
import os
import json
from dotenv import load_dotenv
from typing import Optional
load_dotenv()

# Get the OpenAI API key and org key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")

# Initialize the session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "df" not in st.session_state:
    st.session_state.df = None

# Initialize a connection to the redis store
redis_store = RedisStore()

# Define an Inventory class that will handle the inventory data using Redis
# as the data store.  The inventory will be read in from a CSV or Excel file
# and then stored in Redis as a dictionary.  We will use the session ID_inventory
# as the key and the dictionary as the value.  The dictionary will have the following

# Define a function to return a session id if the user does not have one,
# or to return the session id if the user already has one
def get_session_id():
    session_id = str(uuid.uuid4())
    return session_id



class InventoryService:
    def __init__(self, session_id : Optional[str], inventory: Optional[dict] = None):
        # If the session id is not provided, we will generate a new one
        if not session_id:
            self.session_id = get_session_id()
            self.inventory = None
        else:
            self.session_id = session_id
            # See if the inventory is in redis
            try:
                inventory = self.load_inventory()
                if inventory:
                    self.inventory = inventory
                else:
                    self.inventory = None
            except Exception as e:
                print(f"Failed to load inventory from Redis: {e}")
                self.inventory = None
        
    
    # Define a function to save the recipe to redis under the "recipe" key
    def save_inventory(self):  
        try:
            redis_store.set(f'{self.session_id}_inventory', json.dumps(self.inventory))
        except Exception as e:
            print(f"Failed to save recipe to Redis: {e}")

    # Define a function to load the recipe from redis and convert it to a CocktailRecipe object
    def load_inventory(self):
        try:
            inventory = redis_store.get(f'{self.session_id}_inventory')
            if inventory:
                inventory = json.loads(inventory)
                return inventory
            else:
                return None
        except Exception as e:
            print(f"Failed to load recipe from Redis: {e}")
            return None
        
    # Define the function to process the file
    def process_and_format_file(self, uploaded_file):
        if uploaded_file == None:
            df = pd.read_csv('./resources/inventory.csv')
        elif uploaded_file.name.lower().endswith('csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.lower().endswith(('xlsx', 'xls')):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            raise ValueError('File must be a CSV or Excel file')

            
        # Convert the columns to match desired format
        df.columns = ['Name','Quantity','Volume per Unit (ml)','Cost per Unit']
        # Use the formatted dataframe to calculate the cost per ml, cost per oz, 
        # total amount (ml), total amount (oz), and total value and add these columns
        # Divide the total cost by the total amount to get the cost per ml
        df['Cost per ml'] = df['Cost per Unit'] / df['Volume per Unit (ml)']
        # Convert the cost per ml to cost per oz
        df['Cost per oz'] = round((df['Cost per ml'] / 0.033814), 3)
        # Calculate the total value of the inventory
        df['Total Amount (ml)'] = df['Quantity'] * df['Volume per Unit (ml)']
        df['Total Value'] = df['Total Amount (ml)'] * df['Cost per ml']

        st.session_state.df = df

        # Save the inventory to redis
        self.inventory = df.to_dict()
        self.save_inventory()

        # Return the dictionary
        return df

                
      
