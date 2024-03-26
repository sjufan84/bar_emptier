""" This will be the page to display the user's generated training guides """
# Initial imports
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# Define the page config
st.set_page_config(
    page_title="BarKeepAI", page_icon="./resources/cocktail_icon.png", initial_sidebar_state="collapsed"
)

st.markdown("#### Beta Testers:")
st.markdown('''
        :blue[**Here we display the generated training guide for the cocktail.
        The idea is to generate a "one-pager" that
        can easily be used for pre-shift and distribution to the staff.**]
        ''')
st.markdown('---')

if "cocktail_page" not in st.session_state:
    st.session_state.cocktail_page = "display_recipe"
if "training_guide" not in st.session_state:
    st.session_state.training_guide = None


# Define the function to display the training guide for the cocktail
def display_training_guide():
    """ Display the generated training guide for the current cocktail """
    if not st.session_state.training_guide:
        st.markdown("**You have not created a cocktail yet.  Please select the\
            'Create a Cocktail' button on the home page or sidebar.**")
        st.stop()
    # Display the training guide
    st.markdown(st.session_state.training_guide)

    # Create a button to go back to the cocktail page
    back_to_cocktail_button = st.button(
        "Back to Main Cocktail Page", use_container_width=True, type='secondary'
    )
    if back_to_cocktail_button:
        st.session_state.cocktail_page = "display_recipe"
        switch_page('Create Cocktails')
        st.rerun()

    chat_button = st.button(
        'Questions about the recipe?  Click here to chat with a bartender about it.',
        type = 'secondary', use_container_width=True
    )
    if chat_button:
        switch_page('Cocktail Chat')
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

    general_chat_button = st.button('General Chat', use_container_width=True, type='secondary')
    if general_chat_button:
        switch_page('General Chat')
        st.rerun()

    # Create a button to go back to the home page
    home_button = st.button('Back to Home', type = 'secondary', use_container_width=True)
    if home_button:
        switch_page('Home')
        st.rerun()

    st.link_button(
        label = "**Please help us out by filling out a quick survey about your experience!**",
        url = "https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAVtWsJ1UM0xEWjVGMVEyM1hURldWWU5JRVhPWUJZVy4u",
        type = "secondary",
        use_container_width=True)

    st.link_button(
        label = "**Contact Us**",
        url = "mailto:dave_thomas@enoughwebapp.com",
        type = "secondary",
        use_container_width=True)

display_training_guide()
