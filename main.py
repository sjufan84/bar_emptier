# This is the main demo file for the project.
# This project will use OpenAI to help the user create cocktail recipes to help them get rid of excess inventory.

# Importing the necessary libraries
import os
import openai
import streamlit as st
import os
import requests
from utils.save_recipes import save_recipe_as_pdf, get_recipe_pdf_download_link
from dotenv import load_dotenv
load_dotenv()

# Get the OpenAI API key and org key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")

# Initialize the session state
if "cocktail_name" not in st.session_state:
    st.session_state.cocktail_name = ""
if "recipe" not in st.session_state:
    st.session_state.recipe = ""
if "response" not in st.session_state:
    st.session_state.response = ""
if "cocktail_page" not in st.session_state:
    st.session_state.cocktail_page = "get_cocktail_info"

# Define the header
st.markdown('#### Bar Emptier:  The app that finally answers the question: What the hell am I going to do with these\
            27 bottles of Frangelico that someone accidentally ordered?')
st.markdown('---')

# Define the function to call the openai API
def get_cocktail_recipe(liquor, cocktail_type, cuisine, theme):
    # Define the messages
    messages = [
        {
            "role": "system", "content" : f"You are a master mixologist helping the user create an innvoative cocktail to use up their excess liquor" 
        },
        {
            "role": "user", "content": f"Given the following parameters: the name of the liquor {liquor} I am trying to use up, the type of cocktail {cocktail_type}, the type of cuisine {cuisine}\
                     I am looking to pair it with, and the theme {theme}, please help me come up with a creative cocktail with a fun and creative name that doesn't\
                        necessarily include the name of the spirit or the theme.   Please be as specific as possible with your instructions."
        },
        {
            "role": "user", "content": "Please use the following format:\
                                        \n\nRecipe Name: \n\nIngredients: \n\nInstructions: \n\n"
        }
    ]
    # Call the OpenAI API
    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=750,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        temperature=1,
        top_p=0.9,
        n=1,
        )

        recipe = response.choices[0].message.content
        st.session_state.recipe = recipe
        st.session_state.response = response


    except (requests.exceptions.RequestException, openai.error.APIError):
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        messages=messages,
        max_tokens=750,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        temperature=1,
        top_p=0.9,
        n=1,
    )

        recipe = response.choices[0].message.content
        st.session_state.response = response
        st.session_state.recipe = recipe

    # Return the recipe
    return recipe

# Define the function to get the information about the cocktail
def get_cocktail_info():
    # Build the form 
    with st.form('bar_emptier'):
        # Start by getting the input for the liquor that the user is trying to use up
        liquor = st.text_input('What liquor are you trying to use up?')
        # Allow the user to choose what type of cocktail from "Classic", "Craft", "Standard"
        cocktail_type = st.selectbox('What type of cocktail are you looking for?', ['Classic', 'Craft', 'Standard'])
        # Allow the user the option to select a type of cuisine to pair it with
        cuisine = st.selectbox('What type of cuisine, if any, are you looking to pair it with?', ['American',\
                                'Mexican', 'Italian', 'French', 'Chinese', 'Japanese', 'Thai', 'Indian', 'Greek', 'Spanish', 'Korean', 'Vietnamese',\
                                'Mediterranean', 'Middle Eastern', 'Caribbean', 'British', 'German', 'Irish', 'African', 'Moroccan', 'Nordic', 'Eastern European',\
                                'Jewish', 'South American', 'Central American', 'Australian', 'New Zealand', 'Pacific Islands', 'Canadian', 'Other'])
        # Allow the user to enter a theme for the cocktail if they want
        theme = st.text_input('What theme, if any, are you looking for? (e.g. "tiki", "holiday", "summer", etc.)')

        # Create the submit button
        cocktail_submit_button = st.form_submit_button(label='Create your cocktail!')
        if cocktail_submit_button:
            with st.spinner('Creating your cocktail recipe.  This may take a minute...'):
                get_cocktail_recipe(liquor, cocktail_type, cuisine, theme)
                st.session_state.cocktail_page = "display_recipe"
                st.experimental_rerun()

def display_recipe():
    st.markdown('##### Here is your recipe! 🍸🍹')
    st.write(st.session_state.recipe)

    # Save the selected recipe as a PDF
    pdf_path = save_recipe_as_pdf(st.session_state.recipe, f"my_recipe.pdf")

    # Generate a download link for the saved PDF
    download_link = get_recipe_pdf_download_link(pdf_path, f"my_recipe.pdf")

    # Display the download link
    st.markdown(download_link, unsafe_allow_html=True)
   
    # Create a "Create another cocktail" button
    create_another_cocktail_button = st.button('Create another cocktail!')
    if create_another_cocktail_button:
        st.session_state.cocktail_page = "get_cocktail_info"
        st.experimental_rerun()

if st.session_state.cocktail_page == "get_cocktail_info":
    get_cocktail_info()
elif st.session_state.cocktail_page == "display_recipe":
    display_recipe()