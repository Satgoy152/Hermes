import streamlit as st

# Set the title of the Streamlit application
st.title('Chatbot Interface')

# Initialize conversation memory using st.session_state
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm here to chat with you. How can I help you today?"}]

# Display the conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Input widget for the user to enter their query
prompt = st.chat_input("Your message")

# If a prompt is submitted
if prompt:
    # Add the user's message to the conversation history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display the user's message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate the assistant's response
    # Replace this with your actual chatbot logic (e.g., call to an API, model inference)
    # For demonstration purposes, we'll just echo the user's message back with a twist.

    # Emulate AuditAI specifications based on user request
    response = f"As a friendly counselor for University of Michigan students, after hearing '{prompt}', here's some advice:"

    # Add "advice" with basic example from prompt
    response += f" Consider discussing your degree audit and future plans with an academic advisor for personalized guidance."

    # Add the assistant's response to the conversation history
    st.session_state.messages.append({"role": "assistant", "content": response})
    # Display the assistant's response
    with st.chat_message("assistant"):
        st.markdown(response)

# Run the app: streamlit run your_app_name.py --server.port=8502