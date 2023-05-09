# We are going to allow the user to decide between three chefs who have 3 different cooking styles, give their specifications
# and then generate a recipe for them. After that we will then allow them to ask the selected chef questions about the recipe
import streamlit as st
from streamlit_chat import message
from utils.chat_utils import initialize_chat, save_chat_history_dict, add_message_to_chat, create_bartender_data,\
                             get_recipe_bartender_response, get_general_bartender_response, get_chat_choices
import openai
import os
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
load_dotenv()


def init_chat_session_variables():
    # Initialize session state variables
    session_vars = [
        'recipe', 'bar_chat_page', 'style','attitude', 'initials_seed', 'chat_messages', 'chat_choice','response', 'history', 'chat_history_dict', 'i', 'seed'
    ]
    default_values = [
        '', 'chat_choices', '', '', '', [], '', '', None, {}, 0, "Spooky"
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value


# Set up the OpenAI API configuration
def setup_api():
    # Set up the OpenAI API configuration
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.organization = os.getenv("OPENAI_ORG")

# Define a function to reset the other pages to their default state
def reset_pages():
    # Make sure that when the user clicks onto this page, the session state of the other pages is reset
    st.session_state.cocktail_page = 'get_cocktail_type'
    st.session_state.inventory_page = 'upload_inventory'
    st.session_state.menu_page = 'upload_menus'


# Initializations
init_chat_session_variables()
create_bartender_data()
setup_api()
reset_pages()



# Define the display recipe and follow up chat function
def follow_up_recipe_chat():
    if "seed" not in st.session_state:
        st.session_state.seed = "Spooky"
    
    # Add 1 to the i in session state so we can create unique widgets
    st.session_state.i += 1

    # Display the recipe
    st.write(st.session_state.recipe_text)

    # Initialize the chat if the length of the chat history is 0
    if len(st.session_state.chat_history_dict) == 0:
        initial_message = "What questions can I answer for you about the recipe?"
        initialize_chat(initial_message)
        # Display the initial bartender message
        message(f"{initial_message}", avatar_style='miniavs', seed = f'{st.session_state.seed}')
    # Create a text area for the user to enter their message
    user_message = st.text_area("What questions do you have about the recipe?", value='', height=150, max_chars=None, key=None)
    # Create a button to submit the user message
    submit_user_follow_up_button = st.button("Submit Follow Up Question", type = 'primary', use_container_width=True)
    # Upon clicking the submit button, we want to add the user's message to the chat history and generate a an answer to their question
    if submit_user_follow_up_button:
        with st.spinner('The bartender is thinking about your question...'):
            add_message_to_chat(message = user_message, role = 'user')
            # Generate the response from the bartender
            bartender_response = get_recipe_bartender_response(question = user_message, recipe = st.session_state.parsed_recipe)
            # Add the response to the chat history
            add_message_to_chat(message = f'{bartender_response}', role = 'ai')
            # Add the new chat history to the chat history dictionary
            st.session_state.chat_history_dict = save_chat_history_dict()
            # Display the chat history dictionary 
            for chat_message in st.session_state.chat_history_dict:
                if chat_message['type'] == 'human':
                    message(chat_message['data']['content'], avatar_style='initials', seed = 'UU', key = f'{st.session_state.i}', is_user = True)
                    st.session_state.i += 1
                elif chat_message['type'] == 'ai':
                    message(chat_message['data']['content'], avatar_style='initials', seed = 'SC')
                    st.session_state.i += 1

    # Create space between the chat and the buttons
    st.write("")
    st.write("")
    st.write("")

    # Create a button to allow the user to create a new recipe
    create_new_recipe_button = st.button("Create a New Recipe", type = 'primary', use_container_width=True)
    # Upon clicking the create new recipe button, we want to reset the chat history and chat history dictionary
    # And return to the recipe creation page
    if create_new_recipe_button:
        # Reset the chat history and chat history dictionary
        st.session_state.chat_history_dict = {}
        st.session_state.chat_messages = []
        # Return to the recipe creation page
        st.session_state.bar_chat_page = 'get_cocktail_type'
        switch_page("Create Cocktails")
        st.experimental_rerun()


    # Create a button to allow the user to return to "Chat Home"
    return_to_chat_home_button = st.button("Return to Chat Home", type = 'primary', use_container_width=True)
    # Upon clicking the return to chat home button, we want to reset the chat history and chat history dictionary
    # And return to the chat home page
    if return_to_chat_home_button:
        # Reset the chat history and chat history dictionary
        st.session_state.chat_history_dict = {}
        st.session_state.chat_messages = []
        # Return to the chat home page
        st.session_state.bar_chat_page = 'chat_choices'
        st.experimental_rerun()

# Define the general chat function
def general_chat():
    # Add 1 to the i in session state so we can create unique widgets
    st.session_state.i += 1

    # Initialize the chat if the length of the chat history is 0
    if len(st.session_state.chat_history_dict) == 0:
        initial_message = "What questions can I answer for you today?"
        initialize_chat(initial_message)
    
        # Display initial chef message
        message(f"{initial_message}", avatar_style='miniavs', seed = f'{st.session_state.seed}')
    # Create a text area for the user to enter their message
    user_message = st.text_area('Ask any bar question you might have, i.e. "What is Triple Sec" or "What is the proper muddling technique?', value='', height=150, max_chars=None, key=None)
    # Create a button to submit the user message
    submit_user_follow_up_button = st.button("Submit Your Question", type = 'primary', use_container_width=True)
    # Upon clicking the submit button, we want to add the user's message to the chat history and generate a an answer to their question
    if submit_user_follow_up_button:
        with st.spinner('The bartender is thinking about your question...'):
            add_message_to_chat(message = user_message, role = 'user')
            # Generate the response from the chef
            bartender_response = get_general_bartender_response(question = user_message)
            # Add the response to the chat history
            add_message_to_chat(message = f'{bartender_response}', role = 'ai')
            # Add the new chat history to the chat history dictionary
            st.session_state.chat_history_dict = save_chat_history_dict()
            # Display the chat history dictionary 
            for chat_message in st.session_state.chat_history_dict:
                if chat_message['type'] == 'human':
                    message(chat_message['data']['content'], avatar_style='initials', seed = 'UU', key = f'{st.session_state.i}', is_user = True)
                    st.session_state.i += 1
                elif chat_message['type'] == 'ai':
                    message(chat_message['data']['content'], avatar_style='minavs', seed = f'{st.session_state.seed}')
                    st.session_state.i += 1

    # Create space between the chat and the buttons
    st.write("")
    st.write("")
    st.write("")

    # Create a button to allow the user to create a new recipe
    create_new_recipe_button = st.button("Create a New Recipe", type = 'primary', use_container_width=True)
    # Upon clicking the create new recipe button, we want to reset the chat history and chat history dictionary
    # And return to the recipe creation page
    if create_new_recipe_button:
        # Reset the chat history and chat history dictionary
        st.session_state.chat_history_dict = {}
        st.session_state.chat_messages = []
        # Return to the recipe creation page
        st.session_state.bar_chat_page = 'get_cocktail_type'
        switch_page("Create Cocktails")
        st.experimental_rerun()


    # Create a button to allow the user to return to "Chat Home"
    return_to_chat_home_button = st.button("Return to Chat Home", type = 'primary', use_container_width=True)
    # Upon clicking the return to chat home button, we want to reset the chat history and chat history dictionary
    # And return to the chat home page
    if return_to_chat_home_button:
        # Reset the chat history and chat history dictionary
        st.session_state.chat_history_dict = {}
        st.session_state.chat_messages = []
        # Return to the chat home page
        st.session_state.bar_chat_page = 'chat_choices'
        st.experimental_rerun()



# Establish the app flow
if st.session_state.bar_chat_page == "chat_choices":
    get_chat_choices()
elif st.session_state.bar_chat_page == 'general_chat':
    general_chat()
elif st.session_state.bar_chat_page == 'recipe_chat':
    follow_up_recipe_chat()

    

       
#st.sidebar.markdown("---")
#st.sidebar.header("Instructions")
#st.sidebar.markdown("1. Select a chef from the dropdown menu.")
#st.sidebar.markdown("2. Click 'Start Conversation' to display the chef's message.")
#st.sidebar.markdown("3. Enter your recipe specifications and click 'Generate Recipe'.")
#st.sidebar.markdown("4. Ask follow-up questions about the recipe.")



