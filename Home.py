# This is the main demo file for the project.
# This project will use OpenAI to help the user create cocktail recipes to help them get rid of excess inventory.
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from PIL import Image
from streamlit import components
from PIL import Image
import pandas as pd


# Initialize the session state
def init_session_variables():
    # Initialize session state variables
    session_vars = [
        'cocktail_page', 'num_recipes', 'demo_page', 'menu_page', 'df', 'is_demo', 'training_page'
    ]
    default_values = [
        'get_cocktail_info', 0, 'upload_inventory', 'upload_menus', pd.DataFrame(), False, 'get_training_type'
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

# Reset the pages to their default values if someone returns to the home page
def reset_pages():
    st.session_state.cocktail_page = 'get_cocktail_info'
    st.session_state.menu_page = "upload_menus"
    st.session_state.bar_chat_page = "chat_choices"
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
        st.session_state.bar_chat_page = 'chat_choices'
        switch_page('Cocktail Chat')
        st.experimental_rerun()

st.markdown('---')
## Offer the chance to incorporate inventory (**start out with a dummy inventory**) and menus (full on here)
st.warning("##### For an even richer experience, upload your food and \ or existing drink\
           menus so the model will be able to take them into context when designing your cocktails.\
             \n  ##### Alternatively, you can select 'Inventory Cocktail' to experiment with creating cocktails\
            that prioritize using spirits from your inventory.")
st.text("")
st.text("")

# Now we will create two columns, one to display the upload menu option
# and one to display the "Inventory Cocktail" option
menu_column, inventory_column = st.columns(2, gap='large')

# Insert an image here to illustrate menu uploads
with menu_column:
    menu_image = Image.open("./resources/bar_menu.png")
    st.image(menu_image)
    upload_menu_button = st.button("Upload your menu(s)", type = 'primary', use_container_width=True)
    
    # Redirect to the "Upload Menu" page
    if upload_menu_button:
        st.session_state.menu_page = "upload_menus"
        switch_page("Upload Menus")
        st.experimental_rerun()

# Create the option to create a cocktail from the inventory
with inventory_column:
    inventory_image = Image.open('./resources/inventory_image.png')
    st.image(inventory_image, use_column_width=True)
    inventory_button = st.button("Create an Inventory Cocktail", type='primary', use_container_width=True)
    if inventory_button:
        # Load in the dummy inventory as a dataframe
        st.session_state.df = pd.read_csv('./tests/inventory.csv')

        # Insert a "Use in Cocktail" row to be used as a boolean in the interactive df
        st.session_state.df.insert(0, "Use in Cocktail", False)

        # Set the proper session state and switch pages
        st.session_state.demo_page = "choose_spirit"
        switch_page("Demo")
        st.experimental_rerun()
    
    
st.markdown('---')
st.markdown('''<div style="text-align: center;">
<h4 class="feedback">We want to hear from you!  Please help us grow by taking a quick second to fill out the form below and to stay in touch about future developments.  Thank you!</h4>
</div>''', unsafe_allow_html=True)

src="https://docs.google.com/forms/d/e/1FAIpQLSc0IHrNZvMfzqUeSfrJxqINBVWxE5ZaF4a30UiLbNFdVn1-RA/viewform?embedded=true"
components.v1.iframe(src, height=600, scrolling=True)
