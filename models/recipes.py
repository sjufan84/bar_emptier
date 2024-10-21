""" Recipe Pydantic Models """
from typing import List
from pydantic import Field, BaseModel

class Cocktail(BaseModel):
    name: str = Field(..., description='A creative name for the cockail', example='A Walk in the Clouds')
    ingredients: List[str] = Field(
        ..., description='The ingredients in the recipe.',
        example='2 oz Bourbon, 1/2 oz Simple Syrup, 2 dashes Angostura Bitters')
    directions: List[str] = Field(
        ..., description='The directions for making the recipe',
        example='Add all ingredients to a mixing glass and fill with ice.\
        Stir, and strain into a rocks glass filled with fresh ice. Garnish with an orange twist.')
    glass: str = Field(
        ..., description='The recommended type of glass for the recipe.', example='Rocks Glass'
    )
    garnish: str = Field(..., description='The garnish for the recipe', example='Orange Twist')
    fun_fact: str = Field(
        None, example='A fun fact about the Old Fashioned is the official cocktail of Louisville, Kentucky.',
        description='A fun and intriguing fact about the cocktail, a conversation starter, not just\
          a commonly known fact.  Should be a fact that is not obvious to someone who knows the cocktail.')
    description: str = Field(
        ..., example='This cocktail is an innovative take on the classic Old Fashioned, and will help you\
        use up your bourbon.', description='A short description of the recipe and why you\
        thought it was appropriate given the user\'s request.'
    )
    # image: str = Field(..., example='https:/www.thecocktaildb.com/images/media/drink/vrwquq1478252802.jpg')
    # video: str = Field(..., example='https://www.youtube.com/watch?v=J0o0E7eJkz4')
