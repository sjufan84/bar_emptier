# This will be the page to handle all of the training materials and questions for the generated cocktails
# The user will be able to generate training materials either for the cocktail or just general bar knowledge

# Initial imports
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# Initiate the session state
def init_cocktail_session_variables():
    # Initialize session state variables
    session_vars = [
        'cocktail_page', 'recipe', 'training_type', 'training_page'
    ]
    default_values = [
        '', '', '', 'get_training_type'
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

# Function to ask the user whether or not they would like to generate training materials for the cocktail
# or just general bar knowledge
def get_training_type():
    # If there is a cocktail in the session state, ask the user if they would like to generate training materials for the cocktail
    # or just general bar knowledge
    if "cocktail" in st.session_state:
        st.write("Would you like to generate training materials for the cocktail or just general bar knowledge?")
        training_type = st.radio("", ("Cocktail", "General Bar Knowledge"))
        training_select_button = st.button(f"Continue to {training_type} Training")
        if training_select_button:
            st.session_state["training_type"] = training_type
            if training_type == "Cocktail":
                # If the user selects cocktail training, set the training page to cocktail training and rerun the page
                st.session_state.training_page = "cockail_training"
                st.experimental_rerun()
            else:
                # If the user selects general bar knowledge training, set the training page to general training and rerun the page
                st.session_state.training_page = "general_training"
                st.experimental_rerun()
    # If there is no cocktail in the session state, ask the user if they would like to generate training materials for just general bar knowledge
    else:
        st.markdown('##### You have not generated a cocktail yet. If you want cocktail specific training materials,\
                    click "Create Cocktail" below.  If you would you like to generate training materials for just general bar knowledge,\
                    select "General Bar Knowledge".')
        st.text("")
        # Add a button for the user to go to cocktail page and create a cocktail
        training_cocktail_button = st.button("Create Cocktail", type='primary', use_container_width=True)
        if training_cocktail_button:
            st.session_state["cocktail_page"] = "get_cocktail_info"
            switch_page("Create Cocktails")
            st.experimental_rerun()
        # Add a button to continue on to general bar knowledge training materials
        general_training_button = st.button("General Bar Training", type='primary', use_container_width=True)
        if general_training_button:
            st.session_state["training_type"] = "General Bar Knowledge"
            st.session_state["training_page"] = "general_training"
            st.experimental_rerun()

# Define the function to generate and display the training materials for the cocktail
def cocktail_training():
    st.write("")

# Define the function to generate and display the training materials for general bar knowledge
def general_training():
    st.markdown("### Future Home of General Training")

# Establish the flow of the page
if st.session_state.training_page == "get_training_type":
    get_training_type()
elif st.session_state.training_page == "cockail_training":
    cocktail_training()
elif st.session_state.training_page == "general_training":
    general_training()