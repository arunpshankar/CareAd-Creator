from google.generativeai.types import HarmBlockThreshold
from google.generativeai.types import HarmCategory
from src.playground.utils import read_api_key
from src.config.logging import logger
import google.generativeai as genai
from datetime import datetime
import streamlit as st
import joblib
import time


API_KEY_FILE_PATH = './credentials/api_key.yml'
api_key = read_api_key(API_KEY_FILE_PATH)
genai.configure(api_key=api_key)

current_time = datetime.now()
new_chat_id = current_time.strftime('%d-%m-%Y-%H-%M-%S')

MODEL_ROLE = 'ai'
AI_AVATAR_ICON = '✨'

# Load past chats (if available)
try:
    past_chats: dict = joblib.load('data/history/past_chats')
except:
    past_chats = {}

# If past_chats loaded from file, update session state
if 'past_chats' not in st.session_state:
    st.session_state.past_chats = past_chats

if 'chat_id' not in st.session_state:
    st.session_state.chat_id = None

# Initialize chat_title if not present in the session state
if 'chat_title' not in st.session_state:
    st.session_state.chat_title = "New Session"

# Sidebar allows a list of past chats
with st.sidebar:

    st.write('# Past chat sessions')
    if st.session_state.get('chat_id') is None:
        #options = [new_chat_id] + list(past_chats.keys())
        options = [new_chat_id] + list(st.session_state.past_chats.keys())
        options = list(dict.fromkeys(options))  # Removes duplicates
        st.session_state.chat_id = st.selectbox(
            label='Choose a session',
            options=options,
            format_func=lambda x: past_chats.get(x, 'Start a new session'),
            placeholder='_',
        )
    else:
        options = [new_chat_id, st.session_state.chat_id] + list(past_chats.keys())
        options = list(dict.fromkeys(options))  # Removes duplicates

        st.session_state.chat_id = st.selectbox(
            label='Choose a session',
            options=options,
            index=1,
            format_func=lambda x: past_chats.get(x, 'Start a new session' if x != st.session_state.chat_id else st.session_state.chat_title),
            placeholder='_',
        )
    st.session_state.chat_title = f'session-{st.session_state.chat_id}'

st.write('# CareAd Creator - Powered by Gemini ✨ ')

# Chat history
try:
    st.session_state.messages = joblib.load(
        f'data/history/{st.session_state.chat_id}-st_messages'
    )
    st.session_state.gemini_history = joblib.load(
        f'data/history/{st.session_state.chat_id}-gemini_messages'
    )
except:
    st.session_state.messages = []
    st.session_state.gemini_history = []


with open('data/templates/system_instruction.txt', 'r') as f:
    instructions = f.read()
st.session_state.model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=instructions)
st.session_state.chat = st.session_state.model.start_chat(
    history=st.session_state.gemini_history,
)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(name=message['role'], avatar=message.get('avatar')):
        st.markdown(message['content'])

# React to user input
if prompt := st.chat_input('Your message here...'):
    # Save this as a chat for later
    if st.session_state.chat_id not in past_chats.keys():
        past_chats[st.session_state.chat_id] = st.session_state.chat_title
        joblib.dump(past_chats, 'data/history/past_chats')
    # Display user message in chat message container
    with st.chat_message('user'):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append(dict(role='user', content=prompt))
    # Send message to AI

    safety_settings = { 
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
    }

    response = st.session_state.chat.send_message(prompt, safety_settings=safety_settings, stream=True)

    # Display assistant response in chat message container
    try:
        with st.chat_message(name=MODEL_ROLE, avatar=AI_AVATAR_ICON):
            message_placeholder = st.empty()
            full_response = ''
            # Streams in a chunk at a time
            for chunk in response:
                # Simulate stream of chunk
                for piece in chunk.text.split(' '):
                    full_response += piece + ' '
                    time.sleep(0.05)
                    # Rewrites with a cursor at end
                    message_placeholder.write(full_response + '▌')
        
            # Write full message with placeholder
            message_placeholder.write(full_response)
    except Exception as e:
        logger.error(e)

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
    joblib.dump(st.session_state.messages, f'data/history/{st.session_state.chat_id}-st_messages')
    joblib.dump(st.session_state.gemini_history, f'data/history/{st.session_state.chat_id}-gemini_messages')