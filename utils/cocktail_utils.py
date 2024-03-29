""" Cocktail helper functions """
import logging
import json
from openai import OpenAIError
import streamlit as st
from models.recipes import Cocktail
from dependencies import get_openai_client

# Load the OpenAI client
client = get_openai_client()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("openai").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

if "current_model" not in st.session_state:
    st.session_state.current_model = "gpt-3.5-turbo-1106"

async def create_cocktail(liqour : str, type: str, cuisine: str, theme: str):
    """ Create a cocktail recipe """
    messages = [
        {
            "role": "system",
            "content": f"""You are a master mixologist helping a user create an innovative
            and creative cocktail.  They are trying to use up their {liqour} and want to create
            a {type} cocktail that is inspired by {cuisine} and {theme}.  Create a cocktail recipe
            as a JSON object following this schema:
            Cocktail Name (name):str A unique and descriptive title for the recipe.
            Ingredients (ingredients):List[str] A list of ingredients required for the recipe.
            Directions (directions): List[str] Step-by-step instructions for preparing the recipe.
            Glass (glass): str The type of glassware recommended for serving the recipe.
            Garnish (garnish): str An optional garnish for the recipe.
            Description (description): str A short description of the recipe and why you thought
            it was appropriate given the user's request.
            Fun Fact (fun_fact): Optional[str] An interesting fact about the recipe or its ingredients.

            Ensure that the recipe is presented in a clear and organized manner,
            adhering to the 'Cocktail' {Cocktail} class structure
            as outlined above."""
        }
    ]

    try:
        logger.debug("Creating cocktail recipe")
        # Assuming client has an async method for chat completions
        response = client.chat.completions.create(
            model=st.session_state.current_model,
            messages=messages,
            temperature=0.75,
            top_p=1,
            max_tokens=750,
            response_format={"type": "json_object"}
        )
        cocktail_response = response.choices[0].message.content
        logger.debug("Response: %s", cocktail_response)
        return json.loads(cocktail_response)

    except OpenAIError as e:
        logger.error("OpenAI Error: %s", e)
        return None

    return None  # Return None or a default response if all models fail

async def convert_recipe_to_text(recipe: dict) -> str:
    """ Convert a recipe to text """
    recipe_text = f'''{recipe["name"]}

    Ingredients:
    {recipe["ingredients"]}

    Directions:
    {recipe["directions"]}

    Garnish: {recipe["garnish"]}
    Glass: {recipe["glass"]}
    Description: {recipe["description"]}
    Fun Fact: {recipe["fun_fact"]}
    '''
    return recipe_text
