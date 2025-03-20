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

# streamlit dialog for confused button
@st.dialog("Confused?")
def help_user():
    st.write("If you are wondering what your degree progress is looking like, want recommendations based on the classes your are taking, confused on how to match courses with future career goals, and/or just have basic academic advising questions, why wait weeks for advising meetings when you can just spin up your own personalized advisor with all your information?")
    st.write("You can specify some key elements for your advisor chatbot, then upload your audit or transcript during conversation to get personalized recommendations.")
    st.write("Your chatbot will also be trained on UMich course material and catalog to help you in the best way possible!")

def main():
    # Set the page title
    st.title("UMich Personalized Advisor")

    # text for info
    st.text("Create the perfect assistant to help you select classes, stay on track to graduate, and aid you in your career goals. Your advisor will be trained on updated UMich courses, required advisory materials, and more!")

    
    if "Confused?" not in st.session_state:
        if st.button("Confused? Click me!"):
            help_user()
        
        
    
    # Input field for the app name
    # app_name = st.text_input("Enter App Name:")
    app_name = st.text_input("Enter your chatbot's name:", placeholder="My AI Advisor")

    user_name = st.text_input("What's your name:", key="user_name_input", placeholder="Satyam Goyal")
    
    # Checkboxes for additional options
    # use_RAG = st.checkbox("Use RAG")
    # use_web = st.checkbox("Use web")
    user_major = st.text_input("Enter your major:", key="user_major_input", placeholder="Computer Science")

    # Step 1: Choose chatbot type
    chatbot_type = st.multiselect("What type of chatbot would you like?", 
                              ["Career Advice", "Personal Advisor", "Class Advice"], placeholder="Select none, one, or multiple options")


    # for graduaction year
    user_graduation = st.text_input("Enter your graduation semester and year:", key="user_graduation_input", placeholder="Winter 2025")
    
    # A large text area for the user to enter additional specifications
    # specifications = st.text_area("Enter Specifications for your Chatbot:")
    
    # File uploader (only metadata is used, not the entire file content)
    # uploaded_file = st.file_uploader("Upload a file (for metadata only):", type=["txt", "py", "md"])
    
    #tried to make this more User Friendly for clarify of what kind of metadata is extracted
    # File uploader with help text
    # REMOVING FILE UPLOAD FOO MPV1 TESTS --------------------------------------------------------------------------------------------------------
    # uploaded_file = st.file_uploader("Upload a file (Optional)", type=["txt", "py", "md"], help="Only extracts metadata, not file content")

    # # Check if a file is uploaded before extracting metadata
    # if uploaded_file is not None:
    #     file_metadata = get_file_metadata(uploaded_file)
    #     st.write("File Metadata Extracted:", file_metadata)
    # else:
    #     file_metadata = None  # If no file is uploaded, set it to None or handle it appropriately
    # ---------------------------------------------------------------------------------------------------------------------------------------------
    file_metadata = None
    
    # When the user clicks submit, process the inputs
    if st.button("Generate", key="submit_button"):
        # Build a JSON payload with the user inputs

        #making RAG and WEB false for now
        use_RAG = False
        use_web = False

        # payload = {
        #     "app_name": app_name,
        #     "user_name": user_name,
        #     "user_major": user_major,
        #     "user_graduation": user_graduation,
        #     "chatbot_type": chatbot_type,
        #     "use_RAG": use_RAG,
        #     "use_web": use_web,
        #     "specifications": """Create an AI app that chats with University of Michigan students 
        #     in an empathetic way and gives them advice on their degree. Students might give information 
        #     on their audit, courses, grades, future plans, etc. Give them good and friendly advice, 
        #     you are basically a counselor.""",
        #     "file_upload": file_metadata
        # }
        
        payload = {
            "app_name": app_name,
            "user_name": user_name,
            "user_major": user_major,
            "user_graduation": user_graduation,
            "chatbot_type": chatbot_type,
            "use_RAG": use_RAG,
            "use_web": use_web,
            "specifications": """Create an AI app that chats with University of Michigan students 
            in an empathetic way and gives them advice on their degree. Students might give information 
            on their audit, courses, grades, future plans, etc. Give them good and friendly advice, 
            you are basically a counselor.""",
            "file_upload": file_metadata
        }
        
        # Optionally, save the JSON locally for record keeping or further processing
        with open("user_input.json", "w") as f:
            json.dump(payload, f, indent=4)
        
        # Display the submitted data on the page
        # st.write("Submitted Data:")
        # st.json(payload)
        
        # Call the backend function to generate the code via the LLM API (Google Gemeni)
        # generated_code = generate_code(payload)
        with st.spinner("Generating your chatbot..."):
            generated_code = generate_code(payload)

        
        # Display the generated code in a code block
        st.subheader("Generated Code:")
        # st.code(generated_code, language='python')
        # Added a downlaod button
        # st.download_button("Download Code", generated_code, file_name="chatbot.py")

        # Save and run the generated app, then display its URL for interaction
        app_url = run_generated_app(generated_code)

        # After generation, offer action buttons instead of just showing a link
        st.success("Your chatbot is ready! 🚀")
        st.markdown(f"[Click here to interact with your chatbot]({app_url})")
        st.button("Regenerate Code")

if __name__ == "__main__":
    main()