import logging
import base64
import pdfkit

path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

async def recipe_to_html(recipe: dict):
    """ Convert a recipe to html """
    html_content = f'''<html>
    <head>
    <style>
    body {{
        font-family: Arial, Helvetica, sans-serif;
    }}
    h1 {{
        font-size: 36px;
        color: #1d3557;
    }}
    h2 {{
        font-size: 24px;
        color: #e63946;
    }}
    p {{
        font-size: 18px;
    }}
    ul {{
        font-size: 18px;
    }}
    ol {{
        font-size: 18px;
    }}
    </style>
    </head>
    <body>
    <h1>{recipe["name"]}</h1>
    <h2>Ingredients:</h2>
    <ul>
    '''
    for ingredient in recipe["ingredients"]:
        html_content += f"<li>{ingredient}</li>"
    html_content += "</ul>"
    html_content += f"<h2>Directions:</h2><ol>"
    for direction in recipe["directions"]:
        html_content += f"<li>{direction}</li>"
    html_content += "</ol>"
    html_content += f"<h2>Glass:</h2><p>{recipe['glass']}</p>"
    if "garnish" in recipe:
        html_content += f"<h2>Garnish:</h2><p>{recipe['garnish']}</p>"
    html_content += f"<h2>Description:</h2><p>{recipe['description']}</p>"
    if "fun_fact" in recipe:
        html_content += f"<h2>Fun Fact:</h2><p>{recipe['fun_fact']}</p>"
    html_content += "</body></html>"

    return html_content

async def get_recipe_pdf_download_link(recipe: dict, recipe_name: str):
    html_string = await recipe_to_html(recipe)
    logging.debug("HTML string: %s", html_string)
    pdfkit.from_string(html_string, 'out.pdf', configuration=config)
    download_name = f"{recipe_name}.pdf"
    with open('out.pdf', 'rb') as f:
        pdf_data = f.read()
    b64_pdf = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:file/pdf;base64,{b64_pdf}" download="{download_name}">Download Recipe as PDF</a>'
    return href
