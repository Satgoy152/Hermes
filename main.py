import streamlit as st
import json
from backend import generate_code, run_generated_app  # Import the backend function to call the LLM API

def get_file_metadata(uploaded_file):
    """
    Extract metadata from the uploaded file.
    This function only returns file details without reading the full content.
    """
    if uploaded_file is not None:
        return {
            "filename": uploaded_file.name,
            "filetype": uploaded_file.type,
            # Optionally, you could include file size or other metadata if needed.
        }
    return None

def main():
    # Set the page title
    st.title("Hermes - AI Chatbot Code Generator")
    
    # Input field for the app name
    app_name = st.text_input("Enter App Name:", value="Audit AI")
    
    # Checkboxes for additional options
    use_RAG = st.checkbox("Use RAG")
    use_web = st.checkbox("Use web")
    
    # A large text area for the user to enter additional specifications
    specifications = st.text_area("Enter Specifications for your Chatbot:", value="Create an AI app that chats with Unversity of Michigan students in an empathetic way and gives them advice on their degree. Students might give information on their audit, courses, grades, future plans, etc. Give them good and friendly advice you are basically a counselor.")
    
    # File uploader (only metadata is used, not the entire file content)
    uploaded_file = st.file_uploader("Upload a file (for metadata only):", type=["txt", "py", "md"])
    file_metadata = get_file_metadata(uploaded_file)
    
    # When the user clicks submit, process the inputs
    if st.button("Submit"):
        # Build a JSON payload with the user inputs
        payload = {
            "app_name": app_name,
            "use_RAG": use_RAG,
            "use_web": use_web,
            "specifications": specifications,
            "file_upload": file_metadata
        }
        
        # Optionally, save the JSON locally for record keeping or further processing
        with open("user_input.json", "w") as f:
            json.dump(payload, f, indent=4)
        
        # Display the submitted data on the page
        st.write("Submitted Data:")
        st.json(payload)
        
        # Call the backend function to generate the code via the LLM API (Google Gemeni)
        generated_code = generate_code(payload)
        
        # Display the generated code in a code block
        st.subheader("Generated Code:")
        st.code(generated_code, language='python')

        # Save and run the generated app, then display its URL for interaction
        app_url = run_generated_app(generated_code)
        st.success(f"Your generated chatbot app is running at [this URL]({app_url}). Click to interact!")

if __name__ == "__main__":
    main()