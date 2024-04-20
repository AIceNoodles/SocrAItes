from openai import OpenAI
import streamlit as st
from configs import OAI_MODEL, EXPORT_DIR
from utils import export_current_conversation, num_tokens_from_messages
import pdfplumber
from constants import PromptConstants
from collections import defaultdict


st.title(f"AIce Tutor")
pages = []
# File uploader
uploaded_file = st.file_uploader("Upload your file", type=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv'])
if uploaded_file is not None:
    # Check if the uploaded file is a PDF
    if uploaded_file.type == "application/pdf":
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                # Extract text from the first page
                first_page = pdf.pages[0]
                pages = list(pages)
                extracted_text = first_page.extract_text()
            st.text_area(f"Extracted Text, type {type(pages)}", extracted_text, height=300)
        except Exception as e:
            st.error("Error processing the PDF file.")
            st.write(f"error is {str(e)}")
    else:
        st.write("File uploaded successfully!")

# Create a button
file_text = " ".join(pages[3:6])
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = OAI_MODEL

if 'questions' not in st.session_state:
    st.session_state['questions'] = []

if 'messages' not in st.session_state:
    st.session_state['messages'] = defaultdict(list)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

mode = st.sidebar.radio(
    "Choose your AI Tutor Mode:",
    ('Question', 'Answer')
)

selected_question = st.sidebar.selectbox(
    "Select a question to view responses:",
    options=st.session_state['questions'],
    index=0,
)

if mode == "Answer" and st.session_state['messages'] and selected_question:
    for message in st.session_state.messages[selected_question]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

### Logic for when we listen for user's answer
if mode == "Answer" and selected_question is not None:
    if prompt := st.chat_input("Try to answer:"):
        user_response = "some user response"
        st.session_state['messages'][selected_question].append({"role": "user", "content": user_response})
        with st.chat_message("user"):
            st.markdown(prompt)
        model_response = "some model response"
        st.session_state['messages'][selected_question].append({"role": "assistant", "content": model_response})
        with st.chat_message("assistant"):
            st.markdown(prompt)
        # print(st.session_state['questions'], st.session_state['messages'])
else:
    mode = "Question"
    if prompt := st.chat_input("Ask a question:"):
        # Add question to session state
        with st.chat_message("user"):
            st.markdown(prompt)
        # Process the question
        # Here you would typically send the prompt to the AI model
        full_response = ""
        message_placeholder = st.empty()
        for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": "user", "content": prompt}
                ],
                stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            # message_placeholder.markdown(full_response + "▌")
        # message_placeholder.markdown(full_response)
        with st.chat_message("assistant"):
            st.markdown(full_response)
        response = "Simulated response for demonstration."  # Simulated response
        st.session_state['questions'].append(full_response)
        st.session_state['messages'][full_response].append({"role": "assistant", "content": full_response})
        # print(st.session_state['questions'], st.session_state['messages'])


