import streamlit as st
import json
from backend import generate_code, run_generated_app  # Import the backend function to call the LLM API
from archived.generated_app import app_page
import google.generativeai as genai
import os
from pypdf import PdfReader
from dotenv import load_dotenv
import tempfile
from archived.interaction import get_context_from_vector_db
import time
from llm_response import CounselorBot


st.set_page_config(
    page_title="Hermes",
    layout="centered"
)
# Initialize chat session
def create_chat_session():

    chatbot = CounselorBot()
    # Configure page
    
    st.session_state.messages.append({"role": "assistant", "content": "Hello! I'm your personalized academic advisor. How can I assist you today?"})
    
    return chatbot
def generate_response(prompt, transcript_info=None):
    try:
        # Get relevant context from vector database
        full_prompt = prompt
            
        if transcript_info:
            if not st.session_state.transcript_used:
                # Use the transcript information to provide context
                full_prompt += f"\n\nFrom student's transcript: {transcript_info}"
                st.session_state.transcript_used = True
            # full_prompt += f"\n\nFrom student's transcript: {transcript_info}"
        
        # Get response from Gemini
        response = st.session_state.chat_session.chat_stream(full_prompt)
        return response
    except Exception as e:
        return f"I'm having trouble generating a response right now. Error: {e}"
    
    
def app_page():
    # load_vars()
    # Main app layout
    st.title(st.session_state.payload['app_name'])
    st.markdown("### Your University of Michigan Academic Advisor Assistant")

    # Sidebar for transcript upload
    with st.sidebar:
        st.header("Upload Your Transcript")
        uploaded_file = st.file_uploader("Upload your academic transcript (PDF)", type="pdf")
        
        if uploaded_file:
            with st.spinner("Processing transcript..."):
                # Save uploaded file to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # Extract text from PDF
                transcript_text = extract_text_from_pdf(uploaded_file)
                
                if transcript_text:
                    # Process transcript text to extract information
                    st.session_state.transcript_text = process_transcript(transcript_text)
                    st.session_state.transcript_used = False
                    st.success("Transcript uploaded and processed successfully!")
                    
                    # Display a sample of the extracted text
                    st.markdown("### Transcript Preview")
                    st.markdown(transcript_text[:500] + "..." if len(transcript_text) > 500 else transcript_text)
                else:
                    st.error("Failed to extract text from the transcript. Please ensure it's a valid PDF.")

    # Display chat messages
    st.markdown("### Chat")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your academic journey..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response
        with st.spinner("Thinking..."):
            transcript_info = st.session_state.transcript_text if st.session_state.transcript_text else None
            response = generate_response(prompt, transcript_info)
            # Display assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ''
                assistant_response = response
                # Streams in a chunk at a time
                for chunk in response.split(' '):
                    # Simulate stream of chunk
                    # TODO: Chunk missing `text` if API stops mid-stream ("safety"?)
                    try:
                        
                        full_response += chunk + ' '
                        time.sleep(0.05)
                        # Rewrites with a cursor at end
                        message_placeholder.write(full_response + '▌')
                    except AttributeError:
                        continue # skip the rest and iterate
                # Write full message with placeholder
                message_placeholder.write(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # Feedback to the chat session
    selected = st.feedback("thumbs")
    if selected is not None:
        sentiment = None
        if selected == 0:
            sentiment = "Negative"
        else:
            sentiment = "Positive"
        

    # Add footer with usage instructions
    st.markdown("---")
    st.markdown("#### How to use this advisor:")
    st.markdown("1. Upload your academic transcript (PDF) using the sidebar")
    st.markdown("2. Ask questions about your courses, grades, degree requirements, or future plans")
    st.markdown("3. Get personalized advice based on your academic history and goals")

# if "chat_session" not in st.session_state:
#     st.session_state.chat_session = False


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "transcript_text" not in st.session_state:
    st.session_state.transcript_text = None

def process_transcript(transcript_text):
    # This function would parse the transcript text and extract
    # courses, grades, GPA, etc. For now, we'll just return the raw text
    # In a production version, this should be enhanced with more robust parsing
    return transcript_text


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


def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return None

# streamlit dialog for confused button
@st.dialog("Confused?")
def help_user():
    st.write("If you are wondering what your degree progress is looking like, want recommendations based on the classes your are taking, confused on how to match courses with future career goals, and/or just have basic academic advising questions, why wait weeks for advising meetings when you can just spin up your own personalized advisor with all your information?")
    st.write("You can specify some key elements for your advisor chatbot, then upload your audit or transcript during conversation to get personalized recommendations.")
    st.write("Your chatbot will also be trained on UMich course material and catalog to help you in the best way possible!")

def main():
    if "created" not in st.session_state:
        st.session_state.created = False

    if not st.session_state.created:
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
            # save to session state
            st.session_state.payload = payload
            
            # Optionally, save the JSON locally for record keeping or further processing
            with open("user_input.json", "w") as f:
                json.dump(payload, f, indent=4)
            
            
            # Call the backend function to generate the code via the LLM API (Google Gemeni)
            # generated_code = generate_code(payload)
            with st.spinner("Generating your chatbot..."):
                generated_prmpt = generate_code(payload)

            run_generated_app(generated_prmpt)

            st.session_state.created = True

            if "chat_session" not in st.session_state:
                st.session_state.chat_session = create_chat_session()
            # Display the generated code in a code block
            st.subheader("Generated Code:")
            # st.code(generated_code, language='python')
            # Added a downlaod button
            st.button("Open Chatbot", key="open_chatbot_button")
    else:
    # Save and run the generated app, then display its URL for interaction
        app_page()

        # After generation, offer action buttons instead of just showing a link
        st.success("Your chatbot is ready! 🚀")
        # st.markdown(f"[Click here to interact with your chatbot]({app_url})")
        # st.button("Regenerate Code")  

if __name__ == "__main__":
    main()
