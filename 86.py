
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
#Get the name of a famous celebrity from the user
celebrity_name = st.text_input("Enter the name of a famous celebrity")
#Generate a hilarious parody script for the user to chat with the celebrity
def parodyScriptGenerator(celebrity_name):
    chat = ChatOpenAI(
        model="gpt-3.5-turbo-16k",
        openai_api_key=openai_api_key,
        temperature=0.7
    )
    system_template = """You are a comedy writer tasked with creating a hilarious parody script for the user to chat with {celebrity_name}."""
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_template = """Please generate a funny and entertaining script for the user to chat with {celebrity_name}."""
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result = chain.run(celebrity_name=celebrity_name)
    return result # returns string   


if not openai_api_key.startswith('sk-'):
    st.warning('Please enter your OpenAI API key!', icon='⚠')
    parody_script = ""
elif celebrity_name:
    parody_script = parodyScriptGenerator(celebrity_name)
else:
    parody_script = ""
#Display the parody script to the user
if parody_script:
    st.code(parody_script)
#Enable the user to have a chat-based conversation with the celebrity using the parody script
def celebrity_chat(parody_script):
    prompt = PromptTemplate(
        input_variables=['chat_history', 'parody_script'], template='''You are a chatbot simulating a conversation with a celebrity. Use the given parody script to respond to the user's messages.

Parody Script:
{parody_script}

{chat_history}
User: {user_input}
Celebrity:'''
    )
    memory = ConversationBufferMemory(memory_key="chat_history", input_key="parody_script")
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
    conversation = ""
elif parody_script:
    if 'chat_llm_chain' not in st.session_state:
        st.session_state.chat_llm_chain = celebrity_chat(parody_script)
    conversation = st.session_state.chat_llm_chain.run(parody_script=parody_script)
else:
    conversation = ""
#Display the conversation history to the user
with st.chat_message("assistant"):
    message_placeholder = st.empty()
    full_response = ""
    # Simulate stream of response with milliseconds delay
    for chunk in conversation.split():
        full_response += chunk + " "
        time.sleep(0.05)
        # Add a blinking cursor to simulate typing
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})
