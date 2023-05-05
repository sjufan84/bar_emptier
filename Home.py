# This is the main demo file for the project.
# This project will use OpenAI to help the user create cocktail recipes to help them get rid of excess inventory.
import streamlit as st
from streamlit_extras.switch_page_button import switch_page


# Initialize the session state
def init_session_variables():
    # Initialize session state variables
    session_vars = [
        'cocktail_page', 'num_recipes'
    ]
    default_values = [
        'get_cocktail_info', 0    
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

# Reset the pages to their default values if someone returns to the home page
def reset_pages():
    st.session_state.cocktail_page = 'get_cocktail_type'
    st.session_state.menu_page = "upload_menus"
    st.session_state.bar_chat_page = "chat_choices"
    st.session_state.inventory_page = "upload_inventory"

# Initialize the session variables
init_session_variables()
reset_pages()

# Set the page title
st.markdown('##### Welcome to Bar Room Emptier! 🍸🍹')
st.markdown('##### The app that finally answers the question: "What the hell am I going to do\
            with these 17 bottles of Frangelico that someone accidentally ordered?"')
# Create a button to start creating cocktails
cocktail_button = st.button('Start creating cocktails!')
if cocktail_button:
    switch_page('Create Cocktails')
    st.experimental_rerun()
