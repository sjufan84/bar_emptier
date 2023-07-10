# Importing the necessary libraries
import os
import openai
import streamlit as st
import os
import requests
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate
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
    ingredient_amounts: List[float or int] = Field(description="A list of the amounts of the ingredients in the cocktail.")
    ingredient_units: List[str] = Field(description="A list of the units of the ingredients in the cocktail.")
    instructions: List[str] = Field(description="Instructions for preparing the cocktail")
    garnish: str = Field(description="Garnish for the cocktail")
    glass: str = Field(description="Glass to serve the cocktail in")
    flavor_profile: str = Field(description="Flavor profile of the cocktail")

    # Define a function to return the ingredients in a list of tuples
    @property
    def ingredients(self):
        return list(zip(self.ingredient_names, self.ingredient_amounts, self.ingredient_units))

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
            redis_store.set(f'{self.session_id}_recipe', json.dumps(self.recipe.dict()))
        except Exception as e:
            print(f"Failed to save recipe to Redis: {e}")

    # Define a function to load the recipe from redis and convert it to a CocktailRecipe object
    def load_recipe(self):
        try:
            recipe = redis_store.get(f'{self.session_id}_recipe')
            if recipe:
                recipe = json.loads(recipe)
                return CocktailRecipe(**recipe)
            else:
                return None
        except Exception as e:
            print(f"Failed to load recipe from Redis: {e}")
            return None
        
    # Define a function to check to make sure all of the fields are filled out
    def check_recipe(self):
        # Define the fields we want to check
        fields = ["name", "ingredient_names", "ingredient_amounts", "ingredient_units", "instructions", "garnish", "glass", "flavor_profile"]
        # Iterate through the fields
        for field in fields:
            # If the field is not filled out, return False
            if not getattr(self.recipe, field):
                return False
        # If all of the fields are filled out, return True
        return True



    # Define the function to call the openai API
    def get_cocktail_recipe(self, liquor : str, theme : str, cuisine : str, cocktail_type : str) -> CocktailRecipe:
        parser = PydanticOutputParser(pydantic_object=CocktailRecipe)
        
        # Define the first system message.  This let's the model know what type of output\
        # we are expecting and in what format it needs to be in.
        prompt = PromptTemplate(
            template = "You are a master mixologist helping a user use up the excess liquor {liquor}\
                        they have in their inventory by using it in a creative and innovate cocktail recipe.\
                        The recipe should be based around a theme {theme}, cuisine type {cuisine},\
                        and the type of cocktail {cocktail_type} the user wants to make.\
                        The recipe should include the ingredient names, the ingredient amounts,\
                             the ingredient units, the garnish, the class, and a flavor profile. The cocktail should be returned in this format{format_instructions}.",
            input_variables = ["liquor", "theme", "cuisine", "cocktail_type"],
            partial_variables = {"format_instructions": parser.get_format_instructions()}
        )

        # Generate the system message prompt
        system_message_prompt = SystemMessagePromptTemplate(prompt=prompt)

        # Define the user message.  This is the message that will be passed to the model to generate the recipe.
        human_template = "Create a delcious cocktail recipe to help me use up my excess inventory."
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)    
        
        # Create the chat prompt template
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        # format the messages to feed to the model
        messages = chat_prompt.format_prompt(liquor=liquor, theme=theme, cuisine=cuisine, cocktail_type=cocktail_type).to_messages()

        # Create a list of models to loop through in case one fails
        models = ["gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k"]

        # Loop through the models and try to generate the recipe
        for model in models:
            try:
                chat = ChatOpenAI(model_name = model, temperature = 1, max_retries=3)

                recipe = chat(messages).content

                try:
                    parsed_recipe = parser.parse(recipe)
                    self.recipe = parsed_recipe
                    # We need to create a "recipe_text" field for the recipe to be returned to the user
                    # This will be a string that includes all of the recipe information so that we can
                    # Use it for functions downstream
                    self.save_recipe()
                    # Return the recipe
                    return parsed_recipe
                except Exception as e:
                    print(f"Failed to parse recipe: {e}")
            except (requests.exceptions.RequestException, openai.error.APIError):
                continue
                    


                    
            

    # Create a function to generate a recipe based on the user's inventory if they have one uploaded
    def get_inventory_cocktail_recipe(self, inventory_list, liquor, cocktail_type, cuisine, theme):
        parser = PydanticOutputParser(pydantic_object=CocktailRecipe)
        messages = [
        {
             "role": "system", 
                "content" : f"You are a master mixologist helping the user create an innovative cocktail to use up their excess liquor, {liquor}.\
                            Return the recipe in the following format:\n{parser.get_format_instructions()}\n.  Make sure all of the fields including garnish, flavor profile\
                                and glass are filled out before returning the recipe." 
        },
        {   
            "role": "user", "content": f"Given the following parameters: the name of the liquor {liquor} I am trying to use up, the type of cocktail {cocktail_type}, the theme {theme},\
                                    and the style of cuisine {cuisine} to pair it with, please help me come up with a creative cocktail featuring {liquor} with a fun and creative name that doesn't necessarily include the name of the spirit or the theme.\
                                    Please prioritize using the ingredients I have on hand in {inventory_list}, but you can include other ingredients as well if needed.\
                                    Please be as specific as possible with your instructions."
        },
        {
            "role":"user", "content": f"Please use the following format:\n{parser.get_format_instructions()}\n. and make sure all of the fields are filled out."
        }
        ]

        # Iterate through different models for fallback
        for model in ["gpt-3.5-turbo-16k-0613", 'gpt-3.5-turbo-0613', 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo']:
            # Define the parameters for the API call
            params = {
                "model": model,
                "messages": messages,
                "max_tokens": 1250,
                "frequency_penalty": 0.5,
                "presence_penalty": 0.5,
                "temperature": 1,
                "top_p": 0.9,
                "n": 1,
            }
            
            # Call the OpenAI API and handle exceptions
            try:
                response = openai.ChatCompletion.create(**params)
                recipe = response.choices[0].message.content
                try:
                    parsed_recipe = parser.parse(recipe)
                    
                    # Save the recipe to redis
                    self.recipe = parsed_recipe
                     # Verify that all of the fields are filled out
                    if not self.check_recipe():
                        raise Exception("Not all of the fields are filled out")
                    # Save the recipe to redis 
                    self.save_recipe()
                    # Return the recipe
                    return recipe
                except Exception as e:
                    print(f"Failed to parse recipe: {e}")
            except (requests.exceptions.RequestException, openai.error.APIError):
                continue
                            

    # Define a function to cost out the recipe
    def cost_recipe(self, recipe):
        ""