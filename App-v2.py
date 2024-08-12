import streamlit as st
# openai version=1.1.1 is required
import openai
from openai import OpenAI
import os
import pyperclip
import base64
import requests
from pypdf import PdfReader

st.set_page_config(
    layout="wide",
    page_title="AI Passport Chatbot",
    page_icon="assistant"
)

os.environ['OPENAI_API_KEY'] = 'sk-proj-UVeQodPPxVwv0tkDy3BbT3BlbkFJJazWhRRP3uyLFIdfcXmg'
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Function to encode the image
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# Define LLM model
def generate_response(prompt, image=None, pdf=None):
    if image:
        base64_image = encode_image(uploaded_image)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
                }
            ],
            max_tokens=4096,
        )
        return response.choices[0].message.content.strip()
    elif pdf:
        reader = PdfReader(uploaded_text_file)
        page = reader.pages[0]
        text = page.extract_text()

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                    "type": "text",
                    "text": text,
                    },
                ],
                }
            ],
            max_tokens=4096,
        )
        return response.choices[0].message.content.strip()
    else:    
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4096
        )
        return response.choices[0].message.content.strip()

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

st.subheader("MedChat LLM")

# Display chat history
st.markdown("***Chat History***")
for i, message in enumerate(reversed(st.session_state.messages)):
    if message["role"] == "user":
        st.markdown(f"<span style='color: blue;'>**You:** {message['content']}</span>", unsafe_allow_html=True)
        if st.button("📋", key=f"copy_user_{i}"):
            pyperclip.copy(message["content"])
            st.success("Copied to clipboard!")
    elif message["role"] == "assistant":
        st.markdown(f"<span style='color: green;'>**Assistant:** {message['content']}</span>", unsafe_allow_html=True)
        if st.button("📋", key=f"copy_assistant_{i}"):
            pyperclip.copy(message["content"])
            st.success("Copied to clipboard!")
# Export conversation button
if st.session_state.messages:
    chat_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages])
    st.download_button(
        label="Export Conversation",
        data=chat_history,
        file_name='chat_history.txt',
        mime='text/plain'
    )

# User input and response form
with st.form(key='response_form'):
    user_input = st.text_area('Enter your question here:', 'How can I help you today?', label_visibility='collapsed')
    submit_button = st.form_submit_button("Respond")
    # Streamlit file uploader to upload an image
    uploaded_image = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])
    uploaded_text_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if submit_button and user_input:
        if uploaded_image:
            response = generate_response(user_input, image=uploaded_image)
        elif uploaded_text_file:
            response = generate_response(user_input, pdf=uploaded_text_file)
        else:
            response = generate_response(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
