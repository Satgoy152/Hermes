import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from a .env file
load_dotenv()

# The GEMINI_API_KEY should be defined in your .env file.
api_key = os.getenv("GEMINI_API_KEY")

# Configure the Gemini API key
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("GEMINI_API_KEY not found. Please set it in your .env file.")
    st.stop()

# Define the system instruction to guide the chatbot's behavior
system_instruction = """
You are AuditAI, an empathetic and helpful AI assistant designed to advise University of Michigan students on their academic journeys. 
Students will provide information about their academic audit, courses, grades, future plans, and related topics.
Your role is to offer friendly, supportive, and insightful advice, acting as a virtual academic counselor. 
Maintain a positive and encouraging tone, focusing on the student's well-being and academic success.

Specifically, when interacting with students:
- Demonstrate empathy and understanding.
- Offer constructive advice based on the information they provide.
- Help them explore different academic options and potential career paths.
- Offer strategies for improving their grades or managing their workload.
- Be mindful of their emotional state and offer appropriate encouragement.

Do not provide answers for other questions unrelated to being a counselor to University of Michigan students.
"""


# Model configuration
generation_config = genai.types.GenerationConfig(
    candidate_count=1,
    max_output_tokens=2048,
)

# Initialize the Gemini Flash model with system instructions
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        system_instruction=system_instruction,
    )
except Exception as e:
    st.error(f"Error initializing Gemini Flash model: {e}")
    st.stop()

# Initialize chat session
chat_session = model.start_chat(history=[])

# Streamlit app
st.title("AuditAI - University of Michigan Student Advisor")

# Initialize conversation history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm AuditAI, your academic advisor. How can I help you today?",
        }
    ]

# Display the conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Get user input
user_query = st.chat_input("Enter your query")

# Process user input
if user_query:
    # Add user message to the state
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Get response from Gemini Flash API
    try:
        response = chat_session.send_message(user_query)
        assistant_response = response.text
    except Exception as e:
        assistant_response = f"Error calling Gemini Flash API: {e}"

    # Add assistant response to the state
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_response}
    )
    with st.chat_message("assistant"):
        st.markdown(assistant_response)