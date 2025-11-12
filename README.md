Streamlit MCQ Generator Project

This project is a web application built with Streamlit that uses the Google Gemini API to generate multiple-choice questions (MCQs) from a user-provided text.

Project Structure

mcq-generator/
├── .streamlit/
│   └── secrets.toml     # Stores your secret API key
├── mcq_generator.py     # The main Streamlit app code
└── requirements.txt     # Python dependencies


How to Run This Project Locally

Follow these steps to get the app running on your own machine.

1. Get Your Google API Key

You need an API key to use the Google Gemini models.

Go to Google AI Studio (makers.google.com/aistudio).

Sign in with your Google account.

On the left-hand menu, click "Get API key".

Click "Create API key" (you may need to create a new project).

Copy the generated API key.

2. Set Up Your Project Folder

Create a new folder for your project (e.g., mcq-generator).

Inside that folder, save the mcq_generator.py file.

Inside that same folder, save the requirements.txt file.

Create a new folder inside mcq-generator named .streamlit.

Inside the .streamlit folder, create a new file named secrets.toml.

3. Add Your API Key to secrets.toml

Open the .streamlit/secrets.toml file (which you just created) and add the following line, pasting your API key in place of the placeholder:

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY_GOES_HERE"


4. Install Dependencies

It's highly recommended to use a virtual environment to keep your project dependencies separate.

# Navigate to your project directory
cd mcq-generator

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install the required packages
pip install -r requirements.txt


5. Run the Streamlit App

With your virtual environment active and dependencies installed, run the following command in your terminal:

streamlit run app.py


Streamlit will start a local server and open the app in your web browser!
