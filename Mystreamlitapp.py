#!/usr/bin/env python
# coding: utf-8

# # HugChat with Metaphor Integration
# 
# ## Overview
# 
# This is a Streamlit app that combines the power of [HugChat](https://github.com/huggingface/hugchat) and [Metaphor](https://metaphor.systems/) to create an AI-powered chatbot with internet access. It allows you to have interactive conversations with the chatbot, fetch internet information using Metaphor, and receive informative responses.
# 
# ## Features
# 
# - Chat with an AI-powered chatbot.
# - Access Metaphor to fetch internet search results.
# - Customizable prompts and responses.
# - Clear chat history.
# - Integration with Hugging Face for language model support.
# 
# ## Prerequisites
# 
# Before running the app, make sure you have the following:
# 
# - Python 3.6 or higher
# - Streamlit
# - HugChat
# - Metaphor API key

# In[6]:


import streamlit as st
from hugchat import hugchat
from hugchat.login import Login
from metaphor_python import Metaphor


# In[7]:


# App title
st.set_page_config(page_title="Pluto")


# In[9]:


# Define Metaphor API key
METAPHOR_API_KEY = "cfb854d0-617b-4e1f-8d54-62e5639995a5"  # Replace with your Metaphor API key

# Define chatbot name
chatbot_name = "Pluto"


with st.sidebar:
    st.title('🤗💬 Pluto')
    if ('EMAIL' in st.secrets) and ('PASS' in st.secrets):
        st.success('HuggingFace Login credentials already provided!', icon='✅')
        hf_email = st.secrets['EMAIL']
        hf_pass = st.secrets['PASS']
    else:
        hf_email = st.text_input('Enter E-mail:', type='password')
        hf_pass = st.text_input('Enter password:', type='password')
        if not (hf_email and hf_pass):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')


# In[13]:


# Create Metaphor client
metaphor = Metaphor(METAPHOR_API_KEY)


# In[ ]:


# Store LLM generated responses
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hey, This is Pluto. Its your chatbot this side, how may i assist ?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hey, This is Pluto. Its your chatbot this side, how may i assist?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLM response
def generate_response(prompt_input, email, passwd):
    # Hugging Face Login
    sign = Login(email, passwd)
    cookies = sign.login()

    # Create ChatBot
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

    # Check if the user's input is a specific question
    if prompt_input.strip().lower() in ["who are you?", "who made you?"]:
        response = "I am an AI LLama Hugchat of Huggingface  which is integrated with Metaphor in the backend."
    else:
        # Fetch Metaphor search results
        search_options = {
            "query": prompt_input,
            "num_results": 5  # You can adjust the number of results as needed
        }
        try:
            search_response = metaphor.search(**search_options)

            # Extract links and summaries from the Metaphor search results
            links_and_summaries = [
                f"Title: {result.title}\nURL: {result.url}\nSummary: {result.extract}\n---"
                for result in search_response.results
            ]

            # Combine the user's query and Metaphor output with the previous conversation
            string_dialogue = "You are a helpful assistant."
            for dict_message in st.session_state.messages:
                if dict_message["role"] == "user":
                    string_dialogue += "User: " + dict_message["content"] + "\n\n"
                else:
                    string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"

            prompt = f"{string_dialogue}\n{prompt_input}\n{''.join(links_and_summaries)}\n Assistant: "
            response = chatbot.chat(prompt)
        except Exception as e:
            response = str(e)

    return response
# User-provided prompt
if prompt := st.chat_input(disabled=not (hf_email and hf_pass)):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate a new response if the last message is not from the assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_response(prompt, hf_email, hf_pass)
                st.write(response)

        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)

