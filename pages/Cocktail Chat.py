import streamlit as st
from streamlit_chat import message
from utils.chat_utils import ChatService, Context
from utils.cocktail_functions import RecipeService
import uuid
import openai
import os
from streamlit_extras.switch_page_button import switch_page
from streamlit import components
from dotenv import load_dotenv
load_dotenv()


# Set up the OpenAI API configuration
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")

# Define a function to reset the other pages to their default state
def reset_pages():
    st.session_state.cocktail_page = 'get_cocktail_info'
    st.session_state.inventory_page = 'upload_inventory'
    st.session_state.menu_page = 'upload_menus'

reset_pages()


def init_chat_session_variables():
    # Initialize session state variables
    session_vars = [
        'recipe', 'bar_chat_page', 'chat_service', 'chat_history', 'session_id', 'context', 'i'
    ]
    default_values = [
        None, 'chat_choice', None, [], str(uuid.uuid4()), None, 0
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

init_chat_session_variables()
chat_service = ChatService(session_id=st.session_state.session_id)


def app():
    if st.session_state.bar_chat_page == "chat_choice":
        get_chat_choice()
    elif st.session_state.bar_chat_page == "display_chat":
        display_chat()

def get_chat_choice():
    chat_service = ChatService(session_id=st.session_state.session_id)

    if st.session_state.recipe:
        st.markdown('**You have created a recipe.  Would you like to ask questions about it, or continue to a general bartender chat?**')
        continue_recipe_button = st.button("Continue with Recipe")
        general_chat_button = st.button("General Chat")
        
        if continue_recipe_button:
            context = Context.RECIPE
            st.session_state.context = context
            chat_service.initialize_chat(context=context)
            st.session_state.bar_chat_page = 'display_chat'
        elif general_chat_button:
            context = Context.GENERAL_CHAT
            st.session_state.context = context
            chat_service.initialize_chat(context=context)
            st.session_state.bar_chat_page = 'display_chat'
    

    else:
        context = Context.GENERAL_CHAT
        st.session_state.context = context
        chat_service.initialize_chat(context=context)
        st.session_state.bar_chat_page = 'display_chat'
        st.experimental_rerun()

def display_chat():
    session_id = st.session_state.session_id
    chat_service = ChatService(session_id=session_id)
    recipe_service = RecipeService(session_id=session_id)
    recipe = recipe_service.load_recipe()
    chat_history = chat_service.chat_history
    
    if len(chat_history) == 1:
        initial_prompt = f"What questions can I answer about the {recipe.name}?" if st.session_state.context == Context.RECIPE else "What questions can I answer for you?"
        message(initial_prompt, is_user=False, avatar_style = 'miniavs', seed='Spooky')

    chat_container = st.container()
    with chat_container:
        # Display the chat history
        for i, chat_message in enumerate(chat_history[1:]):
            if chat_message['role'] == 'user':
                message(chat_message['content'], is_user=True, key = f'user_message_{i}')
            elif chat_message['role'] == 'assistant':
                message(chat_message['content'], is_user=False, key = f'ai_message_{i}', avatar_style = 'miniavs', seed='Spooky') 
            else:
                pass
    user_input = st.text_input("Type your message here", key='user_input')
    submit_button = st.button("Submit", type='primary', key='submit_button', use_container_width=True)

    if submit_button:

        with st.spinner("Thinking..."):
            chat_service.get_bartender_response(question=user_input, session_id=st.session_state.session_id)
            st.experimental_rerun()

    st.markdown("---")
    
    # Create a button to allow the user to create a new recipe
    create_new_recipe_button = st.button("Create a New Recipe", type = 'primary', use_container_width=True)
    # Upon clicking the create new recipe button, we want to reset the chat history and chat history dictionary
    # And return to the recipe creation page
    if create_new_recipe_button:
        # Reset the chat history and chat history dictionary
        chat_service.chat_history = None
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
        st.session_state.history = None
        st.session_state.chat_history_dict = {}
        st.session_state.chat_messages = []
        # Return to the chat home page
        st.session_state.bar_chat_page = 'chat_choices'
        st.experimental_rerun()
                

    # Embed a Google Form to collect feedback
    st.markdown('---')
    st.markdown('''<div style="text-align: center;">
    <h4 class="feedback">We want to hear from you!  Please help us grow by taking a quick second to fill out the form below and to stay in touch about future developments.  Thank you!</h4>
    </div>''', unsafe_allow_html=True)

    src="https://docs.google.com/forms/d/e/1FAIpQLSc0IHrNZvMfzqUeSfrJxqINBVWxE5ZaF4a30UiLbNFdVn1-RA/viewform?embedded=true"
    components.v1.iframe(src, height=600, scrolling=True)



    

app()




