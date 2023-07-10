# Importing the necessary libraries
import os
import openai
import streamlit as st
import os
import requests
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
import re
from redis import Redis as RedisStore
import json
import uuid





from dotenv import load_dotenv
load_dotenv()

# Get the OpenAI API key and org key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")

# Initialize a connection to the redis store
redis_store = RedisStore()

class CocktailIngredient(BaseModel):
    name: str = Field(description="Name of the ingredient")
    amount: float = Field(description="Amount of the ingredient")
    unit: str = Field(description="Unit of the ingredient")

# We want to create a parser object to parse the recipe into the variables we want using Pydantic
class CocktailRecipe(BaseModel):
    name: str = Field(description="Name of the cocktail recipe")
    ingredient_names: List[str] = Field(description="A list of the names of the ingredients in the cocktail.")
    ingredient_amounts: List[float] = Field(description="A list of the amounts of the ingredients in the cocktail.")
    ingredient_units: List[str] = Field(description="A list of the units of the ingredients in the cocktail.")
    instructions: List[str] = Field(description="Instructions for preparing the cocktail")
    garnish: str = Field(description="Garnish for the cocktail")
    glass: str = Field(description="Glass to serve the cocktail in")
    flavor_profile: str = Field(description="Flavor profile of the cocktail")

# Define a function to return a session id if the user does not have one,
# or to return the session id if the user already has one
def get_session_id():
    session_id = str(uuid.uuid4())
    return session_id



class RecipeService:
    def __init__(self, session_id : Optional[str] = None, recipe : CocktailRecipe = None):
        # If the session id is not provided, we will generate a new one
        if not session_id:
            self.session_id = get_session_id()
            self.recipe = recipe
        else:
            self.session_id = session_id
            # See if the recipe is already in redis
            recipe = self.load_recipe()
            if not recipe:
                # If the recipe is not in redis, we will create a new recipe
                self.recipe = recipe
           

    # Define a function to save the recipe to redis under the "recipe" key
    def save_recipe(self):  
        try:
            redis_store.set(f'{self.session_id}_recipe', json.dumps(self.recipe))
        except Exception as e:
            print(f"Failed to save recipe to Redis: {e}")

    # Define a function to load the recipe from redis
    def load_recipe(self):
        try:
            recipe_json = redis_store.get(f'{self.session_id}_recipe')
            if recipe_json:
                recipe_dict = json.loads(recipe_json)
                return recipe_dict
            else:
                return None
        except Exception as e:
            print(f"Failed to load recipe from Redis: {e}")
            return None

    # Define a function to allow the user to be able to send menu text to the API and build a recipe\
    # based on the menu text

    def text_cocktail_recipe(self, recipe: dict) -> str:
        ingredients = "\n".join(recipe['ingredients'])
        instructions = "\n".join(recipe['instructions'])
        garnish = recipe['garnish']
        glass = recipe['glass']
        flavor_profile = recipe['flavor_profile']

        return f"Name: {recipe['name']}\nIngredients:\n{ingredients}\nInstructions:\n{instructions}\nGarnish: {garnish}\nGlass: {glass}\nFlavor Profile: {flavor_profile}"
        


    def clean_output(self, output):
        # Remove trailing commas in the JSON string
        output = re.sub(r',\s*}', '}', output)
        output = re.sub(r',\s*\]', ']', output)
        return output


    # Define the function to call the openai API
    def get_cocktail_recipe(self, liquor, cocktail_type, cuisine, theme):
        
        # Instantiate the parser objects
        parser = PydanticOutputParser(pydantic_object=CocktailRecipe)
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
        # Iterate through different models for fallback
        for model in ["gpt-3.5-turbo-16k-0613", 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo-0613', 'gpt-3.5-turbo']:
            # Define the parameters for the API call
            params = {
                "model": model,
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
                continue
                

            # Clean and parse the recipe
            recipe = response.choices[0].message.content
            try:
                parsed_recipe = parser.parse(recipe)

                # Create the recipe object from the parsed recipe
                recipe = CocktailRecipe(**{
                    "name": parsed_recipe.name,
                    "ingredient_names": parsed_recipe.ingredient_names,
                    "ingredient_amounts": parsed_recipe.ingredient_amounts,
                    "ingredient_units": parsed_recipe.ingredient_units,
                    "instructions": parsed_recipe.instructions,
                    "garnish": parsed_recipe.garnish,
                    "glass": parsed_recipe.glass,
                    "flavor_profile": parsed_recipe.flavor_profile,
                })
                # Convert the recipe to a dictionary
                # Iterate through the ingredient_amounts and check for null values.  Also if the float ends in 0, remove the decimal
                recipe.ingredient_amounts = [float(amount) if amount else None for amount in recipe.ingredient_amounts]
                recipe.ingredient_amounts = [int(amount) if amount and amount.is_integer() else amount for amount in recipe.ingredient_amounts]
                ingredients = zip(recipe.ingredient_names, recipe.ingredient_amounts, recipe.ingredient_units)
                recipe = recipe.dict()
                recipe['ingredients'] = [f"{ingredient[1]} {ingredient[2]} {ingredient[0]}" for ingredient in ingredients]
                recipe['recipe_text'] = self.text_cocktail_recipe(recipe)
                self.recipe = recipe
                # Save the recipe to redis 
                self.save_recipe()
                # Return the recipe
                return recipe
            except Exception as e:
                print(f"Failed to parse recipe: {e}")
                continue

    # Create a function to generate a recipe based on the user's inventory if they have one uploaded
    def get_inventory_cocktail_recipe(self, liquor, cocktail_type, cuisine, theme):
        parser = PydanticOutputParser(pydantic_object=CocktailRecipe)
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
            "role": "user", "content": f"Please use the following format:\n{parser.get_format_instructions()}\n"
        }
        ]

        # Iterate through different models for fallback
        for model in ["gpt-3.5-turbo-16k-0613", 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo-0613', 'gpt-3.5-turbo']:
            # Define the parameters for the API call
            params = {
                "model": model,
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
                continue
                

                 # Clean and parse the recipe
            recipe = response.choices[0].message.content
            try:
                parsed_recipe = parser.parse(recipe)

                # Create the recipe object from the parsed recipe
                recipe = CocktailRecipe(**{
                    "ingredient_names": parsed_recipe.ingredient_names,
                    "ingredient_amounts": parsed_recipe.ingredient_amounts,
                    "ingredient_units": parsed_recipe.ingredient_units,
                    "name": parsed_recipe.name,
                    "instructions": parsed_recipe.instructions,
                    "garnish": parsed_recipe.garnish,
                    "glass": parsed_recipe.glass,
                    "flavor_profile": parsed_recipe.flavor_profile,
                })
                # Check for null values in the ingredient_amounts
                recipe.ingredient_amounts = [float(amount) if amount else None for amount in recipe.ingredient_amounts]
                recipe.ingredient_amounts = [int(amount) if amount and amount.is_integer() else amount for amount in recipe.ingredient_amounts]
                # Convert the recipe to a dictionary
                ingredients = zip(recipe.ingredient_names, recipe.ingredient_amounts, recipe.ingredient_units)
                recipe = recipe.dict()
                recipe['ingredients'] = [f"{ingredient[1]} {ingredient[2]} {ingredient[0]}" for ingredient in ingredients]
                recipe['recipe_text'] = self.text_cocktail_recipe(recipe)
                # Save the recipe to redis 
                self.save_recipe(recipe)
                # Return the recipe
                return recipe
            except Exception as e:
                print(f"Failed to parse recipe: {e}")
                continue

    # Define a function to cost out the recipe
    def cost_recipe(self, recipe):