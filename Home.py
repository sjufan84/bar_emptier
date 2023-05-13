# This is the main demo file for the project.
# This project will use OpenAI to help the user create cocktail recipes to help them get rid of excess inventory.
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from PIL import Image


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

# Create the title using the title class
# This is a custom class that I created in the style.css file
# Set the text to be centered
st.markdown('''<div style="text-align: center;">
<h2 class="title">Bar Emptier AI</h2>
<p>The app that finally answers the question: "What the hell am I going to do with these 17 bottles of Frangelico that someone accidentally ordered?"</p>
</div>''', unsafe_allow_html=True)
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
    cocktail_button = st.button('Create a Cocktail', use_container_width=True)
    if cocktail_button:
        switch_page('Create Cocktails')
        st.experimental_rerun()

with col2:
    # Load in the image of the bar
    bar_image = Image.open('./resources/bartenders.png')
    # Display the image
    st.image(bar_image, use_column_width=True)
    # Create a button to start chatting with a bartender
    bartender_button = st.button('Chat with a Bartender', use_container_width=True)
    if bartender_button:
        st.session_state.bar_chat_page = 'chat_choices'
        switch_page('Cocktail Chat')
        st.experimental_rerun()
    

