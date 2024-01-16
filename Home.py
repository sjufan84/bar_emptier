"""
This is the main demo file for the project.
This project will use OpenAI to help the user
create cocktail recipes to help them get rid of excess inventory.
"""
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit import components
from PIL import Image

# Define the page config
st.set_page_config(
    page_title="BarKeepAI", page_icon="./resources/cocktail_icon.png",
    initial_sidebar_state="auto"
)

st.markdown("#### Documentation notes:")
st.success('''
           **The landing page.  Allows the user to choose to have
            a general chat with a bartender, or create a recipe.
            Once the recipe is created, they will have the option
            to initiate a chat about the recipe along with several other features.**
              ''')
st.markdown('---')


# Initialize the session state
# def init_session_variables():
#  Initialize session state variables
#    session_vars = [
#    ]
#    default_values = [
#    ]

#    for var, default_value in zip(session_vars, default_values):
#        if var not in st.session_state:
#            st.session_state[var] = default_value

# Create the title using the title class
# This is a custom class that I created in the style.css file
# Set the text to be centered
st.markdown('''<div style="text-align: center;">
<h2 class="title">BarGuru</h2>
<p style "font-weight:100px;">The app that finally answers the question: "What the hell am I going to do with
these 17 bottles of Frangelico that someone accidentally ordered?"</p>
</div>''', unsafe_allow_html=True)
st.text('')

# Create two columns for the home page
col1, col2 = st.columns(2, gap="large")

# With the first column we will display a picture of a cocktail with a "Create a Cocktail" button underneath
# With the second column we will display a picture of a bar with a "Chat with a Bartender" button underneath
with col1:
    # Load in the image of the cocktail
    cocktail_image = Image.open('./resources/cocktail_pic.png')
    # Display the image
    st.image(cocktail_image, use_column_width=True)
    # Create a button to start creating cocktails
    cocktail_button = st.button('Create a Cocktail', use_container_width=True, type='primary')
    if cocktail_button:
        switch_page('Create Cocktails')
        st.rerun()

with col2:
    # Load in the image of the bar
    bar_image = Image.open('./resources/bartenders.png')
    # Display the image
    st.image(bar_image, use_column_width=True)
    # Create a button to start chatting with a bartender
    bartender_button = st.button('Chat with a Bartender', use_container_width=True, type='primary')
    if bartender_button:
        switch_page('General Chat')
        st.rerun()

# Display feedback form
st.markdown('---')
st.markdown('''<div style="text-align: center;">
<h4 class="feedback">We want to hear from you!  Please help us grow by taking a quick
second to fill out the form below and to stay in touch about future developments.  Thank you!</h4>
</div>''', unsafe_allow_html=True)

src = "https://docs.google.com/forms/d/e/1FAIpQLSc0IHrNZvMfzqUeSfrJxqINBVWxE5ZaF4a30UiLbNFdVn1-RA/viewform?embedded=true"
components.v1.iframe(src, height=600, scrolling=True)
