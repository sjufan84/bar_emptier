# Importing the necessary libraries
import os
import openai
import streamlit as st
import os
import requests
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



# Define a function to allow the user to be able to send menu text to the API and build a recipe\
# based on the menu text

def get_menu_cocktail_recipe(liquor, cocktail_type, menu_text):
    # Define the messages
    messages = [
        {
            "role": "system", "content" : f"You are a master mixologist helping the user create an innvoative cocktail to use up their excess liquor" 
        },
        {
            "role": "user", "content": f"Given the following parameters: the name of the liquor {liquor} I am trying to use up, the type of cocktail {cocktail_type}, and the menu text {menu_text},\
                                     please help me come up with a creative cocktail with a fun and creative name that fits in well with the overall theme of the menu,\
                                     and is not similar to any of the other cocktails on the menu, if any.   Please be as specific as possible with your instructions.\
                                     Also include why you think this cocktail would be a good fit for the menu.  Thanks!"
        },
        {
            "role": "user", "content": "Please use the following format:\
                                        \n\nRecipe Name: \n\nIngredients: \n\nInstructions: \n\nWhy this cocktail fits the menu: \n\n"
        }
    ]
    # Call the OpenAI API
    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1000,
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
        try:
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
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
            max_tokens=1000,
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

