""" General Chat page... not tied to a cocktail recipe """
from PIL import Image
from dependencies import get_openai_client
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    page_title="General Chat", page_icon="./resources/bartenders.png", initial_sidebar_state="auto"
)

if "cocktail_chat_messages" not in st.session_state:
    st.session_state.cocktail_chat_messages = None
if "show_recipe" not in st.session_state:
    st.session_state.show_recipe = False

client = get_openai_client()

IMG_PATH = "./resources/mixologist1.png"  # Replace with your image's path
mixologist_image = Image.open(IMG_PATH)

initial_message = {
    "role": "system",
    "content": f"""
    You are a master mixologist who has created a new cocktail recipe
    {st.session_state.current_cocktail} for a user,
    helping them creatively use up their excess inventory.
    They would like to ask you some follow up questions about the recipe.
    Your tone should be warm and welcoming while having high standards and a passion for the
    details. Your recent chat history is {st.session_state.cocktail_chat_messages}.
    """
}

if not st.session_state.cocktail_chat_messages:
    st.session_state.cocktail_chat_messages = [initial_message]

def cocktail_chat():
    """ Chat bot to answer questions about the business plan """
    recipe = st.session_state.current_cocktail

    # Display chat messages from history on app rerun
    for message in st.session_state.cocktail_chat_messages:
        if message["role"] == "assistant":
            with st.chat_message(message["role"], avatar=mixologist_image):
                st.markdown(message["content"])
        elif message["role"] == "user":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input(f"What questions can I answer about the {recipe['name']}?"):
        with st.spinner("Grabbing the shaker..."):
            # Add user message to chat history
            st.session_state.cocktail_chat_messages.append({"role": "user", "content": prompt})

            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant", avatar=mixologist_image):
                message_placeholder = st.empty()
                full_response = ""

            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=st.session_state.cocktail_chat_messages,
                stream=True,
                temperature=0.6,
                max_tokens=750,
            )
        for chunk in response:
          if chunk.choices[0].finish_reason == "stop":
            break
          full_response += chunk.choices[0].delta.content
          message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        st.session_state.cocktail_chat_messages.append({"role": "assistant", "content": full_response})

    show_recipe_button = st.sidebar.button(
        "Show Recipe", use_container_width=True, type='primary'
    )

    if show_recipe_button:
        # Switch the state of the show_recipe variable
        st.session_state.show_recipe = not st.session_state.show_recipe
    if st.session_state.show_recipe:
        # Display the recipe name
        st.sidebar.markdown(f':blue[**Recipe Name:**]  {recipe["name"]}')
        # Convert the ingredients tuples into a list of strings

        # Display the recipe ingredients
        st.sidebar.markdown(':blue[**Ingredients:**]')
        ingredients_list = recipe['ingredients']
        # Convert the ingredients tuple into a list
        for ingredient in ingredients_list:
            st.sidebar.markdown(f'{ingredient}')
        # Display the recipe instructions
        st.sidebar.markdown(':blue[**Directions:**]')
        for direction in recipe['directions']:
            st.sidebar.markdown(f'{direction}')
        # Display the recipe garnish
        st.sidebar.markdown(f':blue[**Garnish:**] {recipe["garnish"]}')
        # Display the recipe glass
        st.sidebar.markdown(f':blue[**Glass:**] {recipe["glass"]}')
        # Display the recipe description
        st.sidebar.markdown(f':blue[**Description:**] {recipe["description"]}')
        # Display the recipe fun fact
        if recipe["fun_fact"]:
            st.sidebar.markdown(f':blue[**Fun Fact:**] {recipe["fun_fact"]}')

    back_to_cocktail_button = st.sidebar.button(
        "Back to Main Cocktail Page", use_container_width=True, type='primary'
    )
    if back_to_cocktail_button:
        st.session_state.cocktail_page = "display_recipe"
        switch_page('Create Cocktails')
        st.rerun()

if __name__ == "__main__":
    cocktail_chat()