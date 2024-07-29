import streamlit as st
from langchain_community.llms import OpenAI
import os

# Setting the page config
st.set_page_config(layout="wide", page_title="AI Passport Chatbot", page_icon="assistant")

# Getting API Key from environment
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

# Define the model for generating responses
def generate_response(input_text):
    llm = OpenAI(
        model_name='gpt-3.5-turbo-instruct',
        temperature=0.7,
        max_tokens=-1,
        openai_api_key=os.environ['OPENAI_API_KEY']
    )
    return llm(input_text)

# Initializing session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Styling for the app
st.markdown("""
<style>
    .stSubheader {
        margin-bottom: -30px;
    }
    .stMarkdown {
        margin-bottom: -20px;
    }
    .stTextArea {
        margin-top: -10px;
    }
    .reportview-container .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    div[data-testid="stColumns"] > div {
        padding-right: 10px;
    }
    div[data-testid="stColumns"] > div:last-child {
        padding-right: 0px;
    }
    div[data-testid="stColumns"] > div > div.stButton > button {
        height: 50px;
        width: 100%;
        line-height: 50px;
        text-align: center;
        font-size: 16px;
        margin-top: 5px;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Creating subheader
st.subheader("MedChat LLM")

# Chat history display
st.markdown("***Chat History***")
for i, message in enumerate(reversed(st.session_state.messages)):
    if message["role"] == "user":
        col1, col2 = st.columns([4, 1])
        col1.markdown(f"<span style='color: blue;'>**You:** {message['content']}</span>", unsafe_allow_html=True)
    elif message["role"] == "assistant":
        col1, col2 = st.columns([4, 1])
        col1.markdown(f"<span style='color: green;'>**Assistant:** {message['content']}</span>", unsafe_allow_html=True)
        button_html = f"<button onclick=\"navigator.clipboard.writeText('{message['content']}')\">📋 Copy</button>"
        col2.markdown(button_html, unsafe_allow_html=True)

# Export conversation
if st.session_state.messages:
    chat_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages])
    st.download_button("Export Conversation", chat_history, file_name='chat_history.txt', mime='text/plain')

# User input and form for response
with st.form(key='response_form'):
    user_input = st.text_area('Enter your question here:', 'How can I help you today?', label_visibility='collapsed')
    submit_button = st.form_submit_button("Respond")
    if submit_button and user_input:
        response = generate_response(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
