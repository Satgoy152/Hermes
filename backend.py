import os
import subprocess
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from a .env file
load_dotenv()
# The GEMINI_API_KEY should be defined in your .env file.
api_key = os.getenv("GEMINI_API_KEY")

def load_prompt():
    """
    Load prompt instructions from a text file (prompt.txt).
    These instructions tell the LLM how to generate the chatbot code.
    """
    try:
        with open("prompt3.txt", "r") as file:
            prompt = file.read()
        return prompt
    except Exception as e:
        # If reading the file fails, return a default prompt.
        print(f"Error loading prompt instructions: {e}")

def generate_code(user_payload):
    """
    Generate code for the AI chatbot by calling the Gemini Flash API using google.generativeai.
    
    Parameters:
        user_payload (dict): The JSON payload containing user inputs.
        
    Returns:
        str: The generated code from the LLM or an error message.
    """
    # Load prompt instructions from an external file (or use the default prompt)
    prompt_instructions = load_prompt()
    
    # Combine prompt instructions and user payload into one message.
    message = f"{prompt_instructions}\n\nUser specifications:\n{user_payload}"
    
    # Configure the Gemini API key
    genai.configure(api_key=api_key)
    
    # Set up the generation configuration for Gemini Flash
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    # Updated system instruction:
    # You are tasked with generating Python code for a Streamlit application that serves as a full conversational chatbot.
    # The generated app must:
    # - Display a header with st.title('Chatbot Interface').
    # - Initialize conversation memory (e.g., using st.session_state.messages) with a default greeting.
    # - Use a chat interface to display conversation history in alternating roles (user and assistant).
    #   For instance, use st.chat_message('user') and st.chat_message('assistant') if available,
    #   or use st.write with clear labels.
    # - Include an input widget (st.chat_input or st.text_input) to capture user queries.
    # - Update the conversation memory upon each new query and display the full conversation.
    # - Be modular, well-commented, and follow PEP8 style guidelines.
    # - Be self-contained so that when saved (e.g., as generated_app.py) and run with
    #   'streamlit run generated_app.py --server.port=8502', it launches the full chatbot interface.
    system_instruction = (
        "You are tasked with generating code that implements a full conversational chatbot interface. "
        "The app should:\n"
        "  - Display a header using st.title('Chatbot Interface').\n"
        "  - Initialize conversation memory using st.session_state (for example, st.session_state.messages) with a default welcome message.\n"
        "  - Display the conversation history in a chat format. If available, use st.chat_message for each message, "
        "    otherwise use st.write with a clear label (e.g., 'User:' and 'Assistant:').\n"
        "  - Provide an input widget for the user to enter their query, such as st.chat_input('Your message') or st.text_input('Enter your query').\n"
        "  - On submission, update the conversation history with the user's message and then display the assistant's response.\n"
        "  - Ensure that the conversation memory is preserved across interactions and that the full conversation is always visible.\n"
        "  - The code should be modular, include inline comments explaining each section, adhere to PEP8 guidelines, "
        "  - The code should talk to google gemini-2.0-flash specfically via API"   
        "and be self-contained so that it can be executed with 'streamlit run generated_app.py --server.port=8502'.\n"
        "Avoid unnecessary libraries and keep the code simple and easy to understand."
    )
    
    # Create the model instance using Gemini Flash, including the detailed system instruction.
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        system_instruction=system_instruction,
    )
    
    # Start a chat session with an empty history
    chat_session = model.start_chat(history=[])
    
    # Send the combined message to the model and return the generated text
    try:
        response = chat_session.send_message(message)
        return response.text
    except Exception as e:
        return f"# Error calling Gemini Flash API: {e}"

def clean_generated_code(code: str) -> str:
    """
    Remove markdown code block delimiters from the generated code.
    """
    # Remove a leading markdown code block if present
    if code.startswith("```python"):
        code = code[len("```python"):].strip()
    # Remove a trailing markdown code block if present
    if code.endswith("```"):
        code = code[:-3].strip()
    return code

def run_generated_app(generated_code, filename="generated_app.py", port=8502):
    """
    Saves the cleaned generated code to a file and launches it as a separate Streamlit app.
    
    Parameters:
        generated_code (str): The Python code generated by the LLM.
        filename (str): The file name to save the generated code.
        port (int): The port on which to run the generated app.
    
    Returns:
        str: The URL where the generated app is accessible.
    """
    # Clean the markdown delimiters from the generated code
    cleaned_code = clean_generated_code(generated_code)
    
    # Save the cleaned code to the specified file.
    try:
        with open(filename, "w") as f:
            f.write(cleaned_code)
    except Exception as e:
        return f"Error saving generated code to file: {e}"
    
    # Launch the generated Streamlit app on the specified port.
    try:
        subprocess.Popen(["streamlit", "run", filename, f"--server.port={port}"])
        return f"http://localhost:{port}"
    except Exception as e:
        return f"Error launching generated app: {e}"

# Example usage:
# if __name__ == "__main__":
#     # For demonstration, we assume a sample user payload.
#     user_payload = {
#         "app_name": "Chatbot Interface",
#         "use_RAG": False,
#         "use_web": False,
#         "specifications": "Full conversational UI with chat history for chatbot interaction.",
#         "file_upload": None
#     }
    
#     # Generate the code using Gemini Flash.
#     generated_code = generate_code(user_payload)
    
#     # Optionally, print the generated code.
#     print("Generated Code:\n", generated_code)
    
#     # Run the generated code as a separate Streamlit app.
#     app_url = run_generated_app(generated_code)
#     print(f"The generated app is running at: {app_url}")