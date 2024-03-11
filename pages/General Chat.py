""" General Chat page... not tied to a cocktail recipe """
from PIL import Image
from dependencies import get_openai_client
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("openai").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="General Chat", page_icon="./resources/bartenders.png", initial_sidebar_state="auto"
)

client = get_openai_client()

IMG_PATH = "./resources/mixologist1.png"  # Replace with your image's path
mixologist_image = Image.open(IMG_PATH)

# Initialize the session state
def init_general_chat_session_variables():
    # Initialize session state variables
    session_vars = [
        "general_chat_messages"
    ]
    default_values = [
        None
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

# Initialize the session state variables
init_general_chat_session_variables()

initial_message = {
    "role": "system",
    "content": f"""You are a master mixologist and bar manager, helping a user create cocktails,
    craft menus, manage their inventory, and answer general bar questions.  Your tone
    should be warm and welcoming while having high standards and a passion for the
    details. Your recent chat history is {st.session_state.general_chat_messages}.
    Remeber you are a master mixologist and business person, not an AI, so make sure to
    stay in and do not break character.Keep your answer concise and to the point, but ask
    clarifying questions if needed."""
}
logger.debug("Initial message: %s", initial_message)

if not st.session_state.general_chat_messages:
    st.session_state.general_chat_messages = [initial_message]

def general_chat():
    """ Chat bot to answer general bar questions """
    if len(st.session_state.general_chat_messages) == 1:
        st.markdown(
            """:violet[**The goal with this page is to help answer general bar questions.\
            Of course you can always copy and paste a cocktail you have created to get answers\
            to questions about that specific cocktail.  If you would like to create a cocktail,
            select 'Create Cocktail' from the side bar.  Cheers!**]"""
        )

    # Display chat messages from history on app rerun
    for message in st.session_state.general_chat_messages:
        if message["role"] == "assistant":
            with st.chat_message(message["role"], avatar=mixologist_image):
                st.markdown(message["content"])
        elif message["role"] == "user":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Let's get mixing!"):
        with st.spinner("Grabbing the shaker..."):
            # Add user message to chat history
            st.session_state.general_chat_messages.append({"role": "user", "content": prompt})
            logger.debug("Chat history: %s", st.session_state.general_chat_messages)

            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant", avatar=mixologist_image):
                message_placeholder = st.empty()
                full_response = ""

            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=st.session_state.general_chat_messages,
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
        st.session_state.general_chat_messages.append({"role": "assistant", "content": full_response})

    create_cocktail_button = st.sidebar.button(
        "Create Cocktail", use_container_width=True, type='secondary'
    )

    if create_cocktail_button:
        switch_page("Create Cocktails")
        st.rerun()

    clear_chat_button = st.sidebar.button(
        "Clear Chat", use_container_width=True, type='secondary'
    )
    if clear_chat_button:
        st.session_state.general_chat_messages = [initial_message]
        st.rerun()

    home_button = st.sidebar.button(
        "Home", use_container_width=True, type='secondary'
    )
    if home_button:
        switch_page("Home")
        st.rerun()

    st.sidebar.link_button(
        label = ":green[**Please help us out by filling out a quick survey about your experience!**]",
        url = "https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAVtWsJ1UM0xEWjVGMVEyM1hURldWWU5JRVhPWUJZVy4u",
        type = "secondary",
        use_container_width=False)

if __name__ == "__main__":
    general_chat()
