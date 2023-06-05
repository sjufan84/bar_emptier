# This is a page to allow the user to upload their bar inventory to be used in the cocktail creation process

# Initial imports
import streamlit as st
from utils.inventory_functions import process_file, create_spirits_list
from utils.cocktail_functions import get_inventory_cocktail_recipe
from utils.image_utils import generate_image
import openai
import pandas as pd
import os
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
import asyncio
load_dotenv()

# Get the OpenAI API key and org key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")



# Initialize the session state
def init_inventory_session_variables():
    # Initialize session state variables
    session_vars = [
        'inventory_page', 'inventory_csv_data', 'df', 'inventory_list', 'image_generated'
    ]
    default_values = [
        'upload_inventory', [], pd.DataFrame(), [], False
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

init_inventory_session_variables()

async def upload_inventory():
    # Set the page title
    st.markdown('''
    <div style = text-align:center>
    <h3 style = "color: black;">Upload your inventory</h3>
    <h5 style = "color: #7b3583;">The first column of your file should contain the name of the spirit\
        and the second column should contain the quantity of that spirit that you have in stock.\
        By uploading your inventory, you are allowing the model to prioritize using up ingredients you already have on hand when suggesting cocktails.</h5>
    </div>
    ''', unsafe_allow_html=True)
    # Create a file uploader
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx', 'xls'])
    upload_file_button = st.button('Upload File and Continue to Cocktail Creation', use_container_width=True, type = 'secondary')
    # If the user clicks the upload file button, process the file
    if upload_file_button:
        with st.spinner('Converting and formatting your file...'):
            # Use the await keyword to wait for the file to be processed
            st.session_state.df = await process_file(uploaded_file)
            st.session_state.inventory_list = await create_spirits_list(st.session_state.df)
            st.session_state.inventory_page = "inventory_cocktail_info"
            st.experimental_rerun()

# Create a function to get info for a cocktail that takes into account the user's inventory
def get_inventory_cocktail_info():
    st.markdown('''<div style="text-align: center;">
    <h5>Since you have uploaded your inventory, the model will prioritize using spirits you already have on hand\
        when creating your cocktail.</h5>
        </div>''', unsafe_allow_html=True)
  
    # Build the form
    # Start by getting the input for the liquor that the user is trying to use up
    liquor = st.text_input('What spirit are you trying to use up?')
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
            get_inventory_cocktail_recipe(liquor, cocktail_type, cuisine, theme)
            st.session_state.image_generated = False
            st.session_state.inventory_page = "display_inventory_recipe"
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
    <h4>Here's your recipe!</h4>
    <hr>    
    </div>''', unsafe_allow_html=True)
    # Create 2 columns, one to display the recipe and the other to display a generated picture as well as the buttons
    col1, col2 = st.columns([1.5, 1], gap = "large")
    with col1:
        # Display the recipe name
        st.markdown(f'**Recipe Name:** {st.session_state["cocktail_name"]}')
        # Display the recipe ingredients
        st.markdown('**Ingredients:**')
        # If there are inventory ingredients, display them in red
        if st.session_state.inventory_ingredients:
            for ingredient in st.session_state['inventory_ingredients']:
                st.markdown(f'* :red[{ingredient}]')
            # Check to see if the ingredient is in the st.session_state.inventory_ingredients list
        if st.session_state.other_ingredients:
            for ingredient in st.session_state['other_ingredients']:
                st.markdown(f'* {ingredient}')
        # Let the user know the key to the colors
        st.markdown('<div style="color: red;">* Red ingredients are ones that you have in your inventory.</div>', unsafe_allow_html=True)
        st.text("")

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
        # Placeholder for the image
        image_placeholder = st.empty()
        # Check if the image has already been generated
        if st.session_state.image_generated == False:
            image_placeholder.text("Generating cocktail image...")
            # Generate the image
            image_prompt = f'A cocktail named {st.session_state.cocktail_name} in a {st.session_state.glass} glass with a {st.session_state.garnish} garnish'
            st.session_state.image = generate_image(image_prompt)
            st.session_state.image_generated = True
        # Update the placeholder with the generated image
        image_placeholder.image(st.session_state.image['output_url'], use_column_width=True)
        # Markdown "AI image generate by [StabilityAI](https://stabilityai.com)"]"
        st.markdown('''<div style="text-align: center;">
        <p>AI cocktail image generated using the Stable Diffusion API by <a href="https://deepai.org/" target="_blank">DeepAI</a></p>
        </div>''', unsafe_allow_html=True)
        st.warning('**Note:** The actual cocktail may not look exactly like this!')
        # Save the selected recipe as a PDF

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


if st.session_state.inventory_page == 'upload_inventory':
    asyncio.run(upload_inventory())
elif st.session_state.inventory_page == 'inventory_cocktail_info':
    get_inventory_cocktail_info()
elif st.session_state.inventory_page == 'display_inventory_recipe':
    display_recipe()

