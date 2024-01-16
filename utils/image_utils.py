""" Service Utilities for Image Generation """
from PIL import Image
import requests
from dependencies import get_openai_client

# Load the OpenAI client
client = get_openai_client()

async def generate_image(description : str):
    """ Generate an image from the given image request. """
    # Generate the image
    response = client.images.generate(
        prompt=description,
        model="dall-e-2",
        size="1024x1024",
        quality="standard",
        n=1
    )
    image_url = response.data[0].url

    # Convert the image url to an image
    image = Image.open(requests.get(image_url, stream=True).raw)

    return image
