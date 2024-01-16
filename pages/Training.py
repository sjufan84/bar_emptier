""" This will be the page to display the user's generated training guides """
# Initial imports
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# Define the page config
st.set_page_config(
    page_title="BarKeepAI", page_icon="./resources/cocktail_icon.png", initial_sidebar_state="collapsed"
)

st.markdown("#### Documentation notes:")
st.success('''
        **Here we display the generated training guide for the cocktail.
        The idea is to generate a "one-pager" that
        can easily be used for pre-shift and distribution to the staff.**
        ''')
st.markdown('---')


# Define the function to display the training guide for the cocktail
def display_training_guide():
    """ Display the generated training guide for the current cocktail """
    # Display the training guide
    st.markdown(st.session_state.training_guide)

    # Create a button to go back to the cocktail page
    back_to_cocktail_button = st.button(
        "Back to Main Cocktail Page", use_container_width=True, type='primary'
    )
    if back_to_cocktail_button:
        st.session_state.cocktail_page = "display_recipe"
        switch_page('Create Cocktails')
        st.rerun()

display_training_guide()
