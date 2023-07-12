"""
This is the main demo file for the project.
This project will use OpenAI to help the user create cocktail recipes to help them get rid of excess inventory.
"""
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit import components
from PIL import Image
import pandas as pd

# Import the services
from utils.cocktail_functions import RecipeService
from utils.chat_utils import ChatService
from utils.inventory_functions import InventoryService

# Define the page config
st.set_page_config(page_title="BarKeepAI", page_icon="./resources/cocktail_icon.png", initial_sidebar_state="collapsed")

st.markdown("#### Documentation notes:")
st.success('''
           **The landing page.  Allows the user to choose to have a general chat with a bartender, or create a recipe.
           Once the recipe is created, they will have the option to initiate a chat about the recipe along with several other features.**
              ''')
st.markdown('---')


# Initialize the session state
def init_session_variables():
    # Initialize session state variables
    session_vars = [
        'cocktail_page', 'num_recipes', 'demo_page', 'menu_page', 'df',
        'is_demo', 'bar_chat_page', 'recipe_service', 'chat_service',
        'inventory_page', 'inventory_service', 'training_guide', 'is_inventory_recipe'
    ]
    default_values = [
        'get_cocktail_type', 0, 'upload_inventory', 'upload_menus', pd.DataFrame(), 
        False, 'chat_choice', RecipeService(), ChatService(), 
        'upload_inventory', InventoryService(None), "", False
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

# Reset the pages to their default values if someone returns to the home page
def reset_pages():
    st.session_state.cocktail_page = 'get_cocktail_type'
    st.session_state.menu_page = "upload_menus"
    st.session_state.bar_chat_page = "chat_choice"
    st.session_state.inventory_page = "upload_inventory"
    st.session_state.training_page = "get_training_type"

# Initialize the session variables
init_session_variables()
reset_pages()

# Create the title using the title class
# This is a custom class that I created in the style.css file
# Set the text to be centered
st.markdown('''<div style="text-align: center;">
<h2 class="title">BarKeepAI</h2>
<p style "font-weight:100px;">The app that finally answers the question: "What the hell am I going to do with these 17 bottles of Frangelico that someone accidentally ordered?"</p>
</div>''', unsafe_allow_html=True)
st.text('')
# Create two columns for the home page
col1, col2 = st.columns(2, gap="large")
# With the first column we will display a picture of a cocktail with a "Create a Cocktail" button underneath
# With the second column we will display a picture of a bar with a "Chat with a Bartender" button underneath
with col1:
    # Load in the image of the cocktail
    cocktail_image = Image.open('./resources/cocktail_pic.png')
    # Display the image
    st.image(cocktail_image, use_column_width=True)
    # Create a button to start creating cocktails
    cocktail_button = st.button('Create a Cocktail', use_container_width=True, type='primary')
    if cocktail_button:
        switch_page('Create Cocktails')
        st.experimental_rerun()

with col2:
    # Load in the image of the bar
    bar_image = Image.open('./resources/bartenders.png')
    # Display the image
    st.image(bar_image, use_column_width=True)
    # Create a button to start chatting with a bartender
    bartender_button = st.button('Chat with a Bartender', use_container_width=True, type='primary')
    if bartender_button:
        st.session_state.bar_chat_page = 'chat_choice'
        switch_page('Cocktail Chat')
        st.experimental_rerun()

# Display feedback form
st.markdown('---')
st.markdown('''<div style="text-align: center;">
<h4 class="feedback">We want to hear from you!  Please help us grow by taking a quick second to fill out the form below and to stay in touch about future developments.  Thank you!</h4>
</div>''', unsafe_allow_html=True)

src="https://docs.google.com/forms/d/e/1FAIpQLSc0IHrNZvMfzqUeSfrJxqINBVWxE5ZaF4a30UiLbNFdVn1-RA/viewform?embedded=true"
components.v1.iframe(src, height=600, scrolling=True)
