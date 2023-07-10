# This is the main entry point for the user to create cocktails

# Import libraries
import streamlit as st
# from utils.save_recipes import save_recipe_as_pdf, get_recipe_pdf_download_link
from utils.cocktail_functions import RecipeService
from utils.chat_utils import ChatService, Context
from utils.inventory_functions import InventoryService
from streamlit_extras.switch_page_button import switch_page
from utils.image_utils import generate_image 
from streamlit import components
from PIL import Image
from redis import Redis as RedisStore
import uuid

redis_store = RedisStore()

# Initialize the session state
def init_cocktail_session_variables():
    # Initialize session state variables
    session_vars = [
        'cocktail_page', 'cocktail_recipe', 'food_menu', 'drink_menu', 'image', 'inventory_list', 'cocktail_name', 'image_generated', 'ingredients', 'session_id', 'context'
    ]
    default_values = [
        'get_cocktail_info', '', '', '', None, [], '', False, [], str(uuid.uuid4()), None
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

# Reset the pages to their default values
def reset_pages():
    st.session_state.menu_page = "upload_menus"
    st.session_state.bar_chat_page = "chat_choice"
    st.session_state.inventory_page = "get_inventory_choice"


# Initialize the session variables
init_cocktail_session_variables()
reset_pages()

# Create a list of commnonly used spirits that the user can choose from
spirits_list = [
    # Basic spirits
    "Vodka", "Gin", "Rum", "Tequila", "Mezcal", "Brandy", "Whiskey", "Scotch", 
    "Bourbon", "Rye Whiskey", "Irish Whiskey", "Canadian Whisky", "Japanese Whisky", 
    "Cognac", "Armagnac", "Calvados", "Pisco", "Grappa", "Sake", "Soju", "Shochu",
    
    # Liqueurs & Cordials
    "Amaretto", "Baileys Irish Cream", "Benedictine", "Chartreuse (Green)", 
    "Chartreuse (Yellow)", "Cointreau", "Drambuie", "Frangelico", "Galliano", 
    "Grand Marnier", "Jägermeister", "Kahlua", "Limoncello", "Sambuca", 
    "Southern Comfort", "St. Germain (Elderflower Liqueur)", "Tia Maria", 
    "Chambord", "Aperol", "Campari", "Fernet Branca", "Pimm's No. 1",
    
    # Vermouths & Amaro
    "Sweet Vermouth", "Dry Vermouth", "Red Vermouth", "White Vermouth", "Amaro Montenegro", 
    "Amaro Nonino", "Averna", "Cynar", "Ramazzotti", "Zucca", "Amaro Lucano", 

    # Flavored Spirits
    "Absinthe", "Anisette", "Aquavit", "Arak", "Bitters", "Ouzo", "Schnapps", 
    "Flavored Vodka", "Spiced Rum", "Peach Schnapps", "Peppermint Schnapps",
    
    # Other
    "Moonshine", "Everclear", "Fireball", "Malibu (Coconut Rum)", 
    "Margarita Mix", "Bloody Mary Mix", "Other" 
]




# Define the function to get the information about the cocktail
def get_cocktail_type():
    # Instantiate the InventoryService class
    inventory_service = InventoryService(session_id=st.session_state.session_id)
    # If there is already an inventory or a menu uploaded, proceed to the cocktail creation page
    if inventory_service.inventory:
        st.session_state.inventory_page = 'choose_spirit'
        switch_page('Inventory')
        st.experimental_rerun()
    else:    
        st.markdown('''<div style="text-align: center;">
        <h3>Welcome to the Cocktail Creator!</h3>
        <h5>You can chooose to proceed directly to cocktail creation, or upload or use a sample inventory for further customization</h5>
        </div>''', unsafe_allow_html=True)
        
        st.text("")

        # Create two columns -- one for the upload menu image and button, and one for the upload inventory image and button
        col1, col2 = st.columns(2, gap="large")
        with col1:
            menu_image = Image.open('resources/bar_menu.png')
            st.image(menu_image, use_column_width=True)
            proceed_without_inventory_button = st.button('Proceed Directly to Cocktail Creation', use_container_width=True, type = 'primary')
            if proceed_without_inventory_button:
                st.session_state.cocktail_page = 'get_cocktail_info'
                st.experimental_rerun()
        with col2:
            inventory_image = Image.open('resources/inventory_image.png')
            st.image(inventory_image, use_column_width=True)
            proceed_with_inventory_button = st.button('Proceed with Inventory', use_container_width=True, type = 'primary')
            if proceed_with_inventory_button:
                st.session_state.inventory_page = 'get_inventory_choice'
                switch_page('Inventory')
        

def get_cocktail_info():
    # Instantiate the RecipeService class
    recipe_service = RecipeService(session_id=st.session_state.session_id)

    # Build the form 
    # Create the header
    st.markdown('''<div style="text-align: center;">
    <h2>Tell us about the cocktail you want to create!</h2>
    </div>''', unsafe_allow_html=True)
    st.text("")

    # Start by getting the input for the liquor that the user is trying to use up
    chosen_liquor = st.selectbox('What spirit are you trying to use up? (Type to search by name)', spirits_list)
    st.warning('**Note:  If you do not see the spirit you are looking for above, select "Other" and manually enter it below.**')
    # If the spirit they need to use up is not in the list, allow them to enter it manually
    if chosen_liquor == 'Other':
        chosen_liquor = st.text_input('What is the name of the spirit you are trying to use up?')
    chosen_liquor = str(chosen_liquor)
    # Allow the user to choose what type of cocktail from "Classic", "Craft", "Standard"
    cocktail_type = st.selectbox('What type of cocktail are you looking for?', ['Classic', 'Craft', 'Standard'])
    # Allow the user the option to select a type of cuisine to pair it with if they have not uploaded a food menu
    cuisine = st.selectbox('What type of cuisine, if any, are you looking to pair it with?', ['Any', 'American',\
                            'Mexican', 'Italian', 'French', 'Chinese', 'Japanese', 'Thai', 'Indian', 'Greek', 'Spanish', 'Korean', 'Vietnamese',\
                            'Mediterranean', 'Middle Eastern', 'Caribbean', 'British', 'German', 'Irish', 'African', 'Moroccan', 'Nordic', 'Eastern European',\
                            'Jewish', 'South American', 'Central American', 'Australian', 'New Zealand', 'Pacific Islands', 'Canadian', 'Other'])
    # Allow the user to enter a theme for the cocktail if they want
    theme = st.text_input('What theme, if any, are you looking for? (e.g. "tiki", "holiday", "summer", etc.)', 'None')

    # Create the submit button
    cocktail_submit_button = st.button(label='Create your cocktail!')
    if cocktail_submit_button:
        with st.spinner('Creating your cocktail recipe.  This may take a minute...'):
            recipe_service.get_cocktail_recipe(liquor=chosen_liquor, cocktail_type=cocktail_type, cuisine=cuisine, theme=theme)
            st.session_state.image_generated = False
            st.session_state.cocktail_page = "display_recipe"
            st.experimental_rerun()

'''async def get_menu_cocktail_info():

    # Build the form 

    # Start by getting the input for the liquor that the user is trying to use up
    liquor = st.text_input('What liquor are you trying to use up?')
    # Allow the user to choose what type of cocktail from "Classic", "Craft", "Standard"
    cocktail_type = st.selectbox('What type of cocktail are you looking for?', ['Classic', 'Craft', 'Standard'])
   
    # Allow the user to enter a theme for the cocktail if they want
    theme = st.text_input('What theme, if any, are you looking for? (e.g. "tiki", "holiday", "summer", etc.)')

    # Create the submit button
    cocktail_submit_button = st.button(label='Create your cocktail!')
    if cocktail_submit_button:
        with st.spinner('Creating your cocktail recipe.  This may take a minute...'):
            get_menu_cocktail_recipe(liquor, cocktail_type, theme)
            st.session_state.cocktail_page = "display_recipe"
            st.experimental_rerun()'''



def display_recipe():
    # Instantiate the RecipeService class
    recipe_service = RecipeService(session_id=st.session_state.session_id)
    recipe = recipe_service.load_recipe()
    # Create the header
    st.markdown('''<div style="text-align: center;">
    <h4>Here's your recipe!</h4>
    <hr>    
    </div>''', unsafe_allow_html=True)
    # Create 2 columns, one to display the recipe and the other to display a generated picture as well as the buttons
    col1, col2 = st.columns([1.5, 1], gap = "large")
    with col1:
        # Display the recipe name
        st.markdown(f'**Recipe Name:** {recipe.name}')
        # Convert the ingredients tuples into a list of strings
        
        # Display the recipe ingredients
        st.markdown('**Ingredients:**')
        ingredients_list = [list(ingredient) for ingredient in recipe.ingredients]
        # Convert the ingredients tuple into a list
        for ingredient in ingredients_list:
            # Check to see if the amount ends in a 0, if so, remove the decimal
            if float(ingredient[1]) % 1 == 0:
                ingredient[1] = int(ingredient[1])
            st.markdown(f'{ingredient[1]} {ingredient[2]} {ingredient[0]}')
        # Display the recipe instructions
        st.markdown('**Instructions:**')
        for instruction in recipe.instructions:
            st.markdown(f'{instruction}')
        # Display the recipe garnish
        st.markdown(f'**Garnish:** {recipe.garnish}')
        # Display the recipe glass
        st.markdown(f'**Glass:** {recipe.glass}')
        # Display the recipe flavor profile
        st.markdown(f'**Flavor Profile:** {recipe.flavor_profile}') 
    with col2:
        # Display the recipe name
        st.markdown(f'<div style="text-align: center;">{recipe.name}</div>', unsafe_allow_html=True)
        st.text("")
        # Placeholder for the image
        image_placeholder = st.empty()
        # Check if the image has already been generated
        if st.session_state.image_generated == False:
            image_placeholder.text("Generating cocktail image...")
            # Generate the image
            image_prompt = f'A cocktail named {recipe.name} garnished with {recipe.garnish} in a {recipe.glass} glass.'
            st.session_state.image = generate_image(image_prompt)
            st.session_state.image_generated = True
        # Update the placeholder with the generated image
        image_placeholder.image(st.session_state.image['output_url'], use_column_width=True)
        # Markdown "AI image generate by [StabilityAI](https://stabilityai.com)"]"
        st.markdown('''<div style="text-align: center;">
        <p>AI cocktail image generated using the Stable Diffusion API by <a href="https://deepai.org/" target="_blank">DeepAI</a></p>
        </div>''', unsafe_allow_html=True)
        st.warning('**Note:** The actual cocktail may not look exactly like this!')

        # Create an option to chat about the recipe
        chat_button = st.button('Questions about the recipe?  Click here to chat with a bartender about it.', type = 'primary', use_container_width=True)
        if chat_button:
            chat_service = ChatService(session_id=st.session_state.session_id, recipe=recipe)
            context = Context.RECIPE
            st.session_state.context = context
            chat_service.initialize_chat(context=context)
            st.session_state.bar_chat_page = 'display_chat'
            switch_page("Cocktail Chat")
            
    # Display the feedback form
    st.markdown('---')
    st.markdown('''<div style="text-align: center;">
    <h4 class="feedback">We want to hear from you!  Please help us grow by taking a quick second to fill out the form below and to stay in touch about future developments.  Thank you!</h4>
    </div>''', unsafe_allow_html=True)

    src="https://docs.google.com/forms/d/e/1FAIpQLSc0IHrNZvMfzqUeSfrJxqINBVWxE5ZaF4a30UiLbNFdVn1-RA/viewform?embedded=true"
    components.v1.iframe(src, height=600, scrolling=True)

if st.session_state.cocktail_page == "get_cocktail_type":
    get_cocktail_type()
elif st.session_state.cocktail_page == "get_cocktail_info":
    get_cocktail_info()
elif st.session_state.cocktail_page == "display_recipe":
    display_recipe()