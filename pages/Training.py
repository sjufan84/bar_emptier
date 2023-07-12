""" 
This will be the page to display the user's generated training guides
"""

# Initial imports
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# Define the page config
st.set_page_config(page_title="BarKeepAI", page_icon="./resources/cocktail_icon.png", initial_sidebar_state="collapsed")

st.markdown("#### Documentation notes:")
st.success('''
        **Here we display the generated training guide for the cocktail.  The idea is to generate a "one-pager" that
        can easily be used for pre-shift and distribution to the staff.**
        ''')
st.markdown('---')


# Define the function to display the training guide for the cocktail
def display_training_guide():
    # Load the recipe service
    recipe_service = st.session_state.recipe_service
    recipe = recipe_service.recipe
    # Load the chat service
    chat_service = st.session_state.chat_service

    # Display the training guide
    st.markdown(f"##### Here is your training guide for the {recipe.name}!")
    st.markdown("---")

    st.write(st.session_state.training_guide)

    # Create an option to go back to the recipe
    back_to_recipe_button = st.button('Back to Recipe', type = 'primary', use_container_width=True)
    if back_to_recipe_button:
        if st.session_state.is_inventory_recipe == True:
            st.session_state.inventory_page = "display_recipe"
            switch_page("Inventory")
            st.experimental_rerun()
        else:
            st.session_state.cocktail_page = "display_recipe"
            switch_page("Create Cocktails")
            st.experimental_rerun()

    # Create an option to get a new recipe
    new_recipe_button = st.button('Get a new recipe', type = 'primary', use_container_width=True)
    if new_recipe_button:
        # Clear the session state variables
        st.session_state.image_generated = False
        st.session_state.cocktail_page = "get_cocktail_type"
        # Clear the recipe and chat history
        chat_service.chat_history = []
        recipe_service.recipe = None
        st.experimental_rerun()

if __name__ == "__main__":
    display_training_guide()

