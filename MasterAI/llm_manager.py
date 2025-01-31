# MasterAI/llm_manager.py

import openai
from configs import OPENAI_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE

class LLMManager:
    """
    Encapsulates interaction with the LLM (OpenAI or another model).
    """
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
    
    def generate_response(self, messages, model=MODEL_NAME,
                          max_tokens=MAX_TOKENS,
                          temperature=TEMPERATURE) -> str:
        """
        messages: list of dicts, e.g.:
          [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
          ]
        """
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[ERROR] LLM call failed: {e}")
            return "I'm sorry, something went wrong with the AI service."
