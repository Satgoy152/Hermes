# Import necessary libraries
import streamlit as st
import google.generativeai as genai
import os
import tempfile
from pypdf import PdfReader

#from interaction import get_context_from_vector_db # no RAG so remove
from dotenv import load_dotenv
import time

# load environment
def load_vars():
    load_dotenv()

    # Configure page
    st.set_page_config(
        page_title="Larry",
        layout="wide"
    )

    # Initialize Gemini API
    # Replace API_KEY with actual implementation for environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

    # Configure the generation parameters
    generation_config = {
        "temperature": 0.9,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }

    # Create a system instruction based on user preferences
    system_instruction = """
    You are an academic advisor assistant for University of Michigan students specializing in computer science programs.
    Your name is larrry and you're speaking with neeyam who is set to graduate in December 2025.
    You provide Class Advice in an empathetic and supportive manner.

    When responding to the student:
    1. Reference information from their academic transcript when relevant
    2. Provide specific, actionable advice related to their major and graduation timeline
    3. Be encouraging and supportive, focusing on solutions rather than problems
    4. Consider University of Michigan's specific academic policies and requirements
    5. If you don't know something, be honest and suggest they speak with a human advisor

    Maintain a friendly, helpful tone throughout the conversation. BE CONCISE WITH YOUR RESPONSES!

    For tables/lists, use markdown formatting to ensure clarity.
    For example:
    | Course Name | Credits | Grade |
    |-------------|---------|-------|
    | Math 101   | 4       | A     |


    Providing Courses: When you recommend courses, also give a link for them with https://atlas.ai.umich.edu/course/*department*%20*course_number*. Example for EECS 370, give the url: https://atlas.ai.umich.edu/course/EECS%20370/


    """

    # Initialize Gemini model
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-preview-04-17",
        generation_config=generation_config,
        system_instruction=system_instruction
    )

    # Initialize chat session
    def create_chat_session():
        return model.start_chat(history=[])

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi neeyam! I'm larrry, your academic advisor assistant for computer science at the University of Michigan. I'd be happy to help you with your academic journey towards your December 2025 graduation. Feel free to upload your transcript or ask me any questions about your courses, grades, or academic plans!"}]

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = create_chat_session()

    if "transcript_text" not in st.session_state:
        st.session_state.transcript_text = None

# Function to extract text from PDF transcript
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

# Function to get relevant context from vector database
# def get_relevant_context(query): #no rag so comment out
#     try:
#         context = get_context_from_vector_db(query)
#         return context
#     except Exception as e:
#         st.error(f"Error retrieving context: {e}")
#         return ""

# Function to process transcript and extract key information
def process_transcript(transcript_text):
    # This function would parse the transcript text and extract
    # courses, grades, GPA, etc. For now, we'll just return the raw text
    # In a production version, this should be enhanced with more robust parsing
    return transcript_text

# Function to generate response using Gemini
def generate_response(prompt, transcript_info=None):
    try:
        # Get relevant context from vector database
        #context = get_relevant_context(prompt) # no rag so comment out
        context = None
        # Construct full prompt with context and transcript info
        full_prompt = prompt
        
        if context:
            full_prompt += f"\n\nRelevant Database Context information: {context}"
            
        if transcript_info:
            full_prompt += f"\n\nFrom student's transcript: {transcript_info}"
        
        # Get response from Gemini
        response = st.session_state.chat_session.send_message(full_prompt, stream = False) # streaming is important
        return response
    except Exception as e:
        return f"I'm having trouble generating a response right now. Error: {e}"

def app_page():
    # load_vars()
    
    # Main app layout
    st.title("Larry")
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
            print(response)
            # Display assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ''
                assistant_response = response
                # Streams in a chunk at a time
                for chunk in response:
                    # Simulate stream of chunk
                    # TODO: Chunk missing `text` if API stops mid-stream ("safety"?)
                    try:
                        print(chunk.text.split(' '))
                        for ch in chunk.text.split(' '):
                            full_response += ch + ' '
                            time.sleep(0.05)
                            # Rewrites with a cursor at end
                            message_placeholder.write(full_response + '▌')
                    except AttributeError:
                        continue # skip the rest and iterate
                # Write full message with placeholder
                message_placeholder.write(full_response)
                print(full_response)

            
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