# This is the main entry point for the user to create cocktails

# Import libraries
import streamlit as st
# from utils.save_recipes import save_recipe_as_pdf, get_recipe_pdf_download_link
from utils.cocktail_functions import get_cocktail_recipe, get_menu_cocktail_recipe, get_inventory_cocktail_recipe
from streamlit_extras.switch_page_button import switch_page
from utils.image_utils import generate_image
import asyncio
from PIL import Image
import pandas as pd

# Initialize the session state
def init_cocktail_session_variables():
    # Initialize session state variables
    session_vars = [
        'cocktail_page', 'cocktail_recipe', 'food_menu', 'drink_menu', 'image', 'inventory_list', 'cocktail_name'
    ]
    default_values = [
        'get_cocktail_info', '', '', '', None, [], ''
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
    # If there is already an inventory or a menu uploaded, proceed to the cocktail creation page
    # Otherwise, ask the user to upload their inventory or menu
    if st.session_state.inventory_list or st.session_state.food_menu or st.session_state.drink_menu:
        st.session_state.cocktail_page = 'get_cocktail_info'
        st.experimental_rerun()
    else:    
        # Give the user the option to upload a menu or menus for the model to reference when creating the cocktails
        st.markdown('''<div style="text-align: center;">
        <h2 style = "color: black;">Welcome to the Cocktail Creator!</h2>
        <h5 style = "color: black;">If you would like to upload your food and / or existing bar menus, or your inventory, please do so below.  This can\
        be useful to provide extra context for the model when creating your cocktails.  Otherwise, you can proceed directly to the cocktail creation page.</h5>
        </div>''', unsafe_allow_html=True)
        proceed_without_menu_button = st.button('Proceed Directly to Cocktail Creation', use_container_width=True, type = 'primary')
        if proceed_without_menu_button:
            st.session_state.cocktail_page = 'get_cocktail_info'
            st.experimental_rerun()
        
        # Create two columns -- one for the upload menu image and button, and one for the upload inventory image and button
        col1, col2 = st.columns(2, gap="large")
        with col1:
            menu_image = Image.open('resources/bar_menu.png')
            st.image(menu_image, use_column_width=True)
            upload_menus_button = st.button('Upload your menu(s)', use_container_width=True, type = 'primary')
            if upload_menus_button:
                switch_page('Upload Menus')
        with col2:
            inventory_image = Image.open('resources/inventory_image.png')
            st.image(inventory_image, use_column_width=True)
            upload_inventory_button = st.button('Upload your inventory', use_container_width=True, type = 'primary')
            if upload_inventory_button:
                switch_page('Upload Inventory')
        

async def get_cocktail_info():

    # Build the form 

    # Start by getting the input for the liquor that the user is trying to use up
    liquor = st.text_input('What liquor are you trying to use up?')
    # Allow the user to choose what type of cocktail from "Classic", "Craft", "Standard"
    cocktail_type = st.selectbox('What type of cocktail are you looking for?', ['Classic', 'Craft', 'Standard'])
    # Allow the user the option to select a type of cuisine to pair it with if they have not uploaded a food menu
    cuisine = st.selectbox('What type of cuisine, if any, are you looking to pair it with?', ['Any', 'American',\
                            'Mexican', 'Italian', 'French', 'Chinese', 'Japanese', 'Thai', 'Indian', 'Greek', 'Spanish', 'Korean', 'Vietnamese',\
                            'Mediterranean', 'Middle Eastern', 'Caribbean', 'British', 'German', 'Irish', 'African', 'Moroccan', 'Nordic', 'Eastern European',\
                            'Jewish', 'South American', 'Central American', 'Australian', 'New Zealand', 'Pacific Islands', 'Canadian', 'Other'])
    # Allow the user to enter a theme for the cocktail if they want
    theme = st.text_input('What theme, if any, are you looking for? (e.g. "tiki", "holiday", "summer", etc.)', 'None')

    # Create the submit button
    cocktail_submit_button = st.button(label='Create your cocktail!')
    if cocktail_submit_button:
        with st.spinner('Creating your cocktail recipe.  This may take a minute...'):
            await get_cocktail_recipe(liquor, cocktail_type, cuisine, theme)
            image_prompt = f'A cocktail named {st.session_state.cocktail_name} in a {st.session_state.glass} glass with a {st.session_state.garnish} garnish'
            st.session_state.image = generate_image(image_prompt)
            st.session_state.cocktail_page = "display_recipe"
            st.experimental_rerun()

async def get_menu_cocktail_info():

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
            await get_menu_cocktail_recipe(liquor, cocktail_type, theme)
            image_prompt = f'A cocktail named {st.session_state.cocktail_name} in a {st.session_state.glass} glass with a {st.session_state.garnish} garnish'
            st.session_state.image = generate_image(image_prompt)
            st.session_state.cocktail_page = "display_recipe"
            st.experimental_rerun()

# Create a function to get info for a cocktail that takes into account the user's inventory
async def get_inventory_cocktail_info():
    st.markdown('''<div style="text-align: center;">
    <h5 style = "color: black;">Since you have uploaded your inventory, the model will prioritize using spirits you already have on hand\
        when creating your cocktail.</h5>
        </div>''', unsafe_allow_html=True)
  
    # Build the form
    # Start by getting the input for the liquor that the user is trying to use up
    liquor = st.text_input('What liquor are you trying to use up?')
    # Allow the user to choose what type of cocktail from "Classic", "Craft", "Standard"
    cocktail_type = st.selectbox('What type of cocktail are you looking for?', ['Classic', 'Craft', 'Standard'])
    # Allow the user the option to select a type of cuisine to pair it with if they have not uploaded a food menu
    cuisine = st.selectbox('What type of cuisine, if any, are you looking to pair it with?', ['Any', 'American',\
                            'Mexican', 'Italian', 'French', 'Chinese', 'Japanese', 'Thai', 'Indian', 'Greek', 'Spanish', 'Korean', 'Vietnamese',\
                            'Mediterranean', 'Middle Eastern', 'Caribbean', 'British', 'German', 'Irish', 'African', 'Moroccan', 'Nordic', 'Eastern European',\
                            'Jewish', 'South American', 'Central American', 'Australian', 'New Zealand', 'Pacific Islands', 'Canadian', 'Other'])
    # Allow the user to enter a theme for the cocktail if they want
    theme = st.text_input('What theme, if any, are you looking for? (e.g. "tiki", "holiday", "summer", etc.)', 'None')

    # Create the submit button
    cocktail_submit_button = st.button(label='Create your cocktail!')
    if cocktail_submit_button:
        with st.spinner('Creating your cocktail recipe.  This may take a minute...'):
            await get_inventory_cocktail_recipe(liquor, cocktail_type, cuisine, theme)
            image_prompt = f'A cocktail named {st.session_state.cocktail_name} in a {st.session_state.glass} glass with a {st.session_state.garnish} garnish'
            st.session_state.image = generate_image(image_prompt)
            st.session_state.cocktail_page = "display_recipe"
            st.experimental_rerun()

    st.markdown('---')
    # Build the form 
    # Display the user's inventory
    st.write('Here is your current inventory:')
    # Create a dataframe from the inventory list
    inventory_df = pd.DataFrame(st.session_state.inventory_list, columns=['Ingredient', 'Quantity'])
    # Set the index to the ingredient name
    inventory_df.set_index('Ingredient', inplace=True)
    # Display the dataframe
    st.dataframe(inventory_df, use_container_width=True)


def display_recipe():
    # Create the header
    st.markdown('''<div style="text-align: center;">
    <h2 style = "color: black;">Here's your recipe!</h1>
    <hr>    
    </div>''', unsafe_allow_html=True)
    # Create 2 columns, one to display the recipe and the other to display a generated picture as well as the buttons
    col1, col2 = st.columns([1.5, 1], gap = "large")
    with col1:
        # Display the recipe name
        st.markdown(f'**Recipe Name:** {st.session_state["cocktail_name"]}')
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
        # Display the flavor profile
        st.markdown(f'**Flavor Profile:**  {st.session_state.flavor_profile}')
    with col2:
        # Display the recipe name
        st.markdown(f'<div style="text-align: center;">{st.session_state["cocktail_name"]}</div>', unsafe_allow_html=True)
        st.text("")
        # Display the recipe image
        st.image(st.session_state.image['output_url'], use_column_width=True)
        # Markdown "AI image generate by [StabilityAI](https://stabilityai.com)"]"
        st.markdown('''<div style="text-align: center;">
        <p style = "color: black;">AI cocktail image generated using the Stable Diffusion API by <a href="https://deepai.org/" target="_blank">DeepAI</a></p>
        </div>''', unsafe_allow_html=True)
        st.warning('**Note:** The actual cocktail may not look exactly like this!')
        # Save the selected recipe as a PDF
            # pdf_path = save_recipe_as_pdf(st.session_state.recipe, f"{st.session_state.cocktail_name}")

        # Generate a download link for the saved PDF
        # download_link = get_recipe_pdf_download_link(pdf_path, f"{st.session_state.cocktail_name}.pdf")

        # Display the download link in a centered div
        # st.markdown(f'''<div style="text-align: center;">
        # <p>{download_link}</p>''', unsafe_allow_html=True)

        # Create an option to chat about the recipe
        chat_button = st.button('Questions about the recipe?  Click here to chat with a bartender about it.', type = 'primary', use_container_width=True)
        if chat_button:
            st.session_state.bar_chat_page = "recipe_chat"
            switch_page('Cocktail Chat')
    
        # Create a "Create another cocktail" button
        create_another_cocktail_button = st.button('Create another cocktail', type = 'primary', use_container_width=True)
        if create_another_cocktail_button:
            st.session_state.cocktail_page = "get_cocktail_info"
            st.experimental_rerun()

if st.session_state.cocktail_page == "get_cocktail_type":
    get_cocktail_type()
elif st.session_state.cocktail_page == "get_cocktail_info":
    asyncio.run(get_cocktail_info())
elif st.session_state.cocktail_page == "get_menu_cocktail_info":
    asyncio.run(get_menu_cocktail_info())
elif st.session_state.cocktail_page == "get_inventory_cocktail_info":
    asyncio.run(get_inventory_cocktail_info())
elif st.session_state.cocktail_page == "display_recipe":
    display_recipe()