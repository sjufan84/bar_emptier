""" This is the main entry point for the user to create cocktails """
# Import libraries
import logging
import asyncio
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from utils.image_utils import generate_image
from utils.cocktail_utils import create_cocktail
from utils.training_utils import create_training_guide
# from utils.save_print_utils import get_recipe_pdf_download_link

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the page config
st.set_page_config(
    page_title="BarGuruV1", page_icon="./resources/cocktail_icon.png", initial_sidebar_state="auto"
)

general_chat_button = st.sidebar.button(
    "General Chat", type = "secondary", use_container_width=True
)
if general_chat_button:
    switch_page('General Chat')
    st.rerun()

home_button = st.sidebar.button(
    "Home", type = "secondary", use_container_width=True
)
if home_button:
    switch_page('Home')
    st.rerun()

st.sidebar.link_button(
    label = ":green[**Please help us out by filling out a quick survey about your experience!**]",
    url = "https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAVtWsJ1UM0xEWjVGMVEyM1hURldWWU5JRVhPWUJZVy4u",
    type = "secondary",
    use_container_width=False)

# Initialize the session state
def init_cocktail_session_variables():
    # Initialize session state variables
    session_vars = [
        "current_cocktail", "current_image", "cocktail_page", "training_guide",
        "cocktail_chat_messages", "current_model", "model_selection"
    ]
    default_values = [
        None, None, "get_cocktail_info", None, None, "gpt-3.5-turbo-1106", "GPT-3.5"
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

# Define the callback function to update the session state
def set_model():
    if st.session_state["radio_value"] == ':violet[GPT-3.5]':
        logger.info("Setting the model to GPT-3.5")
        st.session_state["current_model"] = "gpt-3.5-turbo-1106"
        logger.info(f"Current model: {st.session_state['current_model']}")
    elif st.session_state["radio_value"] == ':violet[GPT-4]':
        logger.info("Setting the model to GPT-4")
        st.session_state["current_model"] = "gpt-4-1106-preview"
        logger.info(f"Current model: {st.session_state['current_model']}")

# Initialize the session state variables
init_cocktail_session_variables()

# Reset the pages to their default values
# def reset_pages():

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

async def get_cocktail_info():
    """ This is the main entry point for the user to create cocktails """
    st.markdown("#### Hello Beta Testers!")
    st.markdown(
        ''':violet[**This page should be pretty straightforward.  You will notice the option to select
        between 'GPT-3.5' and 'GPT-4'.  GPT-4 will theoretically generate more nuanced and robust
        cocktails, but will take a bit longer to generate.  Feel free to play around with each, and let us
        know what you think!**]'''
    )

    # Create the header
    st.markdown('''<div style="text-align: center;">
    <h2>Tell us about the cocktail you want to create!</h2>
    </div>''', unsafe_allow_html=True)
    st.text("")

    # Start by getting the input for the liquor that the user is trying to use up
    chosen_liquor = st.selectbox('What spirit are you trying to use up?\
    (Type to search by name)', spirits_list)
    st.markdown(':violet[**Note:  If you do not see the spirit you are looking for above,\
    select "Other" and manually enter it below.**]')
    # If the spirit they need to use up is not in the list, allow them to enter it manually
    if chosen_liquor == 'Other':
        chosen_liquor = st.text_input('What is the name of the spirit you are trying to use up?')
    chosen_liquor = str(chosen_liquor)
    logger.info(f"Chosen liquor: {chosen_liquor}")
    # Allow the user to choose what type of cocktail from "Classic", "Craft", "Standard"
    cocktail_type = st.selectbox(
        'What type of cocktail are you looking for?', ['Classic', 'Craft', 'Standard']
    )
    # Allow the user the option to select a type of cuisine to pair
    # it with if they have not uploaded a food menu
    cuisine = st.selectbox('What type of cuisine, if any, are you looking to pair it with?', [
        'Any', 'American', 'Mexican', 'Italian', 'French', 'Chinese', 'Japanese', 'Thai', 'Indian',
        'Greek', 'Spanish', 'Korean', 'Vietnamese', 'Mediterranean', 'Middle Eastern', 'Caribbean',
        'British', 'German', 'Irish', 'African', 'Moroccan', 'Nordic', 'Eastern European',
        'Jewish', 'South American', 'Central American', 'Australian',
        'New Zealand', 'Pacific Islands', 'Canadian', 'Other'
    ])
    # Allow the user to enter a theme for the cocktail if they want
    theme = st.text_input(
        'What theme, if any, are you looking for? (e.g. "tiki", "holiday", "summer", etc.)', 'None'
    )
    col1, col2 = st.columns(2, gap="small")
    # Create the submit button
    with col1:
        cocktail_submit_button = st.button(label='Create your cocktail!')
        if cocktail_submit_button:
            with st.spinner('Creating your cocktail recipe.  This may take a minute...'):
                st.session_state.current_cocktail = await create_cocktail(
                    liqour=chosen_liquor, type=cocktail_type, cuisine=cuisine, theme=theme
                )
                if st.session_state.current_cocktail:
                    st.session_state.cocktail_page = "display_recipe"
                    st.rerun()
    with col2:
        st.radio(
            ":rainbow[AI Model Selection]", [':violet[GPT-3.5]', ':violet[GPT-4]'], index=0, horizontal=True,
            key="radio_value", on_change=set_model
        )
    st.text("")
    general_chat_button = st.button(
        "General Chat", type = "secondary", use_container_width=True, key="gchat2"
    )
    if general_chat_button:
        switch_page('General Chat')
        st.rerun()
    # Create a button to go back to the home page
    home_button = st.button('Back to Home', type = 'secondary', use_container_width=True)
    if home_button:
        switch_page('Home')
        st.rerun()

    st.link_button(
        label = ":rainbow[**Please help us out by filling out a quick survey about your experience!**]",
        url = "https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAVtWsJ1UM0xEWjVGMVEyM1hURldWWU5JRVhPWUJZVy4u",
        type = "secondary",
        use_container_width=True)

    st.link_button(
        label = ":green[**Contact Us**]",
        url = "mailto:dave_thomas@enoughwebapp.com",
        type = "secondary",
        use_container_width=True)
async def display_recipe():
    if not st.session_state.current_cocktail:
        st.session_state.cocktail_page = "get_cocktail_info"
        st.rerun()
    # Create the header
    st.markdown('''<div style="text-align: center; color:#778da9">
    <h4>Here's your recipe!</h4>
    <hr>
    </div>''', unsafe_allow_html=True)
    recipe = st.session_state.current_cocktail
    # Create 2 columns, one to display the recipe and the other to display
    # a generated picture as well as the buttons
    col1, col2 = st.columns([1.5, 1], gap = "large")
    with col1:
        # Display the recipe name
        st.markdown(f':violet[**Recipe Name:**]  {recipe["name"]}')
        # Convert the ingredients tuples into a list of strings

        # Display the recipe ingvioletients
        st.markdown(':violet[**Ingredients:**]')
        ingredients_list = recipe['ingredients']
        # Convert the ingredients tuple into a list
        for ingredient in ingredients_list:
            st.markdown(f'{ingredient}')
        # Display the recipe instructions
        st.markdown(':violet[**Directions:**]')
        for direction in recipe['directions']:
            st.markdown(f'{direction}')
        # Display the recipe garnish
        st.markdown(f':violet[**Garnish:**] {recipe["garnish"]}')
        # Display the recipe glass
        st.markdown(f':violet[**Glass:**] {recipe["glass"]}')
        # Display the recipe description
        st.markdown(f':violet[**Description:**] {recipe["description"]}')
        # Display the recipe fun fact
        if recipe["fun_fact"]:
            st.markdown(f':violet[**Fun Fact:**] {recipe["fun_fact"]}')
    with col2:
        # Display the recipe name
        st.markdown(f'<div style="text-align: center;">{recipe["name"]}</div>', unsafe_allow_html=True)
        st.text("")
        if not st.session_state.current_image:
            with st.spinner('Generating cocktail image...'):
                # Generate the image
                image_prompt = f'''A cocktail named {recipe["name"]}
                garnished with {recipe["garnish"]} in a {recipe["glass"]} glass.'''
                st.session_state.current_image = await generate_image(image_prompt)
        if st.session_state.current_image:
            st.image(st.session_state.current_image, use_column_width=True)
        # Markdown "AI image generate by [StabilityAI](https://stabilityai.com)"]"
        st.markdown('''<div style="text-align: center;">
        <p>AI cocktail image generated using the Dall-E-2 by OpenAI.</p>
        </div>''', unsafe_allow_html=True)
        st.markdown(':violet[**Note:** The actual cocktail may not look exactly like this!]')

        # pdf_download_link = await get_recipe_pdf_download_link(
        #    recipe = recipe, recipe_name = recipe["name"]
        # )
        # st.markdown(pdf_download_link, unsafe_allow_html=True)

        # Create an option to chat about the recipe
        chat_button = st.button(
            'Questions about the recipe?  Click here to chat with a bartender about it.',
            type = 'secondary', use_container_width=True
        )
        if chat_button:
           switch_page('Cocktail Chat')
           st.rerun()

        #  Create an option to generate a training guide
        training_guide_button = st.button(
            'Click here to generate a training guide for this recipe.',
            type = 'secondary', use_container_width=True)
        if training_guide_button:
            with st.spinner('Generating training guide...'):
                st.session_state.training_guide = await create_training_guide(recipe)
                if st.session_state.training_guide:
                    switch_page('Training')
                    st.rerun()

        # Create an option to get a new recipe
        new_recipe_button = st.button('Get a new recipe', type = 'secondary', use_container_width=True)
        if new_recipe_button:
            # Clear the session state variables
            st.session_state.current_cocktail = None
            st.session_state.current_image = None
            # Clear the recipe and chat history
            if st.session_state.cocktail_chat_messages:
                st.session_state.cocktail_chat_messages = None
            st.session_state.cocktail_page = "get_cocktail_info"
            st.rerun()

        st.link_button(
            label = ":rainbow[**Please help us out by filling out a quick survey about your experience!**]",
            url = "https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAVtWsJ1UM0xEWjVGMVEyM1hURldWWU5JRVhPWUJZVy4u",
            type = "secondary",
            use_container_width=False)

        st.link_button(
            label = ":green[**Contact Us**]",
            url = "mailto:dave_thomas@enoughwebapp.com",
            type = "secondary",
            use_container_width=True)

if st.session_state.cocktail_page == "get_cocktail_info":
    asyncio.run(get_cocktail_info())
elif st.session_state.cocktail_page == "display_recipe":
    asyncio.run(display_recipe())
