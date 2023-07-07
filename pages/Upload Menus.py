# This will be the page that allows the users to upload a menu or menus for the model to reference when creating cocktails

# Initial Imports
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from utils.text_extraction_functions import extract_and_concatenate_text, edit_menu

# Initialize the session state
def init_menu_session_variables():
    # Initialize session state variables
    session_vars = [
        'menu_page', 'food_menu', 'drink_menu',
    ]
    default_values = [
        'upload_menus', None, None
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

# Initialize the session variables and reset the pages
init_menu_session_variables()



# Define the upload menus page
def upload_menus():
    # Create the header
    st.markdown('##### Upload your menu files for additional context when creating your cocktails.')
                
    st.success('**There are two options for uploading files: either upload a food menu file (or files) and / or upload a cocktail menu file (or files).\
                The model will then take these into account when creating your cocktail to ensure it fits into your menu theme\
                and is not too similar to any of the other drinks on your menu.**\n\n**Files can be in the form of a pdf, txt, or even a jpeg or png.\
                The text can be extracted from pictures of menus as long as the picture is clear enough and well lit.**')
    # Create a space in between the header and the uploaders
    st.text('')
    
    
    # We will create two separate uploaders, one for food menus and one for drink menus as well as two text areas (one for food and one for drink)
    # The user can upload a menu or paste the text of a menu into the text area
    # We will create two columns, one for food and one for drink
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Food Menu")
        menu_files = st.file_uploader("Upload a menu", type=["pdf", "txt", "jpeg", "png", "jpg"], key = "food_menu_files")
        menu_text_area = st.text_area("Or paste the text of the menu here", height=250, key = "food_menu_text_area")
    with col2:
        st.subheader("Drink Menu")
        drink_menu_files = st.file_uploader("Upload a menu", type=["pdf", "txt", "jpeg", "png", "jpg"], key="drink_menu_files")
        drink_menu_text_area = st.text_area("Or paste the text of the menu here", height=250, key = "drink_menu_text_area")

    # Create a button to submit the menus
    submit_menus_button = st.button("Submit Menus")

    # Warning about using Google Vision to extract text from menus
    st.warning('*Please note: if uploading a picture of a menu or menus, we use Google Vision to extract the text and then\
               reformat it to be more readable for the model.  You will have the chance to edit the resulting menu after\
               it is generated.  By default we do not reformat the menus pulled from text or pdf as they are generally\
               easy to interpret for cocktail creation purposes.*')
    
    if submit_menus_button:
        # If there is not a food menu or drink menu, display a warning
        if not menu_files and not menu_text_area and not drink_menu_files and not drink_menu_text_area:
            st.warning("Please upload a drink menu file or copy and paste the drink menu text into the text box above.  Ensure images are formatted with the\
                       extension .jpg, .jpeg, or .png.")
        else:
            with st.spinner("Extracting and cleaning menu text. If uploading from photos, this will take a minute..."):
                # Update the st.session_state variables after submitting the menus
                if menu_files or menu_text_area:
                    if menu_files:
                        full_food_menu_text = extract_and_concatenate_text(menu_files, menu_text_area)
                        st.session_state.food_menu = edit_menu(full_food_menu_text, menu_files)
                    else:
                        st.session_state.food_menu = menu_text_area

                if drink_menu_files or drink_menu_text_area:
                    if drink_menu_files:
                        full_drink_menu_text = extract_and_concatenate_text(drink_menu_files, drink_menu_text_area)
                        st.session_state.drink_menu = edit_menu(full_drink_menu_text, drink_menu_files)
                    else:
                        st.session_state.drink_menu = drink_menu_text_area
                
                # Once the menus have been uploaded, we will switch to the user edit menu page
                st.session_state.menu_page = 'user_edit_menu'
                st.experimental_rerun()
                

def user_edit_menu():
    # Here we will display the text of the menus and allow the user to edit them if they wish
    # We will create two columns if the user has uploaded both a food and drink menu, otherwise we will only create one column
    if st.session_state.food_menu and st.session_state.drink_menu:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Food Menu")
            # Create a text area for the user to edit the food menu
            food_text_area = st.text_area("Edit the food menu here", value=st.session_state.food_menu, height=250)
        with col2:
            st.subheader("Drink Menu")
            # Create a text area for the user to edit the drink menu
            drink_text_area = st.text_area("Edit the drink menu here", value=st.session_state.drink_menu, height=250)
    elif st.session_state.food_menu:
        st.subheader("Food Menu")
        # Create a text area for the user to edit the food menu
        food_text_area = st.text_area("Edit the food menu here", value=st.session_state.food_menu, height=250)
    elif st.session_state.drink_menu:
        st.subheader("Drink Menu")
        # Create a text area for the user to edit the drink menu
        drink_text_area = st.text_area("Edit the drink menu here", value=st.session_state.drink_menu, height=250)

    # Create a button to save the menu text(s) and return to the cocktail creation page
    save_menu_button = st.button("Save Menus and Return to Cocktail Creation")
    if save_menu_button:
        if st.session_state.food_menu and st.session_state.drink_menu:
            st.session_state.food_menu = food_text_area
            st.session_state.drink_menu = drink_text_area
        elif st.session_state.food_menu:
            st.session_state.food_menu = food_text_area
        elif st.session_state.drink_menu:
            st.session_state.drink_menu = drink_text_area
        st.session_state.cocktail_page = "get_menu_cocktail_info"

        switch_page("Create Cocktails")
        st.experimental_rerun()

# Create the page flow
if st.session_state.menu_page == "upload_menus":
    upload_menus()
elif st.session_state.menu_page == "user_edit_menu":
    user_edit_menu()