# Importing the necessary libraries
import streamlit as st
import openai
import os
from langchain.memory import ChatMessageHistory
from langchain.schema import messages_to_dict
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
load_dotenv()


# Get the OpenAI API key and org key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")

def init_chat_session_variables():
    # Initialize session state variables
    session_vars = [
        'recipe', 'bar_chat_page', 'style','attitude', 'chat_messages', 'chat_choice','response', 'history', 'chat_history_dict'
    ]
    default_values = [
        '', 'chat_choices', '', '', [], '', '', None, {}
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value



# Define a function to initialize the chatbot
# This function will be re-used throughout the app
# And take in the initial message as a parameter as well
# as a chat type (e.g. "recipe" or "foodpedia", etc.
# to distinguish between different chatbots and how they are stored in memory
# Set it to the initial message in the chat history
def initialize_chat(initial_message):
    # Initialize the chatbot with the first message
    history = ChatMessageHistory()
    history.add_ai_message(initial_message)
    st.session_state.history = history
    return st.session_state.history

# We need to define a function to save the chat history as a dictionary
# This will be used to save the chat history to the database and to display the chat history
def save_chat_history_dict():
    # Save the chat history as a dictionary
    chat_history_dict = messages_to_dict(st.session_state.history.messages)
    st.session_state.chat_history_dict = chat_history_dict
    return st.session_state.chat_history_dict


# Now we need to define a function to add messages to the chatbot
# This will take in the message_type (e.g. "user" or "ai")
# and the message itself
# It will then add the message to the chat history
# and return the updated chat history
def add_message_to_chat(message, role):
    # Add the appropriate message to the chat history depending on the role
    if role == "user":
        st.session_state.history.add_user_message(message)
    elif role == "ai":
        st.session_state.history.add_ai_message(message)
    
    return st.session_state.history


def create_bartender_data():
    # Create chef-related dictionaries
    global bartender_style_dict, bartender_attitude_dict, seed_dict
   # Create a dictionary of chefs and their cooking styles, a seed for their initials to be displayed in the chatbot, and a dictionary of notes on each chef
    bartender_style_dict = {
        "Mixologist": "An innovative, craft-focused bartender skilled in blending unique flavors and utilizing advanced techniques for artistic cocktails.",

        "Efficient" : "A fast-paced bartender adept at preparing popular drinks quickly and accurately in high-traffic environments.",

        "Home Tinkerer" : "An enthusiastic amateur mixologist who experiments with various ingredients and techniques, creating unique drinks in a relaxed setting."
    }
    bartender_attitude_dict = {
        "Mixologist": "Innovative and creative",
        "Efficient" : "Fast-paced and accurate",
        "Home Tinkerer" : "Relaxed and enthusiastic"
        }
    seed_dict = {
        "Mixologist": "Spooky",
        "Efficient" : "Mittens",
        "Home Tinkerer" : "Bandit"
    }

# Define a function to get the user's choice of bartender style and attitude and whether or not they are querying a recipe
def get_chat_choices():

    # Create a selectbox to allow the user to choose a bartender style
    st.subheader("Choose a bartender style")
    bartender_style = st.selectbox(
            "Select the type of bartender you want to chat with.  Each type of bartender has a different style and attitude, so you can\
            choose the one that best fits your needs.",
        ("Mixologist", "Efficient", "Home Tinkerer")
    )
    # If there is as recipe in the session state, give the user the option to ask a follow up question or continue with general conversation
    # If there is not a recipe in session state, note that the user has not created a recipe yet and then allow them to continue with general conversation
    if st.session_state.recipe != '':
        st.success("**You have created a recipe.  Would you like to ask a follow up question about it or continue with general conversation?**")
        # Create a selectbox to allow the user to choose whether or not they want to ask a follow up question about the recipe or just continue with general conversation
        chat_choice_question = st.selectbox(
            "Choose whether or not you want to ask a follow up question about your recipe or just continue with general conversation",
            (["Recipe Chat", "General Conversation"])
        )
        if chat_choice_question == "Recipe Chat":
            st.session_state.chat_choice = 'recipe_chat'
        elif chat_choice_question == "General Conversation":
            st.session_state.chat_choice = 'general_chat'
    else:
        st.warning('**You have not created a recipe yet.  If you want to create a recipe first to chat about, click "Create a Cocktail" below.\
                    Otherwise you can continue with general bar questions by clicking the "Start Conversation" button.**')
        st.session_state.chat_choice = 'general_chat'
        # Create a button to allow the user to create a recipe
        create_recipe_button = st.button("Create a Cocktail", type = 'primary', use_container_width=True)
        if create_recipe_button:
            switch_page("Create Cocktails")
    
    start_conversation_button = st.button("Start Conversation", type = 'primary', use_container_width=True)
    if start_conversation_button:
        # Establish the bartender style and attitude based on the user's choice and the relevant values in the dictionaries
        st.session_state.style = bartender_style_dict[bartender_style]
        st.session_state.attitude = bartender_attitude_dict[bartender_style]
        st.session_state.seed = seed_dict[bartender_style]
        # If the chat_choice is 'general_chat', set the bar_chat_page to 'general_chat'
        # If the chat_choice is 'recipe_chat', set the bar_chat_page to 'recipe_chat'
        if st.session_state.chat_choice == 'general_chat':
            st.session_state.bar_chat_page = 'general_chat'
            st.experimental_rerun()
        elif st.session_state.chat_choice == 'recipe_chat':
            st.session_state.bar_chat_page = 'recipe_chat'
            st.experimental_rerun()
        

# Define the function to answer any follow up questions the user has about the recipe
def get_recipe_bartender_response(question, recipe):
    # Check to see if there is an inventory in the session state
    messages = [
    {
        "role": "system",
        "content": f"You are a master mixologist who has provided a recipe {recipe} for the user about which they would like to ask some follow up questions.  The conversation\
            you have had so far is {st.session_state.history.messages}.  Please respond as a friendly bartender with {st.session_state.style}\
            and a {st.session_state.attitude} attitude who is happy to answer the user's questions thoroughly."
                
    },
    {
        "role": "user",
        "content": f"Thanks for the recipe!  I need to ask you a follow up question {question}.  Do you mind answering it for me?"
    },
   
    ]

      # Use the OpenAI API to generate a recipe
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = messages,
            max_tokens=750,
            frequency_penalty=0.5,
            presence_penalty=0.75,
            temperature=1,
            n=1
        )
        st.session_state.response = response
        response = response.choices[0].message.content

    except:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages = messages,
            max_tokens=500,
            frequency_penalty=0.2,
            temperature = 1, 
            n=1, 
            presence_penalty=0.2,
        )
        st.session_state.response = response
        response = response.choices[0].message.content

    return response

# Define the function to answer general questions the user has about cocktails
def get_general_bartender_response(question):
        
        messages = [
        {
            "role": "system",
            "content": f"You are a master mixologist who is chatting with the user about cocktails.  The conversation\
                you have had so far is {st.session_state.history.messages}.  Please respond as a friendly bartender with {st.session_state.style}\
                and a {st.session_state.attitude} attitude who is happy to answer the user's questions thoroughly."
                    
        },
        {
            "role": "user",
            "content": f"I have a question about cocktails.  {question}"
        },
    
        ]
    
        # Use the OpenAI API to generate a recipe
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages = messages,
                max_tokens=750,
                frequency_penalty=0.5,
                presence_penalty=0.75,
                temperature=1,
                n=1
            )
            st.session_state.response = response
            response = response.choices[0].message.content
    
        except:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                messages = messages,
                max_tokens=500,
                frequency_penalty=0.2,
                temperature = 1, 
                n=1, 
                presence_penalty=0.2,
            )
            st.session_state.response = response
            response = response.choices[0].message.content
    
        return response


