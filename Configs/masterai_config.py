# configs/masterai_config.py
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
MODEL_NAME = "gpt-3.5-turbo"
MAX_TOKENS = 150
TEMPERATURE = 0.7
