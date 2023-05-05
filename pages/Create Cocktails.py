# This is the main entry point for the user to create cocktails

# Import libraries
import streamlit as st
from utils.save_recipes import save_recipe_as_pdf, get_recipe_pdf_download_link
from utils.cocktail_functions import get_cocktail_recipe, get_menu_cocktail_recipe
from streamlit_extras.switch_page_button import switch_page

# Initialize the session state
def init_cocktail_session_variables():
    # Initialize session state variables
    session_vars = [
        'cocktail_page', 'cocktail_recipe', 'food_menu', 'drink_menu'
    ]
    default_values = [
        'get_cocktail_type', '', '', ''
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

# Reset the pages to their default values
def reset_pages():
    st.session_state.menu_page = "upload_menus"
    st.session_state.bar_chat_page = "chat_choices"
    st.session_state.inventory_page = "upload_inventory"

# Initialize the session variables
init_cocktail_session_variables()
reset_pages()



# Define the function to get the information about the cocktail
def get_cocktail_type():
    # Set the page title
    st.title('Create Cocktails')
    st.markdown('##### Use this page to create a cocktail recipe to help you use up your excess liquor inventory! 🍸🍹')
    # Give the user the option to upload a menu or menus for the model to reference when creating the cocktails
    st.success(f'**If you would like to upload your existing food menu, cocktail menu, or both, please do so by clicking below.\
               This can be useful if you want to create a cocktail that fits in well with the overall theme of the menu and is\
                not similar to any of the other cocktails on the menu, if any.  You can also upload your current inventory\
                for further contextual recipe creation.  Otherwise click "Proceed to Cocktail Creation" to get started!"**')
    upload_menus_button = st.button('Upload your menu(s)')
    if upload_menus_button:
        switch_page('Upload Menus')
    upload_inventory_button = st.button('Upload your inventory')
    if upload_inventory_button:
        switch_page('Upload Inventory')
    proceed_without_menu_button = st.button('Proceed to Cocktail Creation')
    if proceed_without_menu_button:
        st.session_state.cocktail_page = 'get_cocktail_info'
        st.experimental_rerun()

def get_cocktail_info():

    # Build the form 

    # Start by getting the input for the liquor that the user is trying to use up
    liquor = st.text_input('What liquor are you trying to use up?')
    # Allow the user to choose what type of cocktail from "Classic", "Craft", "Standard"
    cocktail_type = st.selectbox('What type of cocktail are you looking for?', ['Classic', 'Craft', 'Standard'])
    # Allow the user the option to select a type of cuisine to pair it with if they have not uploaded a food menu
    cuisine = st.selectbox('What type of cuisine, if any, are you looking to pair it with?', ['American',\
                            'Mexican', 'Italian', 'French', 'Chinese', 'Japanese', 'Thai', 'Indian', 'Greek', 'Spanish', 'Korean', 'Vietnamese',\
                            'Mediterranean', 'Middle Eastern', 'Caribbean', 'British', 'German', 'Irish', 'African', 'Moroccan', 'Nordic', 'Eastern European',\
                            'Jewish', 'South American', 'Central American', 'Australian', 'New Zealand', 'Pacific Islands', 'Canadian', 'Other'])
    # Allow the user to enter a theme for the cocktail if they want
    theme = st.text_input('What theme, if any, are you looking for? (e.g. "tiki", "holiday", "summer", etc.)')

    # Create the submit button
    cocktail_submit_button = st.button(label='Create your cocktail!')
    if cocktail_submit_button:
        with st.spinner('Creating your cocktail recipe.  This may take a minute...'):
            get_cocktail_recipe(liquor, cocktail_type, cuisine, theme)
            st.session_state.cocktail_page = "display_recipe"
            st.experimental_rerun()

def get_menu_cocktail_info():

    # Build the form 

    # Start by getting the input for the liquor that the user is trying to use up
    liquor = st.text_input('What liquor are you trying to use up?')
    # Allow the user to choose what type of cocktail from "Classic", "Craft", "Standard"
    cocktail_type = st.selectbox('What type of cocktail are you looking for?', ['Classic', 'Craft', 'Standard'])
   
    # Allow the user to enter a theme for the cocktail if they want
    theme = st.text_input('What theme, if any, are you looking for? (e.g. "tiki", "holiday", "summer", etc.)')

    # Create the submit button
    cocktail_submit_button = st.button(label='Create your cocktail!')
    if cocktail_submit_button:
        with st.spinner('Creating your cocktail recipe.  This may take a minute...'):
            get_menu_cocktail_recipe(liquor, cocktail_type, theme)
            st.session_state.cocktail_page = "display_recipe"
            st.experimental_rerun()


def display_recipe():
    st.markdown('##### Here is your recipe! 🍸🍹')
    st.write(st.session_state.recipe_text)
    # Display the recipe name
    st.markdown(f'**{st.session_state["cocktail_name"]}**')
    # Display the recipe ingredients
    st.markdown('**Ingredients:**')
    for ingredient in st.session_state['ingredients']:
        st.markdown(f'* {ingredient}')
    # Display the recipe instructions
    st.markdown('**Instructions:**')
    for instruction in st.session_state['instructions']:
        st.markdown(f'* {instruction}')
    # Display the recipe garnish
    st.markdown(f'**Garnish:**  {st.session_state.garnish}')
    # Display the recipe glass
    st.markdown(f'**Glass:**  {st.session_state.glass}')
    # Save the selected recipe as a PDF
    pdf_path = save_recipe_as_pdf(st.session_state.recipe, f"my_recipe.pdf")

    # Generate a download link for the saved PDF
    download_link = get_recipe_pdf_download_link(pdf_path, f"my_recipe.pdf")

    # Display the download link
    st.markdown(download_link, unsafe_allow_html=True)

    # Create an option to chat about the recipe
    chat_button = st.button('Chat with a bartender about this recipe?')
    if chat_button:
        switch_page('Cocktail Chat')
   
    # Create a "Create another cocktail" button
    create_another_cocktail_button = st.button('Create another cocktail!')
    if create_another_cocktail_button:
        st.session_state.cocktail_page = "get_cocktail_info"
        st.experimental_rerun()

if st.session_state.cocktail_page == "get_cocktail_type":
    get_cocktail_type()
elif st.session_state.cocktail_page == "get_cocktail_info":
    get_cocktail_info()
elif st.session_state.cocktail_page == "get_menu_cocktail_info":
    get_menu_cocktail_info()
elif st.session_state.cocktail_page == "display_recipe":
    display_recipe()