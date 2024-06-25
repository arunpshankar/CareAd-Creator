from src.playground.utils import read_api_key
from src.config.logging import logger 
import google.generativeai as genai
from datetime import datetime
import streamlit as st
import jsonlines 
import joblib
import time
import os

# Path to the API key YAML file
API_KEY_FILE_PATH = './credentials/api_key.yml'

api_key = read_api_key(API_KEY_FILE_PATH)


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

# Load past chats --- jsonl 
try:
    # Open the JSONL file and read it into a dictionary
    with jsonlines.open('./data/history/past_chats.jsonl') as reader:
        past_chats = {entry['chat_id']: entry for entry in reader}
except FileNotFoundError:
    # If the file does not exist, initialize an empty dictionary
    past_chats = {}



# Sidebar allows a list of past chats
with st.sidebar:
    st.write('## Past Chat Sessions')
    logger.info(f'Session state: {st.session_state}')
    if st.session_state.get('chat_id') is None:
        chat_id_options = [new_chat_id] + list(past_chats.keys())
        st.session_state.chat_id = st.selectbox(label='Choose a session', 
                                                options=chat_id_options,
                                                format_func=lambda x: past_chats.get(x, 'Start a new session'), 
                                                placeholder='_')
    else:
        # condition only  when 1st time AI response comes in 
        chat_id_options = [new_chat_id, st.session_state.chat_id] + list(past_chats.keys())
        st.session_state.chat_id = st.selectbox(label='Choose a session', 
                                                options=chat_id_options, 
                                                index=1, 
                                                format_func=lambda x: past_chats.get(x, 'Start a new session' if x != st.session_state.chat_id else st.session_state.chat_title),
            placeholder='_',
        )
    # Save new chats after a message has been sent to AI
    st.session_state.chat_title = f'chat-{st.session_state.chat_id}'
    logger.info(f'Session state: {st.session_state}')

st.write('# Chat with Gemini ✨ ')




# Path to the chat history files
chat_messages_file = f'data/{st.session_state.chat_id}-st_messages.jsonl'
gemini_messages_file = f'data/{st.session_state.chat_id}-gemini_messages.jsonl'

# Load or initialize chat history
if os.path.exists(chat_messages_file):
    with jsonlines.open(chat_messages_file) as reader:
        st.session_state.messages = list(reader)
    # print('old cache')
else:
    st.session_state.messages = []
    # print('new_cache made')

# Load or initialize Gemini messages history
if os.path.exists(gemini_messages_file):
    with jsonlines.open(gemini_messages_file) as reader:
        st.session_state.gemini_history = list(reader)
    # print('old cache')
else:
    st.session_state.gemini_history = []
    # print('new_cache made')

st.session_state.model = genai.GenerativeModel('gemini-pro')
st.session_state.chat = st.session_state.model.start_chat(
    history=st.session_state.gemini_history,
)


print('>>>>>', st.session_state)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    
    message = eval(message)
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
    st.session_state.messages.append(
        dict(
            role='user',
            content=prompt,
        )
    )
    # Send message to AI
    try:
        response = st.session_state.chat.send_message(
            prompt,
            stream=True,
        )
    except Exception as e:
        print(e)
    # Display assistant response in chat message container
    with st.chat_message(
        name=MODEL_ROLE,
        avatar=AI_AVATAR_ICON,
    ):
        message_placeholder = st.empty()
        full_response = ''
        assistant_response = response
        # Streams in a chunk at a time
        for chunk in response:
            # Simulate stream of chunk
            # TODO: Chunk missing `text` if API stops mid-stream ("safety"?)
            for ch in chunk.text.split(' '):
                full_response += ch + ' '
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

    # Convert each object in the lists to its string representation
    messages_to_save = [str(message) for message in st.session_state.messages]
    gemini_history_to_save = [str(history) for history in st.session_state.gemini_history]

    # Save the string representations to jsonlines files
    with jsonlines.open(f'data/{st.session_state.chat_id}-st_messages.jsonl', mode='w') as writer:
        for message in messages_to_save:
            writer.write(message)

    with jsonlines.open(f'data/{st.session_state.chat_id}-gemini_messages.jsonl', mode='w') as writer:
        for history in gemini_history_to_save:
            writer.write(history)