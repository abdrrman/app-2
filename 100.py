
import os
import streamlit as st
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)
from langchain.document_loaders import *
from langchain.chains.summarize import load_summarize_chain
import tempfile
from langchain.docstore.document import Document
import time
from langchain.memory import ConversationBufferMemory
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

openai_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    placeholder="sk-...",
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password",
)

st.title('Celebrity Parody')
#Get the name of the famous celebrity from the user
celebrity_name = st.text_input("Enter the name of the famous celebrity")
#Generate a chat response as the celebrity
def generate_chat_response(celebrity_name):
    prompt = PromptTemplate(
        input_variables=['chat_history', 'celebrity_name'], template='''You are a chatbot imitating {celebrity_name}. Generate a response as if you were the celebrity.

{chat_history}
User: {user_input}
{celebrity_name}:'''
    )
    memory = ConversationBufferMemory(memory_key="chat_history", input_key="celebrity_name")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", openai_api_key=openai_api_key, temperature=0.7)
    chat_llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=False,
        memory=memory,
    )
    return chat_llm_chain
    

if not openai_api_key.startswith('sk-'):
    st.warning('Please enter your OpenAI API key!', icon='⚠')
    celebrity_response = ""
elif celebrity_name:
    if 'chat_llm_chain' not in st.session_state:
        st.session_state.chat_llm_chain = generate_chat_response(celebrity_name)
    celebrity_response = st.session_state.chat_llm_chain.run(celebrity_name=celebrity_name)
else:
    celebrity_response = ""
#Display the chat response to the user with a chat interface
with st.chat_message("assistant"):
    message_placeholder = st.empty()
    full_response = ""
    # Simulate stream of response with milliseconds delay
    for chunk in celebrity_response.split():
        full_response += chunk + " "
        time.sleep(0.05)
        # Add a blinking cursor to simulate typing
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})
