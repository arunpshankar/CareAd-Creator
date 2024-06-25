from src.playground.utils import read_api_key
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
from datetime import datetime
import streamlit as st
import joblib
import time
import os

# Path to the API key YAML file
API_KEY_FILE_PATH = './credentials/api_key.yml'

api_key = read_api_key(API_KEY_FILE_PATH)



safety_settings={
        
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH
    }



  
genai.configure(api_key=api_key)


current_time = datetime.now()

# Format the datetime in the desired format
new_chat_id = current_time.strftime('%d-%m-%Y-%H-%M-%S')

MODEL_ROLE = 'ai'
AI_AVATAR_ICON = '✨'

# Create a data/ folder if it doesn't already exist
try:
    os.mkdir('data/')
except:
    pass

# Load past chats (if available)
try:
    past_chats: dict = joblib.load('data/past_chats_list')
except:
    past_chats = {}

# Sidebar allows a list of past chats
with st.sidebar:

    st.write('# Past Chats')
    #print(st.session_state)
    if st.session_state.get('chat_id') is None:
        options = [new_chat_id] + list(past_chats.keys())
        print('Yes', options)
        st.session_state.chat_id = st.selectbox(
            label='Pick a past chat',
            options=options,
            format_func=lambda x: past_chats.get(x, 'New Chat'),
            placeholder='_',
        )
    else:
        print('else')
        # This will happen the first time AI response comes in
        print(list(past_chats.keys()))
        print([new_chat_id, st.session_state.chat_id])
        options = [new_chat_id, st.session_state.chat_id] + list(past_chats.keys())
        if len(options) > 2:
            options = options[0:-1]

        
        st.session_state.chat_id = st.selectbox(
            label='Pick a past chat',
            options=options,
            index=1,
            format_func=lambda x: past_chats.get(x, 'New Chat' if x != st.session_state.chat_id else st.session_state.chat_title),
            placeholder='_',
        )
    # Save new chats after a message has been sent to AI
    # TODO: Give user a chance to name chat
    st.session_state.chat_title = f'session-{st.session_state.chat_id}'
    #print(st.session_state)


st.write('# Chat with Gemini ✨ ')

# Chat history (allows to ask multiple questions)
try:
    st.session_state.messages = joblib.load(
        f'data/{st.session_state.chat_id}-st_messages'
    )
    st.session_state.gemini_history = joblib.load(
        f'data/{st.session_state.chat_id}-gemini_messages'
    )
    # print('old cache')
except:
    st.session_state.messages = []
    st.session_state.gemini_history = []
    # print('new_cache made')

st.session_state.model = genai.GenerativeModel('gemini-pro')
st.session_state.chat = st.session_state.model.start_chat(
    history=st.session_state.gemini_history,
)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(
        name=message['role'],
        avatar=message.get('avatar'),
    ):
        st.markdown(message['content'])

# React to user input
if prompt := st.chat_input('Your message here...'):
    # Save this as a chat for later
    if st.session_state.chat_id not in past_chats.keys():
        past_chats[st.session_state.chat_id] = st.session_state.chat_title
        joblib.dump(past_chats, 'data/past_chats_list')
    # Display user message in chat message container
    with st.chat_message('user'):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append(dict(role='user', content=prompt))
    # Send message to AI

    response = st.session_state.chat.send_message(prompt, safety_settings=safety_settings, stream=True)

    # Display assistant response in chat message container
    with st.chat_message(name=MODEL_ROLE, avatar=AI_AVATAR_ICON):
        message_placeholder = st.empty()
        full_response = ''
        # Streams in a chunk at a time
        for chunk in response:
            print(chunk)
            # Simulate stream of chunk
            # TODO: Chunk missing `text` if API stops mid-stream ("safety"?)
            for piece in chunk.text.split(' '):
                full_response += piece + ' '
                time.sleep(0.05)
                # Rewrites with a cursor at end
                message_placeholder.write(full_response + '▌')
    
        # Write full message with placeholder
        message_placeholder.write(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        dict(
            role=MODEL_ROLE,
            content=st.session_state.chat.history[-1].parts[0].text,
            avatar=AI_AVATAR_ICON,
        )
    )
    st.session_state.gemini_history = st.session_state.chat.history

    # Save to file
    joblib.dump(st.session_state.messages, f'data/{st.session_state.chat_id}-st_messages')

    joblib.dump(st.session_state.gemini_history, f'data/{st.session_state.chat_id}-gemini_messages')