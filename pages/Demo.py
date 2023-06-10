# Demonstrating the flow of the application and its features, with a demo using an example inventory that allows the user
# to select a spirit from their inventory and center their cocktail around it.  We will then supply the model with
# their other specifications and a cocktail will be created using the user's specifications and the spirit they selected.
# After the recipe is generated, we will display the recipe and then cost out the drink by multiplying the Cost per oz of each ingredient 
# from our inventory by the amount of each ingredient in the recipe.  We will then caculate the total revenue generated from the amount of the
# spirit selected vs. the cost of the amount sitting in inventory and display it to the user.   This is for demonstration purposes only
# so it will be used in a screen video capture as a demo, for live demos, and to distribute to potential investors and or initial development partners.

# Importing the necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
from utils.inventory_functions import process_file
from utils.image_utils import generate_image
from utils.cocktail_functions import get_inventory_cocktail_recipe
import asyncio
from streamlit_extras.switch_page_button import switch_page
from langchain.output_parsers import PydanticOutputParser, RetryWithErrorOutputParser
from pydantic import BaseModel, Field
from typing import List
import re
import os
from dotenv import load_dotenv
import openai
import requests

load_dotenv()


# Get the OpenAI API key and org key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")


# Initialize the session state
def init_inventory_session_variables():
    # Initialize session state variables
    session_vars = [
        'inventory_page', 'inventory_csv_data', 'df', 'inventory_list', 'image_generated', 'demo_page', 'chosen_spirit', 'estimated_cost', 'recipe_cost',\
                         'cost_estimates', 'total_ni_cost', 'num_drinks', 'total_cost', 'total_drinks_cost', 'inventory_ingredients', 'ni_ingredients'
    ]
    default_values = [
        'upload_inventory', [], pd.DataFrame(), [], False, 'upload_inventory', '', 0.00, [], [], 0.00, 0.00, 0.00, 0.00, [], []
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

def reset_inventory_session_variables():
    # Session state variables and their default values
    session_vars = [
        'image_generated', 'chosen_spirit', 'estimated_cost', 'recipe_cost',\
                         'cost_estimates', 'total_ni_cost', 'num_drinks', 'total_cost', 'total_drinks_cost', 'inventory_ingredients', 'ni_ingredients'
    ]
    default_values = [
        False, '', 0.00, [], [], 0.00, 0.00, 0.00, 0.00, [], []
    ]

    # Reset session state variables to their default values
    for var, default_value in zip(session_vars, default_values):
        st.session_state[var] = default_value


init_inventory_session_variables()

# We want to create a parser object to parse the estimated costs of the non-inventory ingredients into the variables we want using Pydantic
class CostEstimate(BaseModel):
    total_ni_cost: float = Field(description="The sum of the total cost of the ingredients in the cocktail.")
    
# Create the parser object for the estimated cost of the non-inventory ingredients
cost_parser = PydanticOutputParser(pydantic_object = CostEstimate)
    
# A function to estimate the cost of non-inventory items in a cocktail by calling gpt-3.5
def estimate_cost_of_non_inventory_items(ingredients):
    
    messages = [
    {
        "role": "system", "content" : f"You are a bar manager helping the user estimate the cost of ingredients {ingredients} in a cocktail you created for them.\
            The first value of the tuple is the amount in oz, and then second value is the ingredient.  You can just estimate the cost of the ingredients,\
            based on your training data, it does not need to be exact." 
    },
    {   
        "role": "user", "content": f"Given the ingredients and their amounts in {ingredients}, can you help me estimate the total cost of the ingredients?"
    },
    {
        "role": "user", "content": f"Please use the following format:\n{cost_parser.get_format_instructions()}\n"
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

        response = response.choices[0].message.content
        parsed_reponse = cost_parser.parse(response)
        st.session_state.total_ni_cost = parsed_reponse.total_ni_cost
        

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

            response = response.choices[0].message.content
            parsed_reponse = cost_parser.parse(response)
            st.session_state.total_ni_cost = parsed_reponse.total_ni_cost




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

            response = response.choices[0].message.content
            parsed_reponse = cost_parser.parse(response)
            st.session_state.total_ni_cost = parsed_reponse.total_ni_cost


            
    return response

# Define a function to cost out the recipe
def cost_out_recipe():

    # Muliply the cost of each ingredient by the value in the "Cost per oz" column in the dataframe and save it to a new list of tuples
    ingredients_cost = []
    total_cost = 0
    # Remove any duplicates from the inventory_ingredients session state variable
    st.session_state.inventory_ingredients = list(set(st.session_state.inventory_ingredients))
    # Remove any duplicates from the ni_ingredients session state variable
    st.session_state.ni_ingredients = list(set(st.session_state.ni_ingredients))

    # Get the cost of the inventory ingredients
    for ingredient in st.session_state.inventory_ingredients:
        st.write(ingredient)
        ingredient_cost_per_oz = st.session_state.df.loc[st.session_state.df['Name'].str.lower() == ingredient[1].lower(), 'Cost per oz'].values[0]
        recipe_ingredient_cost = ingredient_cost_per_oz * ingredient[0]
        ingredients_cost.append((f'{ingredient[0]} oz {ingredient[1]}', recipe_ingredient_cost))
        total_cost += recipe_ingredient_cost
    # Convert the second value of the tuple to a float with two decimal places and a dollar sign
    for i in range(len(ingredients_cost)):
        ingredients_cost[i] = (ingredients_cost[i][0], f'{round(ingredients_cost[i][1], 2)}')
    
    # Call the function to get the cost of the non-inventory ingredients
    estimate_cost_of_non_inventory_items(st.session_state.ni_ingredients)
    # Append the cost of the non-inventory ingredients to the list of tuples
    ingredients_cost.append((f'Estimated total cost of other ingredients:', f'{round(st.session_state.total_ni_cost, 2)}'))

    # Add the cost of the non-inventory ingredients to the total cost
    total_cost += st.session_state.total_ni_cost

    # Get the total number of drinks we can make with the selected spirit by dividing the total amount of the spirit in the "Total amount (oz)" column by the amount of the spirit in the recipe
    st.session_state.num_drinks = st.session_state.df.loc[st.session_state.df['Name'].str.lower() == st.session_state.chosen_spirit.lower(), 'Total Amount (oz)'].values[0] / st.session_state.ingredients[0][0]
    
    # Round the number of drinks to the nearest integer
    st.session_state.num_drinks = round(st.session_state.num_drinks)
    
    # Append the total cost of the recipe to the list of tuples
    ingredients_cost.append((f'Total cost of recipe:', f'{round(total_cost, 2)}'))

    # Set the total_cost session state variable to the total cost of the recipe
    st.session_state.total_cost = total_cost

    # Create a "total_drinks_cost" that is the total cost of the recipe * the number of drinks we can make with the selected spirit
    total_drinks_cost = total_cost * st.session_state.num_drinks
    st.session_state.total_drinks_cost = total_drinks_cost
    
    # Return the list of tuples
    return ingredients_cost
    

# Create the function to allow the user to upload their inventory.  We will borrow this from the "Inventory Cocktails" page
async def upload_inventory():
    # Set the page title
    st.markdown('''
    <div style = text-align:center>
    <h3 style = "color: black;">Upload your inventory</h3>
    <h5 style = "color: #7b3583;">The first column of your file should contain the name of the spirit\
        and the second column should contain the quantity of that spirit that you have in stock.\
        By uploading your inventory, you are allowing the model to prioritize using up ingredients you already have on hand when suggesting cocktails.</h5>
    </div>
    ''', unsafe_allow_html=True)
    # Create a file uploader
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx', 'xls'])
    if uploaded_file:
        upload_file_button = st.button('Upload File and Continue to Cocktail Creation', use_container_width=True, type = 'secondary')
        # If the user clicks the upload file button, process the file
        if upload_file_button:
            with st.spinner('Converting and formatting your file...'):
                # Use the await keyword to wait for the file to be processed
                st.session_state.df = await process_file(uploaded_file)
                # Insert a "Use in Cocktail" column as the first column and set it to False for all rows
                st.session_state.df.insert(0, "Use in Cocktail", False)
                st.session_state.demo_page = "choose_spirit"
                st.experimental_rerun()
    else:
        st.warning('Please upload a file to continue')

# Define a function that will allow the user to select the spirit they want to use in their cocktail
# We will use the new st.data_editor library to allow for dynamic display of the inventory dataframe
# and the ability to let the user interact with it and select the spirit from their inventory
def choose_spirit():
    # Set the page title
    st.markdown('''
    <div style = text-align:center>
    <h3>Select the spirit you want to use in your cocktail</h3>
    </div>
    ''', unsafe_allow_html=True)

    edit_df = st.data_editor(
        st.session_state.df,
        column_config={
        "Use in Cocktail": st.column_config.CheckboxColumn(
            "Use in Cocktail?",
            help="Check this box if you want to use this spirit in your cocktail",
            default=False,
        )
    },
    disabled=["widgets"],
    hide_index=True,
    key="data_editor"
)
    # Create a button to display the 'data_editor' session_state variable
    # This will allow us to see the changes the user makes to the dataframe
    # and will allow us to use the data to create the cocktail
    
    # Check to make sure only one of the "Use in Cocktail" checkboxes is checked, otherwise display an error message
    if edit_df['Use in Cocktail'].sum() == 1:
        display_data_editor_button = st.button(f'Create a cocktail using {edit_df[edit_df["Use in Cocktail"] == True]["Name"].values[0]}', use_container_width=True, type = 'primary')
        if display_data_editor_button:
            # Get the name of the spirit the user selected
            st.session_state['chosen_spirit'] = edit_df[edit_df['Use in Cocktail'] == True]['Name'].values[0]
            # Set the demo_page session_state variable to the name of the spirit
            st.session_state.demo_page = "create_cocktail"
            st.experimental_rerun()
    else:
        st.error('Please select exactly one spirit to use in your cocktail')

# Create the function to allow the user to create their cocktail.  We will be repurposing the existing "Create Cocktail" page

def create_cocktail():

    # Build the form 
    # Create the header
    st.markdown('''<div style="text-align: center;">
    <h4 style = "color:#7b3583;">Tell us about the cocktail you want to create!</h4>
    </div>''', unsafe_allow_html=True)
    st.text("")

    # Display a message with the spirit the user selected
    st.markdown(f'''<div style="text-align: center;">
    <h5>Spirit selected: <div style="color:red;">{st.session_state.chosen_spirit}</div></h5>
    </div>''', unsafe_allow_html=True)

    st.text("")

    # Set the chosen_liquor variable to the spirit the user selected
    chosen_liquor = st.session_state.chosen_spirit

    # Allow the user to choose what type of cocktail from "Classic", "Craft", "Standard"
    cocktail_type = st.selectbox('What type of cocktail are you looking for?', ['Classic', 'Craft', 'Standard'])
    # Allow the user the option to select a type of cuisine to pair it with if they have not uploaded a food menu
    cuisine = st.selectbox('What type of cuisine, if any, are you looking to pair it with?', ['Any', 'Fresh Northern Californian', 'American',\
                            'Mexican', 'Italian', 'French', 'Chinese', 'Japanese', 'Thai', 'Indian', 'Greek', 'Spanish', 'Korean', 'Vietnamese',\
                            'Mediterranean', 'Middle Eastern', 'Caribbean', 'British', 'German', 'Irish', 'African', 'Moroccan', 'Nordic', 'Eastern European',\
                            'Jewish', 'South American', 'Central American', 'Australian', 'New Zealand', 'Pacific Islands', 'Canadian', 'Other'])
    # Allow the user to enter a theme for the cocktail if they want
    theme = st.text_input('What theme, if any, are you looking for? (e.g. "tiki", "holiday", "summer", etc.)', 'None')

    # Create the submit button
    cocktail_submit_button = st.button(label='Create your cocktail!')
    if cocktail_submit_button:
        with st.spinner('Creating your cocktail recipe.  This may take a minute...'):
            get_inventory_cocktail_recipe(chosen_liquor, cocktail_type, cuisine, theme)
            st.session_state.image_generated = False
            st.session_state.demo_page = "display_recipe"
            st.experimental_rerun()

# Function to display the recipe
def display_recipe():
    # Create the header
    st.markdown('''<div style="text-align: center;">
    <h4>Here's your recipe!</h4>
    <hr>    
    </div>''', unsafe_allow_html=True)
    # Create 2 columns, one to display the recipe and the other to display a generated picture as well as the buttons
    col1, col2 = st.columns([1.5, 1], gap = "large")
    with col1:
        # Display the recipe name
        st.markdown(f'**Recipe Name:** {st.session_state["cocktail_name"]}')
        # Display the recipe ingredients
        st.markdown('**Ingredients:**')
        
        # Check to see if there are any non-alphanumeric characters in the ingredient name and if so, remove them
        for ingredient in st.session_state.ingredients:
            ingredient_name = ingredient[1].replace('[', '').replace(']', '').strip()
            # Replace the 1st value in the ingredient tuple with the ingredient name
            ingredient = (ingredient[0], ingredient_name)

            if ingredient_name.lower() in st.session_state.df['Name'].str.lower().values:
                st.markdown(f'* <div style="color: red;">{ingredient[0]} oz {ingredient_name}</div>', unsafe_allow_html=True)
                st.session_state['inventory_ingredients'].append(ingredient)
            else:
                st.session_state['ni_ingredients'].append(ingredient)
                # If the ingredient is not a float, display it without the oz
                if type(ingredient[0]) != float:
                    st.markdown(f'* {ingredient[0]} {ingredient_name}', unsafe_allow_html=True)
                else:
                    st.markdown(f'* {ingredient[0]} oz {ingredient_name}', unsafe_allow_html=True)
        # Create a key so the user can see what the colors mean
        st.markdown(f'<div style="color: red;">Note: If the color of the ingredient is red, it is from your inventory', unsafe_allow_html=True)
      

        
          
        st.text("")

        # Display the recipe instructions
        st.markdown('**Instructions:**')
        for instruction in st.session_state['instructions']:
            st.markdown(f'* {instruction}')
        # Display the recipe garnish
        st.markdown(f'**Garnish:**  {st.session_state.garnish}')
        # Display the recipe glass
        st.markdown(f'**Glass:**  {st.session_state.glass}')
        # Display the flavor profile
        st.markdown(f'**Flavor Profile:**  {st.session_state.flavor_profile}')
    with col2:
        # Display the recipe name
        st.markdown(f'<div style="text-align: center;">{st.session_state["cocktail_name"]}</div>', unsafe_allow_html=True)
        st.text("")
        # Placeholder for the image
        image_placeholder = st.empty()
        # Check if the image has already been generated
        if st.session_state.image_generated == False:
            image_placeholder.text("Generating cocktail image...")
            # Generate the image
            image_prompt = f'A cocktail named {st.session_state.cocktail_name} in a {st.session_state.glass} glass with a {st.session_state.garnish} garnish'
            st.session_state.image = generate_image(image_prompt)
            st.session_state.image_generated = True
        # Update the placeholder with the generated image
        image_placeholder.image(st.session_state.image['output_url'], use_column_width=True)
        # Markdown "AI image generate by [StabilityAI](https://stabilityai.com)"]"
        st.markdown('''<div style="text-align: center;">
        <p>AI cocktail image generated using the Stable Diffusion API by <a href="https://deepai.org/" target="_blank">DeepAI</a></p>
        </div>''', unsafe_allow_html=True)
        st.warning('**Note:** The actual cocktail may not look exactly like this!')
        # Save the selected recipe as a PDF

        # Save the selected recipe as a PDF
            # pdf_path = save_recipe_as_pdf(st.session_state.recipe, f"{st.session_state.cocktail_name}")

        # Generate a download link for the saved PDF
        # download_link = get_recipe_pdf_download_link(pdf_path, f"{st.session_state.cocktail_name}.pdf")

        # Display the download link in a centered div
        # st.markdown(f'''<div style="text-align: center;">
        # <p>{download_link}</p>''', unsafe_allow_html=True)

        # Create an option to chat about the recipe
        chat_button = st.button('Questions about the recipe?  Click here to chat with a bartender about it.', type = 'primary', use_container_width=True)
        if chat_button:
            st.session_state.bar_chat_page = "recipe_chat"
            switch_page('Cocktail Chat')
        # Create a button to cost out the recipe
        cost_out_button = st.button('Cost out the recipe', type = 'primary', use_container_width=True)
        if cost_out_button:
            with st.spinner('Costing out the recipe.  This may take a minute...'):
                st.session_state.recipe_cost = cost_out_recipe()
                st.session_state.demo_page = "display_recipe_cost"
                st.experimental_rerun()


# Create a function to display the cost of the recipe
def display_cost():
    # Create two columns -- one two display the recipe text and the cost per recipe, the other to display the profit
    col1, col2 = st.columns(2, gap = 'medium')
    with col1:
        # Display the recipe name
        st.markdown(f'**Recipe Name:** {st.session_state["cocktail_name"]}')
        # Display the recipe ingredients
        st.markdown('**Ingredients:**')
        # Check to see if the name of each ingredient is in the inventory dataframe regardless of case, and if it is, display it in red
        # If they are not in the inventory dataframe, display them in black
        for ingredient in st.session_state.ingredients:
            # Check to see if there are any non-alphanumeric characters in the ingredient name and if so, remove them
            ingredient_name = ingredient[1]
            if ingredient_name.lower() in st.session_state.df['Name'].str.lower().values:
                st.markdown(f'* <div style="color: red;">{ingredient[0]} oz {ingredient_name}</div>', unsafe_allow_html=True)
            else:
                # If the ingredient is not a float, display it without the oz
                if type(ingredient[0]) != float:
                    st.markdown(f'* {ingredient[0]} {ingredient_name}', unsafe_allow_html=True)
                else:
                    st.markdown(f'* {ingredient[0]} oz {ingredient_name}', unsafe_allow_html=True)
        # Create a key so the user can see what the colors mean
        st.markdown(f'<div style="color: red;">**Inventory Item</div>', unsafe_allow_html=True)
        st.text("")

        # Display the cost
        st.markdown('**Recipe Cost:**')
        for ingredient in st.session_state.recipe_cost:
            st.write(f'{ingredient[0]}: ${float(ingredient[1]):.2f}')

        
    with col2:
        # Calculate and display total costs and the potential profit
        st.markdown(f'**Total cost to use up the amount of {st.session_state.chosen_spirit} in your inventory:**')
        st.markdown(f'You can make **{st.session_state.num_drinks}** of the "{st.session_state.cocktail_name}" with the amount of {st.session_state.chosen_spirit} you have in your inventory.')

        total_drinks_cost = st.session_state.total_cost * st.session_state.num_drinks
        st.write(f'The total cost of the recipe for {st.session_state.num_drinks} drinks is ${total_drinks_cost:.2f}.')
        # Display the potential profit
        st.markdown('**Potential Profit:**')
        # Create a slider that allows the user to select the price of the drink they want to sell it for
        st.write('Select the price you want to sell the drink for:')
        st.session_state.price = st.slider('Price', min_value=10, max_value=20, value=10, step=1)

        # Calculate the profit
        total_profit = (st.session_state.num_drinks * st.session_state.price) - total_drinks_cost

        # Profit per drink
        profit_per_drink = st.session_state.price - st.session_state.total_cost

        # Display the profit
        st.write(f'The total profit for {st.session_state.num_drinks} drinks is ${total_profit:.2f}.')
        st.write(f'The profit per drink is ${profit_per_drink:.2f} or {(profit_per_drink / st.session_state.price) * 100:.2f}%.')

    st.text("")
    st.text("")
    
    # Set the value of the chosen_spirit to the amount from the "Total Value" column in the inventory dataframe.  Match the name of the chosen_spirit to the name in the inventory dataframe regardless of case
    total_value = st.session_state.df.loc[st.session_state.df['Name'].str.lower() == st.session_state.chosen_spirit.lower()]['Total Value'].values[0]

    # Note the difference in the value of the chosen_spirit in inventory and the total profit
    st.success(f"Congratulations!  You turned \${total_value:.2f} worth of {st.session_state.chosen_spirit} into ${total_profit:.2f} worth of profit!")

    # Create a button to go back to the recipe page
    back_button = st.button('Create another recipe', type = 'primary', use_container_width=True)
    if back_button:
        st.session_state.demo_page = "choose_spirit"
        reset_inventory_session_variables()
        st.experimental_rerun()






# Establish the flow of the application
if st.session_state.demo_page == "upload_inventory":
    asyncio.run(upload_inventory())
elif st.session_state.demo_page == "choose_spirit":
    choose_spirit()
elif st.session_state.demo_page == "create_cocktail":
    create_cocktail()
elif st.session_state.demo_page == "display_recipe":
    display_recipe()
elif st.session_state.demo_page == "display_recipe_cost":
    display_cost()