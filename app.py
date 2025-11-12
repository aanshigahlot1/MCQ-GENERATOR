import streamlit as st
import google.generativeai as genai # Import Google Gemini
import json
import time # We'll use this for simple retries

# --- Google Gemini API Configuration ---
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20" # Switched to the modern 1.5-flash model

# This is the JSON schema we will request from the model.
RESPONSE_SCHEMA = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "question": {"type": "STRING"},
            "options": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "minItems": 4,
                "maxItems": 4
            },
            "answer": {"type": "STRING"}
        },
        "required": ["question", "options", "answer"]
    }
}

def generate_mcqs(context: str, num_questions: int, api_key: str) -> list | None:
    """
    Calls the Google Gemini API to generate MCQs based on the provided text.
    
    Args:
        context: The source text for generating questions.
        num_questions: The number of questions to generate.
        api_key: The Google API key.

    Returns:
        A list of dictionaries (MCQs) or None if an error occurs.
    """
    
    # Initialize the Google Gemini client
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to configure Gemini client: {e}")
        return None

    # Set up the model generation config to force JSON output
    generation_config = {
        "response_mime_type": "application/json",
    }
    
    model = genai.GenerativeModel(
        GEMINI_MODEL,
        generation_config=generation_config
    )

    system_prompt = (
        "You are an expert quiz creator. Your role is to generate high-quality, "
        "multiple-choice questions (MCQs) based *only* on the text provided by the user. "
        "You must generate exactly four options for each question. "
        "One of these options must be the correct answer, which is directly supported by the text. "
        "The other three options must be plausible but incorrect distractors. "
        "The 'answer' field in your response must exactly match the text of the correct option. "
        "You MUST format your output as a single JSON array of objects, matching this schema:\n"
        f"{json.dumps(RESPONSE_SCHEMA, indent=2)}\n"
        "Do not include any other text or markdown formatting (like ```json) in your response. "
        "Just provide the raw JSON array."
    )
    
    user_prompt = (
        f"Please generate {num_questions} multiple-choice questions from the following text:\n\n"
        f"---BEGIN TEXT---\n{context}\n---END TEXT---"
    )
    
    full_prompt = [system_prompt, user_prompt]

    try:
        response = model.generate_content(full_prompt)
        
        # Extract the JSON string from the response
        json_string = response.text
        
        if not json_string:
            st.error("API returned a successful but empty response.")
            return None
        
        # Parse the JSON string from the model
        mcq_data = json.loads(json_string)
        
        # Sometimes the model might wrap the list in a dictionary, e.g. {"questions": [...] }
        # Let's try to find the list if it's not a list directly
        if isinstance(mcq_data, dict):
            # Try to find a value that is a list
            for key, value in mcq_data.items():
                if isinstance(value, list):
                    mcq_data = value
                    break
            else:
                st.error("The API returned JSON, but not in the expected array format. Please try again.")
                return None

        if not isinstance(mcq_data, list):
             st.error("The API returned JSON, but not in the expected array format. Please try again.")
             return None

        return mcq_data

    except json.JSONDecodeError:
        st.error(f"Failed to decode the API's JSON response. The model might not be following the schema. Response text: {json_string}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while calling the Gemini API: {e}")
        return None

# --- Streamlit App UI ---

st.set_page_config(layout="wide", page_title="MCQ Generator")
st.title("MCQ Generator from Text 🧠")

# Check for API Key in secrets
try:
    API_KEY = st.secrets.get("GOOGLE_API_KEY") # Changed to GOOGLE_API_KEY
    if not API_KEY:
        st.error("GOOGLE_API_KEY not found. Please add it to your .streamlit/secrets.toml file.") # Updated error message
        st.stop()
except Exception:
    st.error("Could not read Streamlit secrets. Are you running this locally with a .streamlit/secrets.toml file?")
    st.stop()


with st.sidebar:
    st.header("How to use")
    st.markdown("""
    1.  Paste any text (e.g., an article, a chapter summary) into the text box on the left.
    2.  Select the number of questions you want to generate.
    3.  Click the **"Generate MCQs"** button.
    4.  The AI will read the text and create questions with options and answers.
    5.  Review the generated questions below!
    """)
    st.divider()
    num_questions = st.number_input("Number of questions to generate:", min_value=1, max_value=10, value=3)

# Main layout
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("Paste your text here:")
    context_text = st.text_area("Source Text", height=500, label_visibility="collapsed")
    
    if st.button("Generate MCQs", type="primary", use_container_width=True):
        if not context_text.strip():
            st.warning("Please paste some text into the box first.")
        else:
            # Generate MCQs
            with st.spinner("Generating... This might take a moment."):
                mcq_list = generate_mcqs(context_text, num_questions, API_KEY)
            
            # Store results in session state to display in the other column
            st.session_state.mcq_list = mcq_list

with col2:
    st.subheader("Generated MCQs")
    
    if 'mcq_list' not in st.session_state or not st.session_state.mcq_list:
        st.info("Click the 'Generate MCQs' button to see your questions here.")
    else:
        # Display the generated MCQs
        for i, mcq in enumerate(st.session_state.mcq_list):
            try:
                st.write(f"**Q{i+1}: {mcq['question']}**")
                
                # Create a list of options for st.radio
                # It's important that len(mcq['options']) is 4, as requested from the model
                options_list = mcq.get('options', [])
                if len(options_list) != 4:
                    st.warning(f"Q{i+1} did not return 4 options. Skipping.")
                    continue
                    
                # Using st.radio to display options.
                # We set it to `disabled=True` as this is a review, not a test.
                st.radio(
                    "Options",
                    options=options_list,
                    key=f"mcq_{i}",
                    label_visibility="collapsed",
                    disabled=True 
                )
                
                # Show the correct answer in an expander
                with st.expander("Show Answer"):
                    st.success(f"Correct Answer: {mcq['answer']}")
                st.divider()
                
            except KeyError as e:
                st.error(f"Error displaying MCQ {i+1}: Missing expected key {e}. Data: {mcq}")
            except Exception as e:
                st.error(f"An unknown error occurred while displaying MCQ {i+1}: {e}")