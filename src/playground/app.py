from src.playground.utils import read_api_key
import google.generativeai as genai
from datetime import datetime
import streamlit as st
import joblib
import time
import os

# Path to the API key YAML file
API_KEY_FILE_PATH = './credentials/api_key.yml'

api_key = read_api_key(API_KEY_FILE_PATH)


genai.configure(api_key=api_key)

current_time = datetime.now()

# Format the datetime in the desired format
new_chat_id = current_time.strftime('%d %m %Y %H %M %S')

MODEL_ROLE = 'ai'
AI_AVATAR_ICON = '✨'

# Create a data/ folder if it doesn't already exist
try:
    os.mkdir('data/')
except:
    pass

# Load past chats --- jsonl 
try:
    past_chats: dict = joblib.load('./data/history/past_chats.jsonl')
except:
    past_chats = {}



