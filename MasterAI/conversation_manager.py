# MasterAI/conversation_manager.py
from SmartStorage.db_manager import DBManager

class ConversationManager:
    """Manages short-term chat memory."""

    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager

    def store_message(self, prompt_payload):
        self.db_manager.insert_conversation_log(prompt_payload["conversation_id"], prompt_payload["message_id"], prompt_payload["user_id"], prompt_payload["user_name"], prompt_payload["user_prompt"], prompt_payload["bot_reply"])

