import streamlit as st
from document_service import DocumentService
import time

# Function to load a document
def load_document(document_id, url, tenant_id):
    if not document_id or not url or not tenant_id:
        st.error("document_id, tenant_id, and url are required")
        return

    DocumentService.load_document(document_id, url, tenant_id)
    st.success("Document loaded successfully")
    st.balloons()

# Function to ask a question with streaming response
def ask_question(question, tenant_id):
    if not question or not tenant_id:
        st.error("Question and tenant_id are required")
        return

    # Container for the streaming response
    response_container = st.empty()
    response_text = ""

    # Simulate streaming the response
    for char in DocumentService.get_answer(question, tenant_id)['result']:
        response_text += char
        response_container.write(response_text)
        time.sleep(0.01)  # Add a small delay to simulate streaming

    # st.write("Source Documents Metadata:", DocumentService.get_answer(question, tenant_id)['source_documents'])

# Function to clear memory
def clear_memory(tenant_id):
    DocumentService.clear_memory(tenant_id)
    st.success("Memory cleared successfully")

# Streamlit UI
# st.title("Document Service")

st.header("Load Document")
document_id = st.text_input("Document ID")
url = st.text_input("Document URL")
tenant_id_load = st.text_input("Tenant ID", key="tenant_id_load")
if st.button("Load Document"):
    load_document(document_id, url, tenant_id_load)

st.header("Ask Question")

# Initialize session state for ask_question
if 'ask_question' not in st.session_state:
    st.session_state['ask_question'] = False

# Text input for question with an enter key press detection
def on_question_change():
    st.session_state['ask_question'] = True

tenant_id_ask = st.text_input("Tenant ID", key="tenant_id_ask")
question = st.text_input("Question", key="question_input", on_change=on_question_change)

# If the button is pressed or the enter key is pressed (detected through on_change)
ask_question_button = st.button("Ask Question")
if ask_question_button or st.session_state['ask_question']:
    ask_question(question, tenant_id_ask)
    st.session_state['ask_question'] = False  # Reset the flag

# Tenant ID input for clearing memory
tenant_id_clear = st.text_input("Tenant ID", key="tenant_id_clear")
if st.button("Clear Memory"):
    clear_memory(tenant_id_clear)
