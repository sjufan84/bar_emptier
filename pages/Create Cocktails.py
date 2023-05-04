# This is the main entry point for the user to create cocktails

# Import libraries
import streamlit as st
from utils.save_recipes import save_recipe_as_pdf, get_recipe_pdf_download_link
from utils.cocktail_functions import get_cocktail_recipe


# Define the function to get the information about the cocktail
def get_cocktail_info():
    # Set the page title
    st.title('Create Cocktails')
    st.markdown('##### Use this page to create a cocktail recipe to help you use up your excess liquor inventory! 🍸🍹')
    st.markdown('---')
    # Give the user the option to upload a menu or menus for the model to reference when creating the cocktails
    st.success('If you would like to upload your existing food menu, cocktail menu, or both, please do so by clicking below.\
               This can be useful if you want to create a cocktail that fits in well with the overall theme of the menu and is\
                not similar to any of the other cocktails on the menu, if any.')
    upload_menus_button = st.button('Upload your menu(s)')
    
    # Build the form 
    with st.form('bar_emptier'):
        # Start by getting the input for the liquor that the user is trying to use up
        liquor = st.text_input('What liquor are you trying to use up?')
        # Allow the user to choose what type of cocktail from "Classic", "Craft", "Standard"
        cocktail_type = st.selectbox('What type of cocktail are you looking for?', ['Classic', 'Craft', 'Standard'])
        # Allow the user the option to select a type of cuisine to pair it with
        cuisine = st.selectbox('What type of cuisine, if any, are you looking to pair it with?', ['American',\
                                'Mexican', 'Italian', 'French', 'Chinese', 'Japanese', 'Thai', 'Indian', 'Greek', 'Spanish', 'Korean', 'Vietnamese',\
                                'Mediterranean', 'Middle Eastern', 'Caribbean', 'British', 'German', 'Irish', 'African', 'Moroccan', 'Nordic', 'Eastern European',\
                                'Jewish', 'South American', 'Central American', 'Australian', 'New Zealand', 'Pacific Islands', 'Canadian', 'Other'])
        # Allow the user to enter a theme for the cocktail if they want
        theme = st.text_input('What theme, if any, are you looking for? (e.g. "tiki", "holiday", "summer", etc.)')

        

        # Create the submit button
        cocktail_submit_button = st.form_submit_button(label='Create your cocktail!')
        if cocktail_submit_button:
            with st.spinner('Creating your cocktail recipe.  This may take a minute...'):
                get_cocktail_recipe(liquor, cocktail_type, cuisine, theme)
                st.session_state.cocktail_page = "display_recipe"
                st.experimental_rerun()


def display_recipe():
    st.markdown('##### Here is your recipe! 🍸🍹')
    st.write(st.session_state.recipe)

    # Save the selected recipe as a PDF
    pdf_path = save_recipe_as_pdf(st.session_state.recipe, f"my_recipe.pdf")

    # Generate a download link for the saved PDF
    download_link = get_recipe_pdf_download_link(pdf_path, f"my_recipe.pdf")

    # Display the download link
    st.markdown(download_link, unsafe_allow_html=True)
   
    # Create a "Create another cocktail" button
    create_another_cocktail_button = st.button('Create another cocktail!')
    if create_another_cocktail_button:
        st.session_state.cocktail_page = "get_cocktail_info"
        st.experimental_rerun()

if st.session_state.cocktail_page == "get_cocktail_info":
    get_cocktail_info()
elif st.session_state.cocktail_page == "display_recipe":
    display_recipe()