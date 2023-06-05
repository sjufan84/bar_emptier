# Importing the necessary libraries
import os
import openai
import streamlit as st
import os
import requests
from langchain.output_parsers import PydanticOutputParser, RetryWithErrorOutputParser
from pydantic import BaseModel, Field
from typing import List
import re



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
if "recipe_text" not in st.session_state:
    st.session_state.recipe_text = ""
if "response" not in st.session_state:
    st.session_state.response = ""
if "cocktail_page" not in st.session_state:
    st.session_state.cocktail_page = "get_cocktail_info"
if "parsed_recipe" not in st.session_state:
    st.session_state.parsed_recipe = None
if "cocktail_name" not in st.session_state:
    st.session_state.cocktail_name = ""
if "ingredients" not in st.session_state:
    st.session_state.ingredients = []
if "instructions" not in st.session_state:
    st.session_state.instructions = []
if "garnish" not in st.session_state:
    st.session_state.garnish = ""
if "glass" not in st.session_state:
    st.session_state.glass = ""
if "flavor_profile" not in st.session_state:
    st.session_state.flavor_profile = ""
if "inventory_ingredients" not in st.session_state:
    st.session_state.inventory_ingredients = []
if "other_ingredients" not in st.session_state:
    st.session_state.other_ingredients = []


# We want to create a parser object to parse the recipe into the variables we want using Pydantic
class CocktailRecipe(BaseModel):
    name: str = Field(description="Name of the cocktail recipe")
    ingredients: List[str] = Field(description="List of ingredients in the cocktail")
    instructions: List[str] = Field(description="Instructions for preparing the cocktail")
    garnish: str = Field(description="Garnish for the cocktail")
    glass: str = Field(description="Glass to serve the cocktail in")
    flavor_profile: str = Field(description="Flavor profile of the cocktail")

# We will create a separate parser for inventory cocktails
class InventoryCocktailRecipe(BaseModel):
    name: str = Field(description="Name of the cocktail recipe")
    ingredients: List[tuple] = Field(description="List of tuples of the ingredients in the cocktail with the amounts as a float and the names of the ingredients as a string.")
    # ingredient_amounts: List[float] = Field(description="Amounts of each ingredient in the cocktail")
    instructions: List[str] = Field(description="Instructions for preparing the cocktail")
    garnish: str = Field(description="Garnish for the cocktail")
    glass: str = Field(description="Glass to serve the cocktail in")
    flavor_profile: str = Field(description="Flavor profile of the cocktail")

# Instantiate the parser objects
parser = PydanticOutputParser(pydantic_object=CocktailRecipe)
inventory_parser = PydanticOutputParser(pydantic_object=InventoryCocktailRecipe)




# Define a function to allow the user to be able to send menu text to the API and build a recipe\
# based on the menu text

def text_cocktail_recipe(recipe: CocktailRecipe) -> str:
    ingredients = "\n".join(recipe.ingredients)
    instructions = "\n".join(recipe.instructions)
    formatted_recipe = (
        f"Recipe Name: {recipe.name}\n\n"
        f"Ingredients:\n{ingredients}\n\n"
        f"Instructions:\n{instructions}\n\n"
        f"Garnish: {recipe.garnish}\n\n"
        f"Glass: {recipe.glass}"
    )
    return formatted_recipe

def text_inventory_cocktail_recipe(recipe: InventoryCocktailRecipe) -> str:
    instructions = "\n".join(recipe.instructions)
    ingredients = "\n".join([f"{ingredient[0]} {ingredient[1]}" for ingredient in recipe.ingredients])
    formatted_recipe = (
        f"Recipe Name: {recipe.name}\n\n"
        f"Ingredients:\n{ingredients}\n\n"
        f"Instructions:\n{instructions}\n\n"
        f"Garnish: {recipe.garnish}\n\n"
        f"Glass: {recipe.glass}"
    )
    return formatted_recipe

def clean_output(output):
    # Remove trailing commas in the JSON string
    output = re.sub(r',\s*}', '}', output)
    output = re.sub(r',\s*\]', ']', output)
    return output


def get_menu_cocktail_recipe(liquor, cocktail_type, theme):
    # Define the messages
    # If there is a food menu in session state, add a message to the messages list
    if st.session_state.food_menu != "":
        food_menu_message = {
            "role": "user", "content": f"Food Menu: {st.session_state.food_menu}"
        }
    # If there is a drink menu in session state, add a message to the messages list
    if st.session_state.drink_menu != "":
        drink_menu_message = {
            "role": "user", "content": f"Drink Menu: {st.session_state.drink_menu}"
        }
        

    messages = [
        {
            "role": "system", "content" : f"You are a master mixologist helping the user create an innvoative cocktail to use up their excess liquor" 
        },
        {
            "role": "user", "content": f"Given the following parameters: the name of the liquor {liquor} I am trying to use up, the type of cocktail {cocktail_type}, and the theme {theme},\
                                    please help me come up with a creative cocktail that features the {liquor} with a fun and creative name that fits in well with the overall theme of the food menu referenced above, if any\
                                    and is not similar to any of the other cocktails on the drink menu referenced above, if any.   Please be as specific as possible with your instructions.\
                                    Also include why you think this cocktail works with the cocktail and / or / food menus.  Thanks!"
        },
        {
             "role": "user", "content": f"Please use the following format:\n{parser.get_format_instructions()}\n"
        }
    ]

    # If there is a drink message or food message or both, add them to the messages list after the first message
    if st.session_state.food_menu != "" and st.session_state.drink_menu != "":
        messages.insert(1, food_menu_message)
        messages.insert(2, drink_menu_message)
    elif st.session_state.food_menu != "":
        messages.insert(1, food_menu_message)
    elif st.session_state.drink_menu != "":
        messages.insert(1, drink_menu_message)

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
        parsed_recipe = parser.parse(recipe)
        st.session_state.recipe_text = text_cocktail_recipe(parsed_recipe)
        st.session_state.parsed_recipe = parsed_recipe
        st.session_state.cocktail_name = parsed_recipe.name
        st.session_state.ingredients = parsed_recipe.ingredients
        st.session_state.instructions = parsed_recipe.instructions
        st.session_state.garnish = parsed_recipe.garnish
        st.session_state.glass = parsed_recipe.glass
        st.session_state.flavor_profile = parsed_recipe.flavor_profile

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
            parsed_recipe = parser.parse(recipe)
            st.session_state.recipe_text = text_cocktail_recipe(parsed_recipe)
            st.session_state.parsed_recipe = parsed_recipe
            st.session_state.cocktail_name = parsed_recipe.name
            st.session_state.ingredients = parsed_recipe.ingredients
            st.session_state.instructions = parsed_recipe.instructions
            st.session_state.garnish = parsed_recipe.garnish
            st.session_state.glass = parsed_recipe.glass
            st.session_state.flavor_profile = parsed_recipe.flavor_profile



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
        st.session_state.recipe = recipe
        st.session_state.response = response
        parsed_recipe = parser.parse(recipe)
        st.session_state.parsed_recipe = parsed_recipe
        st.session_state.cocktail_name = parsed_recipe.name
        st.session_state.ingredients = parsed_recipe.ingredients
        st.session_state.instructions = parsed_recipe.instructions
        st.session_state.garnish = parsed_recipe.garnish
        st.session_state.glass = parsed_recipe.glass
        st.session_state.recipe_text = text_cocktail_recipe(parsed_recipe)
        st.session_state.flavor_profile = parsed_recipe.flavor_profile

            

    # Return the recipe
    return recipe



# Define the function to call the openai API
def get_cocktail_recipe(liquor, cocktail_type, cuisine, theme):
    # Define the messages
    messages = [
        {
            "role": "system", 
            "content" : f"You are a master mixologist helping the user create an innovative cocktail to use up their excess liquor" 
        },
        {
            "role": "user", 
            "content": f"Given the following parameters: the name of the liquor {liquor} I am trying to use up, the type of cocktail {cocktail_type}, the type of cuisine {cuisine}\
                    I am looking to pair it with, and the theme {theme}, please help me come up with a creative cocktail featuring {liquor} with a fun and creative name that doesn't\
                    necessarily include the name of the spirit or the theme.   Please be as specific as possible with your instructions."
        },
        {
             "role": "user", 
             "content": f"Please use the following format:\n{parser.get_format_instructions()}\n"
        }
    ]

    # Define the parameters for the API call
    params = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 750,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "temperature": 1,
        "top_p": 0.9,
        "n": 1,
    }
    
    # Call the OpenAI API and handle exceptions
    try:
        response = openai.ChatCompletion.create(**params)
    except (requests.exceptions.RequestException, openai.error.APIError):
        params["model"] = "gpt-3.5-turbo-0301"
        response = openai.ChatCompletion.create(**params)

    # Clean and parse the recipe
    recipe = response.choices[0].message.content
    clean_recipe = clean_output(recipe)
    try:
        parsed_recipe = parser.parse(clean_recipe)
    except Exception as e:
        with st.spinner("Error parsing recipe. Retrying..."):
            parsed_recipe = RetryWithErrorOutputParser().parse(clean_recipe)


    # Update the session state
    st.session_state.update({
        "recipe": recipe,
        "response": response,
        "parsed_recipe": parsed_recipe,
        "cocktail_name": parsed_recipe.name,
        "ingredients": parsed_recipe.ingredients,
        "instructions": parsed_recipe.instructions,
        "garnish": parsed_recipe.garnish,
        "glass": parsed_recipe.glass,
        "recipe_text": text_cocktail_recipe(parsed_recipe),
        "flavor_profile": parsed_recipe.flavor_profile,
    })

    # Return the recipe
    return recipe

# Create a function to generate a recipe based on the user's inventory if they have one uploaded
def get_inventory_cocktail_recipe(liquor, cocktail_type, cuisine, theme):
    messages = [
    {
        "role": "system", "content" : f"You are a master mixologist helping the user create an innvoative cocktail to use up their excess liquor" 
    },
    {   
        "role": "user", "content": f"Given the following parameters: the name of the liquor {liquor} I am trying to use up, the type of cocktail {cocktail_type}, the theme {theme},\
                                and the style of cuisine {cuisine} to pair it with, please help me come up with a creative cocktail featuring {liquor} with a fun and creative name that doesn't necessarily include the name of the spirit or the theme.\
                                Please prioritize using the ingredients I have on hand in {st.session_state.inventory_list}, but you can include other ingredients as well if needed.\
                                Please be as specific as possible with your instructions."
    },
    {
        "role": "user", "content": f"Please use the following format:\n{inventory_parser.get_format_instructions()}\n"
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

        # Clean and parse the recipe
        recipe = response.choices[0].message.content
        clean_recipe = clean_output(recipe)
        try:
            parsed_recipe = inventory_parser.parse(clean_recipe)
            st.session_state.recipe = recipe
            st.session_state.response = response
            parsed_recipe = inventory_parser.parse(recipe)
            st.session_state.recipe_text = text_inventory_cocktail_recipe(parsed_recipe)
            st.session_state.parsed_recipe = parsed_recipe
            st.session_state.cocktail_name = parsed_recipe.name
            st.session_state.instructions = parsed_recipe.instructions
            st.session_state.garnish = parsed_recipe.garnish
            st.session_state.glass = parsed_recipe.glass
            st.session_state.flavor_profile = parsed_recipe.flavor_profile
            st.session_state.ingredients = parsed_recipe.ingredients
        except Exception as e:
            with st.spinner("Error parsing recipe. Retrying..."):
                parsed_recipe = RetryWithErrorOutputParser(parser = inventory_parser).parse(clean_recipe)
                st.session_state.recipe = recipe
                st.session_state.response = response
                parsed_recipe = inventory_parser.parse(recipe)
                st.session_state.recipe_text = text_inventory_cocktail_recipe(parsed_recipe)
                st.session_state.parsed_recipe = parsed_recipe
                st.session_state.cocktail_name = parsed_recipe.name
                st.session_state.instructions = parsed_recipe.instructions
                st.session_state.garnish = parsed_recipe.garnish
                st.session_state.glass = parsed_recipe.glass
                st.session_state.flavor_profile = parsed_recipe.flavor_profile
                st.session_state.ingredients = parsed_recipe.ingredients

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
            clean_recipe = clean_output(recipe)
            try:
                parsed_recipe = inventory_parser.parse(clean_recipe)
                st.session_state.recipe = recipe
                st.session_state.response = response
                parsed_recipe = inventory_parser.parse(recipe)
                st.session_state.recipe_text = text_inventory_cocktail_recipe(parsed_recipe)
                st.session_state.parsed_recipe = parsed_recipe
                st.session_state.cocktail_name = parsed_recipe.name
                st.session_state.instructions = parsed_recipe.instructions
                st.session_state.garnish = parsed_recipe.garnish
                st.session_state.glass = parsed_recipe.glass
                st.session_state.flavor_profile = parsed_recipe.flavor_profile
                st.session_state.ingredients = parsed_recipe.ingredients
            except Exception as e:
                with st.spinner("Error parsing recipe. Retrying..."):
                    parsed_recipe = RetryWithErrorOutputParser(parser = inventory_parser).parse(clean_recipe)
                    st.session_state.recipe = recipe
                    st.session_state.response = response
                    parsed_recipe = inventory_parser.parse(recipe)
                    st.session_state.recipe_text = text_inventory_cocktail_recipe(parsed_recipe)
                    st.session_state.parsed_recipe = parsed_recipe
                    st.session_state.cocktail_name = parsed_recipe.name
                    st.session_state.instructions = parsed_recipe.instructions
                    st.session_state.garnish = parsed_recipe.garnish
                    st.session_state.glass = parsed_recipe.glass
                    st.session_state.flavor_profile = parsed_recipe.flavor_profile
                    st.session_state.ingredients = parsed_recipe.ingredients




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
            clean_recipe = clean_output(recipe)
            try:
                parsed_recipe = inventory_parser.parse(clean_recipe)
                st.session_state.recipe = recipe
                st.session_state.response = response
                parsed_recipe = inventory_parser.parse(recipe)
                st.session_state.recipe_text = text_inventory_cocktail_recipe(parsed_recipe)
                st.session_state.parsed_recipe = parsed_recipe
                st.session_state.cocktail_name = parsed_recipe.name
                st.session_state.instructions = parsed_recipe.instructions
                st.session_state.garnish = parsed_recipe.garnish
                st.session_state.glass = parsed_recipe.glass
                st.session_state.flavor_profile = parsed_recipe.flavor_profile
                st.session_state.ingredients = parsed_recipe.ingredients
            except Exception as e:
                with st.spinner("Error parsing recipe. Retrying..."):
                    parsed_recipe = RetryWithErrorOutputParser(parser = inventory_parser).parse(clean_recipe)
                    st.session_state.recipe = recipe
                    st.session_state.response = response
                    parsed_recipe = inventory_parser.parse(recipe)
                    st.session_state.recipe_text = text_inventory_cocktail_recipe(parsed_recipe)
                    st.session_state.parsed_recipe = parsed_recipe
                    st.session_state.cocktail_name = parsed_recipe.name
                    st.session_state.instructions = parsed_recipe.instructions
                    st.session_state.garnish = parsed_recipe.garnish
                    st.session_state.glass = parsed_recipe.glass
                    st.session_state.flavor_profile = parsed_recipe.flavor_profile
                    st.session_state.ingredients = parsed_recipe.ingredients


            
    return recipe
