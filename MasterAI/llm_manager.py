# MasterAI/llm_manager.py
import ollama

class LLMManager:
    """Handles calls to Ollama LLM API."""

    def __init__(self, model_name="deepseek-r1:1.5b"):
        self.model_name = model_name  # Ollama model to use

    def generate_response(self, messages):
        """
        Calls Ollama LLM with chat messages.
        :param messages: List of dicts containing chat history (role, content).
        :return: AI-generated response.
        """
        try:
            response = ollama.chat(model=self.model_name, messages=messages)
            return response['message']['content']
        except Exception as e:
            print(f"[ERROR] Ollama API call failed: {e}")
            return "I'm sorry, something went wrong with the AI service."
