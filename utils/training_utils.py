""" Cocktail helper functions """
import logging
from openai import OpenAIError
from dependencies import get_openai_client
from models.recipes import Cocktail
# Load the OpenAI client
client = get_openai_client()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

async def create_training_guide(cocktail : Cocktail):
    """ Create a training guide for a cocktail."""
    messages = [
        {
            "role": "system",
            "content": f"""You are a master mixologist who has
            helped a user generate a cocktail recipe {cocktail}.
            Tbey would like for you to help them generate a training guide for their staff.  This should be
            a "one page" guide that can be used to train staff during a pre-shift meeting or other training
            session.  The guide should include information
            such as the flavor profile of the cocktail, information
            about the ingredients, notes about the technique,
            and how they can upsell and explain the cocktail to
            their guests."""
        }
    ]
    try:
        logging.debug("Trying model: gpt-4o-mini")
        # Assuming client has an async method for chat completions
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.75,
            top_p=1,
            max_tokens=750,
        )
        training_response = response.choices[0].message.content
        logging.debug("Response: %s", training_response)
        return training_response
    except OpenAIError as e:
        logging.error("Error with model: %s. Error: %s", "gpt-4o-mini", e)

    except Exception as e:
        logging.error("Error with model: %s. Error: %s", "gpt-4o-mini", e)

    return None  # Return None or a default response if all models fail
