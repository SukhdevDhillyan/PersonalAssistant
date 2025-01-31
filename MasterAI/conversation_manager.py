# MasterAI/conversation_manager.py

from SmartStorage.db_manager import DBManager

class ConversationManager:
    """
    Manages short-term conversation logs.
    """
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
    
    def store_user_message(self, user_id: str, message: str):
        self.db_manager.insert_conversation_log(user_id, sender="user", message=message)
    
    def store_system_message(self, user_id: str, message: str):
        self.db_manager.insert_conversation_log(user_id, sender="system", message=message)
    
    def get_recent_messages(self, user_id: str, limit: int = 5):
        return self.db_manager.fetch_recent_messages(user_id, limit=limit)
