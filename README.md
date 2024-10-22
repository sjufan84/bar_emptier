# Bar Guru v1

Welcome to Bar Guru! This open-source app leverages AI to craft unique and personalized cocktail recipes aimed at helping bars and restaurants use up their dead stock.

## Features
- 🥂 **AI-Powered Cocktail Recipes**: Enter a spirit and optionally a cuisine type and theme, and Bar Guru will generate a unique cocktail featuring the chosen ingredient.
- 💭 **Chat with a bartender**: Engage in a general bar chat or a chat focused on the generated recipe for any necessary follow-ups, questions, adjustments, etc.
- 👩‍🏫 **Training Guide Generator**: Generate a 'one-pager' training guide for staff to engage guests confidently and effectively.
- 🖼️ **Cocktail Image Generator**: Utilize dall-e-3 to generate an image based on the recipe
- 📊 **OpenAI Integration**: Built on top of OpenAI's GPT-4 with structured outputs to ensure correct formatting.
- 🎨 **Streamlit Interface**: Simple and interactive web app, perfect for quick use and experimentation.

## Demo
Here’s a quick peek at the app in action:  
🚀🍸[View the deployed demo here.](https://sjufan84-barguru.streamlit.app/)

## Tech Stack
- **Backend**: [OpenAI API](https://openai.com/)
- **Frontend**: [Streamlit](https://streamlit.io/) (current)
- **Planned Future Framework**: Transition to [Next.js](https://nextjs.org/) or a similar sustainable framework for front-end, FastAPI / Python for backend.

## Getting Started

### Prerequisites
Before you begin, ensure you have the following installed:
- Python 3.9+
- OpenAI API Key (sign up [here](https://openai.com/))
- Streamlit

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/sjufan84/bar_emptier.git
    cd bar_emptier
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up OpenAI API key**:  
   Create a `.env` file in the project root with your API key:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4.  **Run the app**:
     ```bash
     streamlit run Home.py
     ```
**The app will launch locally at http://localhost:8501.**

### Usage
- Open the app in your browser.
- Choose whether to chat with a bartender or generate a cocktail
- If generating a cocktail, select the primary spirit, cuisine type, and theme
- Your cocktail will be generated along with an image.
- You can then chat with a bartender about the cocktail, generate a training guide, etc.

### Contributing
We welcome contributions to improve the app or assist in transitioning to a more sustainable framework like Next.js. Here’s how you can get involved:

- Raise any issues with comments or suggestions on the best path forward to scale the project.
- Fork the repository
- Create a new branch (git checkout -b feature-branch)
- Make your changes
- Submit a pull request
- Feel free to open issues for any bugs or feature requests!

License
This project is licensed under the MIT License - see the LICENSE file for details.

Future Plans
- We’re working on evolving the project to a more robust framework such as Next.js for enhanced scalability and performance, although this is not currently set in stone. Contributions to help with this transition are encouraged!
- We also want to move toward a more robust backend framework and structure for database integrations, etc.  Ideas and comments are welcome.
- We would love to partner with industry leaders including bartenders, distilleries, distributors, and anyone else looking to get involved.
- We are looking for sponsors and sustaining partners.

Contact
If you have any questions or suggestions, feel free to reach out via [e-mail](mailto:barguru@enoughwebapp.com) or [LinkedIn](www.linkedin.com/in/david-s-thomas-1b655254).
