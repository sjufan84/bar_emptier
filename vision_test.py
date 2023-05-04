# %%
import streamlit as st
import os
import pdfplumber
import requests
from dotenv import load_dotenv
load_dotenv()
import openai
from google.oauth2 import service_account
from spellchecker import SpellChecker
from Home import get_menu_cocktail_recipe
# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")

credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])



if "sos_recipe" not in st.session_state:
    st.session_state.sos_recipe = ""
if "sos_page" not in st.session_state:
    st.session_state.sos_page = "upload menu"
if "sos_question" not in st.session_state:
    st.session_state.sos_question = ""
if "sos_answer" not in st.session_state:
    st.session_state.sos_answer = ""

def extract_pdf(pdf_file):
    # Here we are going to use the pdfplumber library to extract the text from the PDF file
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# %%
from google.cloud import vision

def detect_document(uploaded_image):

    client = vision.ImageAnnotatorClient(credentials=credentials)

    #with io.BytesIO(uploaded_image) as image_file:
    #    content = image_file

    #image = vision.Image(uploaded_image)

    response = client.document_text_detection(image=uploaded_image)

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            print('\nBlock confidence: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
                print('Paragraph confidence: {}'.format(
                    paragraph.confidence))

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    print('Word text: {} (confidence: {})'.format(
                        word_text, word.confidence))

                    for symbol in word.symbols:
                        print('\tSymbol: {} (confidence: {})'.format(
                            symbol.text, symbol.confidence))
    
    response_text = response.full_text_annotation.text


    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    
    return response_text

# %%

# Define a function to run the extracted text through a spellchecker
def spellcheck_text(text):

    # Load the custom domain-specific list
    with open("./resources/new_ingredients.txt", "r") as file:
        cooking_terms = [line.strip() for line in file]

    # Initialize the spell-checker
    spell = SpellChecker(language='en')
    spell.word_frequency.load_words(cooking_terms)

    # Tokenize the returned text from the Vision model`)
    tokens = text.split()

    # Correct the misspelled words
    corrected_tokens = []
    for token in tokens:
        if token not in cooking_terms:
            corrected = spell.correction(token)
            if corrected:
                corrected_tokens.append(corrected)
            else:
                corrected_tokens.append(token)
        else:
            corrected_tokens.append(token)

    # Reconstruct the corrected text
    corrected_text = ' '.join(corrected_tokens)

    return corrected_text



def extract_text_from_txt(file):
    # Extract text from a text file
    return file.read()

# We need two functions for feeding extracted text to the OpenAI API -- 1 for text and pdf that uses GPT 3.5 turbo, and one for photots that uses GPT 4.
# The extracted text from photos generally needs to be cleaned up a bit more and needs a more powerful model to handle it.

def text_menu_edit(menu):
    # Use the OpenAI API to re-format the menu

    # Use the OpenAI API to re-format the menu

    messages = [
        {
            "role": "system",
            "content": f"You are an amazingly helpful assistant restauranteur who edits user's menus in a format to make it readable,\
                if necessary, and be able to answer questions about it.."
        },
        {
            "role": "user",
             "content" : f"""
             Can you help me format this menu {menu} to make it more readable, if needed, and to be able to answer questions about it?  Please stay as true to the original menu {menu} as possible.
            """
        },
    ]


           # Use the OpenAI API to generate the menu
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = messages,
            max_tokens=750,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            temperature=0.6,
            n=1,
            top_p =1
        )
        edited_menu = response.choices[0].message.content

    except (requests.exceptions.RequestException, openai.error.APIError):

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages = messages,
                max_tokens=750,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                temperature=0.6,
                n=1,
                top_p =1
            )
            edited_menu = response.choices[0].message.content
        except (requests.exceptions.RequestException, openai.error.APIError):

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                messages = messages,
                max_tokens=750,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                temperature=0.6,
                n=1,
                top_p =1
            )
            edited_menu = response.choices[0].message.content
       
    return edited_menu



def photo_menu_edit(menu):
    # Use the OpenAI API to re-format the menu

    messages = [
        {
            "role": "system",
            "content": f"You are an amazingly helpful assistant restauranteur who edits user's menus to make them more readable."
        },
        {
            "role": "user",
             "content" : f"""
             Can you help me format this menu {menu} to make it as readable as possible?  Please stay as true to the original menu {menu} as possible.
            """
        },
    ]

           # Use the OpenAI API to generate a menu
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages = messages,
            max_tokens=750,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            temperature=0.6,
            n=1,
            top_p =1
        )
        edited_menu = response.choices[0].message.content

    except (requests.exceptions.RequestException, openai.error.APIError):

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-0314",
                messages = messages,
                max_tokens=750,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                temperature=0.6,
                n=1,
                top_p =1
            )
            edited_menu = response.choices[0].message.content
        except (requests.exceptions.RequestException, openai.error.APIError):

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages = messages,
                max_tokens=750,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                temperature=0.6,
                n=1,
                top_p =1
            )
            edited_menu = response.choices[0].message.content
       
    return edited_menu

def get_menu_sos_answer(menu,question):
    
    messages = [
    {
        "role": "system",
        "content": f"You are the most amazing and knowledgeable restauranteur who answers user's questions about\
                    a restaurant menu {menu}."
                
    },
    {
        "role": "user",
        "content": f"I have this menu {menu}, and I was hoping you could answer my question {question} about it."
                    
    },
    ]

      # Use the OpenAI API to generate a menu
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = messages,
            max_tokens=750,
            frequency_penalty=0.5,
            presence_penalty=0.75,
            temperature=1,
            n=1
        )
        answer = response.choices[0].message.content

    except (requests.exceptions.RequestException, openai.error.APIError):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages = messages,
            max_tokens=500,
            frequency_penalty=0.2,
            temperature = 1, 
            n=1, 
            presence_penalty=0.2,
        )
        answer = response.choices[0].message.content

    return answer


def upload_menu():
    st.warning('*Please note: we will do our best to re-format your menu into one that is as clean and easy to read\
               as possible. Especially if you are uploading an image/photo of the menu, it may not be perfect, but you\
               should still be able to ask questions about it, and will have the opportunity to edit it after as well.*')
    
    menu_files = st.file_uploader("Upload one or multiple menu files", type=["txt", "pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)
    

    menu_text_area = st.text_area("Or copy and paste the menu text here")
    submit_menu_button = st.button("Submit menu", type='primary')

    if submit_menu_button and menu_files:
        with st.spinner("Extracting and cleaning menu text. If uploading from photos, this will take a minute..."):
            full_menu_text = extract_and_concatenate_text(menu_files, menu_text_area)
            menu_edited = edit_menu(full_menu_text, menu_files)

            st.session_state.sos_menu = menu_edited
            st.session_state.sos_page = "user edit menu"
            st.experimental_rerun()
    elif submit_menu_button and menu_text_area:
        with st.spinner("Reading and formatting menu..."):
            menu_edited = text_menu_edit(menu_text_area)
            st.session_state.sos_menu = menu_edited
            st.session_state.sos_page = "user edit menu"
            st.experimental_rerun()
    else:
        st.warning("Please upload a menu file or copy and paste the menu text into the text box above.  In addition to a food menu,\
                   you can also upload or paste an existing cocktail menu so the model does not create a recipe too similar\
                   to ones you currently feature.  Ensure images are formatted with the\
                   extension .jpg, .jpeg, or .png.")


def extract_and_concatenate_text(menu_files, menu_text_area):
    allowed_image_types = ["image/jpeg", "image/png", "image/jpg"]
    full_menu_text = ""

    for menu_file in menu_files:
        if menu_file.type == "application/pdf":
            menu_text = extract_pdf(menu_file)
        elif menu_file.type == "text/plain":
            menu_text = extract_text_from_txt(menu_file)
        elif menu_text_area != "":
            menu_text = menu_text_area
        elif menu_file.type in allowed_image_types:
            menu_text = detect_document(menu_file)
            menu_text = spellcheck_text(menu_text)
        else:
            st.write(f"Unsupported file type: {menu_file.type}")
            continue

        full_menu_text += menu_text + "\n\n"

    return full_menu_text


def edit_menu(full_menu_text,  menu_files):
    allowed_image_types = ["image/jpeg", "image/png", "image/jpg"]
    last_uploaded_file = menu_files[-1]

    if last_uploaded_file.type in allowed_image_types:
        return photo_menu_edit(full_menu_text)
    else:
        return text_menu_edit(full_menu_text)

       
      

def user_edit_menu():
    st.markdown("**Extracted menu text:**")
    user_menu_text = st.text_area('Make any edits to the menu text you need to here. The model is very good at understanding\
                                    the text of the menu, regardless of format, but there may be wording or abbreviations, etc.\
                                    that need to be fixed. A good rule of thumb is, if you cannot understand the text, the model probably can\'t either.\
                                    Once you are ready, click the "Ask Question" below to ask your question about the menu', height=300, value=st.session_state.sos_menu)
    submit_menu_button = st.button("Create your cocktail", type='primary')
    if submit_menu_button:
        st.session_state.sos_menu = user_menu_text
        st.session_state.sos_page = "create cocktail"
        st.experimental_rerun()

def question_form():
    st.markdown("Your edited menu text:")
    st.write(st.session_state.sos_menu)
    
    st.markdown("**Ask a question about the menu**")
    question = st.text_area("", height=150)

    submit_question_button = st.button("Submit Question")
    if submit_question_button:
        with st.spinner("Thinking..."):
            st.session_state.sos_answer = get_menu_sos_answer(st.session_state.sos_menu, question)
            st.session_state.sos_question = question
            st.session_state.sos_page = "display answer"
            st.experimental_rerun()

    upload_different_menu_button = st.button("Upload a Different menu")
    if upload_different_menu_button:
        st.session_state.sos_page = "upload menu"
        st.experimental_rerun()

# Define a function to allow the user to create a cocktail based on the menu text
def create_cocktail():
    # Build the form 
    with st.form('bar_emptier'):
        # Start by getting the input for the liquor that the user is trying to use up
        liquor = st.text_input('What liquor are you trying to use up?')
        # Allow the user to choose what type of cocktail from "Classic", "Craft", "Standard"
        cocktail_type = st.selectbox('What type of cocktail are you looking for?', ['Classic', 'Craft', 'Standard'])
        
        # Create the submit button
        cocktail_submit_button = st.form_submit_button(label='Create your cocktail!')
        if cocktail_submit_button:
            with st.spinner('Creating your cocktail recipe.  This may take a minute...'):
                get_menu_cocktail_recipe(liquor, cocktail_type, st.session_state.sos_menu)
                st.session_state.sos_page = "display recipe"
                st.experimental_rerun()


def display_recipe():
    st.markdown('##### Here is your recipe! 🍸🍹')
    st.write(st.session_state.recipe)
    st.write(st.session_state.response)

if st.session_state.sos_page == "upload menu":
    upload_menu()
elif st.session_state.sos_page == "question form":
    question_form()
elif st.session_state.sos_page == "display recipe":
    display_recipe()
elif st.session_state.sos_page == "user edit menu":
    user_edit_menu()
elif st.session_state.sos_page == "create cocktail":
    create_cocktail()





