from vertexai.generative_models import GenerationConfig
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import ChatSession
from vertexai.generative_models import Part
from src.config.logging import logger 
from src.config.setup import config


with open('./data/templates/system_instructions.txt', 'r') as f:
    system_instruction = f.read()


model = GenerativeModel(config.TEXT_GEN_MODEL_NAME, 
                        system_instruction=[system_instruction])

generation_config = GenerationConfig(temperature=0.0, 
                                     top_p=0.0, 
                                     top_k=1, 
                                     candidate_count=1, 
                                     max_output_tokens=8192,
                                     response_mime_type="application/json")


user_prompt = "What is the meaning of this life?"

chat = model.start_chat(response_validation=False)

response = chat.send_message(user_prompt,
                            generation_config=generation_config)

logger.info(response)