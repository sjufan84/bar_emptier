""" Cocktail helper functions """
import logging
from openai import OpenAIError
from models.recipes import Cocktail
from dependencies import get_openai_client

# Load the OpenAI client
client = get_openai_client()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("openai").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

async def create_cocktail(liqour : str, type: str, cuisine: str, theme: str):
    """ Create a cocktail recipe """
    messages = [
        {
            "role": "system",
            "content": f"""You are a master mixologist helping a user create an innovative
            and creative cocktail.  They are trying to use up their {liqour} and want to create
            a {type} cocktail that is inspired by {cuisine} and {theme}.  Create a unique,
            innovative, and creative recipe that fits their parameters and the provided schema."""
        }
    ]
    try:
        logger.debug("Creating cocktail recipe")
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=Cocktail,
        )
        cocktail_response = completion.choices[0].message.parsed
        logger.debug("Cocktail Response: %s", cocktail_response)
        return cocktail_response

    except OpenAIError as e:
        logger.error("OpenAI Error: %s", e)
        return None

    except Exception as e:
        logger.error("Error creating cocktail: %s", e)
        return None

    return None  # Return None or a default response if all models fail

async def convert_recipe_to_text(recipe: Cocktail) -> str:
    """ Convert a recipe to text """
    recipe_text = f'''{recipe.name}

    Ingredients:
    {recipe.ingredients}

    Directions:
    {recipe.directions}

    Garnish: {recipe.garnish}
    Glass: {recipe.glass}
    Description: {recipe.description}
    Fun Fact: {recipe.fun_fact}
    '''
    return recipe_text
