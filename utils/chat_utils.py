# Importing the necessary libraries
import streamlit as st
import openai
import os
import json
import uuid
from typing import Optional
from enum import Enum
from redis import Redis as RedisStore
from utils.cocktail_functions import CocktailRecipe
from dotenv import load_dotenv
load_dotenv()

# Get the OpenAI API key and org key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")

# Initialize a connection to the redis store
redis_store = RedisStore()

# Establish the context which should be an enum with the following values: "recipe", "general_chat"
class Context(Enum):
    RECIPE = "recipe"
    GENERAL_CHAT = "general_chat"

# Define a class for the chat messages
class ChatMessage:
    # Define the init method
    def __init__(self, content, role):
        self.content = content
        self.role = role

# Define a class for the chat service -- this is the class we will use to track the chat history and save it to redis
class ChatService:
    def __init__(self, session_id : Optional[str] = None, recipe : Optional[CocktailRecipe] = None):
        # If the session id is not provided, we will generate a new one
        if not session_id:
            self.session_id = str(uuid.uuid4())
            self.chat_history = []
            self.recipe = None
        else:
            self.session_id = session_id
            # Get the chat history from redis
            self.chat_history = self.load_chat_history()
            # Get the recipe from redis
            self.recipe = recipe

    def load_chat_history(self):
        try:
            chat_history_json = redis_store.get(self.session_id)
            if chat_history_json:
                chat_history_dict = json.loads(chat_history_json)
                return [message for message in chat_history_dict]
            else:
                return []
        except Exception as e:
            print(f"Failed to load chat history from Redis: {e}")
            return []

    def load_recipe(self):
        try:
            return redis_store.get(f"{self.session_id}_recipe").decode("utf-8")
        except Exception as e:
            print(f"Failed to load recipe from Redis: {e}")
            return None

    def save_chat_history(self):
        try:
            # Save the chat history to redis
            chat_history_json = json.dumps(self.chat_history)
            redis_store.set(self.session_id, chat_history_json)
        except Exception as e:
            print(f"Failed to save chat history to Redis: {e}")
        return self.chat_history


    # Define a function to initialize the chat with an initial message.  We need to take in the
    # context and then generate the initial message based on that.  Context should be an enum with
    # the following values: "recipe", "general_chat"
    def initialize_chat(self, context: Context):
        # Check to see if the context is "recipe" -- if it is, we need to retrieve the
        # recipe from the session state and use that to generate the initial message
        if context == Context.RECIPE:
            initial_message = {
                                    "role": "system", 
                                    "content": f"""
                                    You are a master mixologist answering a user's questions 
                                    about the recipe {self.recipe} you created for them.  Your
                                    chat messages so far are {self.chat_history[1:]} 
                                    """
                                    }
        else:
            initial_message = {"role": "system", "content": f"You are a master mixologist answering\
                                   a user's questions about bartending."}
            
        second_message = {"role": "system", "content": "Your chat messages so far are:"}
        # Append the initial message to the chat history
        self.chat_history.append(initial_message)
        self.chat_history.append(second_message)

        # Save the chat history to redis
        self.save_chat_history()

        # Return the chat history
        return initial_message


    # Define a function to add a message to the chat history
    # This will take in a "role" string and a "content" string
    # Role must be one of the following: "system", "user", "ai"
    def add_message(self, role, content):
        # If the role is user, we will add a user message formatted as a HumanMessage
        if role == "user":
            message = {"role": "user", "content": content}
        # If the role is ai, we will add an ai message formatted as an AIMessage
        elif role == "ai":
            message = {"role": "assistant", "content": content}
        # If the role is system, we will add a system message formatted as a SystemMessage
        elif role == "system":
            message = {"role": "system", "content": content}
        # Append the message to the chat history
        self.chat_history.append(message)

        # Save the chat history to redis
        self.save_chat_history()

        #Save the chat history to redis
        return self.chat_history

    # Define a function to clear the chat history
    def clear_chat_history(self):
        self.chat_history = []
        self.save_chat_history()
        return self.chat_history

    # Define the function to answer any follow up questions the user has about the recipe
    def get_bartender_response(self, question: str, session_id: str):
        # Load the chat history from redis
        chat_service = ChatService(session_id)
        # Append the user's question to messages
        chat_service.add_message(role="user", content=question)
        chat_history = chat_service.load_chat_history()
        # Add the rest of the chat history to messages
        messages = chat_history
        # Define the models we want to iterate through
        models = ["gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613", "gpt-3.5-turbo"]
        # Iterate through the models and generate a response
        for model in models:
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages = messages,
                    max_tokens=750,
                    frequency_penalty=0.2,
                    presence_penalty=0.6,
                )
                bartender_response = response.choices[0].message.content
                # Append the bartender response to the chat history
                chat_service.add_message(role="ai", content=bartender_response)
                # Save the chat history to Redis
                chat_service.save_chat_history()

                return bartender_response

                

                
            except Exception as e:
                print(f"Failed to generate response with model {model}: {e}")
                continue


def get_training_bartender_response(question, recipe, guide):
    # Check to see if there is an inventory in the session state
    messages = [
    {
        "role": "system",
        "content": f"You are a master mixologist who has provided a recipe {recipe} for the user and a training guide {guide} about\
            which they would like to ask some follow up questions.  The conversation you have had so far is {st.session_state.history.messages}.\
            Please respond as a friendly bartender to help them with their questions."
    },
    {
        "role": "user",
        "content": f"Thanks for the recipe and the training guide!  I need to ask you a follow up question {question}."
    },
    ]

    # Use the OpenAI API to generate a recipe
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = messages,
            max_tokens=750,
            frequency_penalty=0.5,
            presence_penalty=0.75,
            temperature=1,
            n=1
        )
        st.session_state.response = response
        response = response.choices[0].message.content

    except:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages = messages,
            max_tokens=500,
            frequency_penalty=0.2,
            temperature = 1, 
            n=1, 
            presence_penalty=0.2,
        )
        st.session_state.response = response
        response = response.choices[0].message.content

    return response

