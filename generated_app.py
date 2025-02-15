import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from pypdf import PdfReader

# Load environment variables from a .env file
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(page_title="Audit AI Chatbot")

# Access the Gemini API key from the environment variables
api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is available
if not api_key:
    st.error("GEMINI_API_KEY not found. Please set it in your .env file.")
    st.stop()

# Configure the Gemini API
genai.configure(api_key=api_key)

# Define the system instruction for the Gemini model
system_instruction = """You are a helpful and empathetic counselor for University of Michigan students. Your role is to provide advice and guidance to students regarding their degree, career, and academic plans. Be friendly and supportive, and tailor your advice to the student's specific situation and goals.  You are currently helping Akshey, a CS student looking for Career advice. """

# Define generation configuration for the Gemini model
generation_config = genai.types.GenerationConfig(
    candidate_count=1,
    max_output_tokens=2048,
)

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    system_instruction=system_instruction,
)

# Initialize the chat session within the app's session state
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

chat_session = st.session_state.chat_session

# Initialize messages in session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello Akshey! I'm here to help you with your career or academic questions. I am excited to help you with your career plans!"}]

# Upload file functionality
uploaded_file = st.file_uploader("Upload your audit:", type=["pdf", "txt"])

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {e}"

# If a file is uploaded, process it and add its content to the chat session
if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension == "pdf":
        pdf_text = extract_text_from_pdf(uploaded_file)
        if "Error" not in pdf_text:
             chat_session.history.append({"role": "user", "parts": [{"text": pdf_text}]})
        else:
             st.error(pdf_text)
    elif file_extension == "txt":
        text = uploaded_file.read().decode()
        chat_session.history.append({"role": "user", "parts": [{"text": text}]})
    else:
        st.error("Unsupported file type. Please upload a PDF or TXT file.")

# Display the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Ask me about your degree and future!")

# Function to get response from Gemini
def get_gemini_response(message):
    """
    Sends a message to the Gemini Flash API and returns the response.
    Handles potential API errors gracefully.
    """
    try:
        response = chat_session.send_message(message)
        return response.text
    except Exception as e:
        return f"Error calling Gemini Flash API: {e}"

# If the user has entered a prompt
if prompt:
    # Add user message to the chat history in session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in the chat interface
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from Gemini
    full_response = get_gemini_response(prompt)

    # Add assistant's response to the chat history in session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    # Display assistant's response in the chat interface
    with st.chat_message("assistant"):
        st.markdown(full_response)