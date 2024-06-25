from vertexai.generative_models import HarmBlockThreshold
from vertexai.generative_models import GenerationConfig
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import HarmCategory
from vertexai.generative_models import ChatSession
from vertexai.generative_models import Part
from src.config.logging import logger 
from src.config.setup import config
import json 
import os 



with open('./../../data/templates/system_instructions.txt', 'r') as f:
    instructions = f.read()
    
system_instruction = [instructions]




model = GenerativeModel(config.TEXT_GEN_MODEL_NAME, 
                        system_instruction=[system_instruction])


chat = gemini_model.start_chat(response_validation=False)