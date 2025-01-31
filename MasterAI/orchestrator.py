# MasterAI/orchestrator.py

from SmartStorage.db_manager import DBManager
from .conversation_manager import ConversationManager
from .user_profile_manager import UserProfileManager
from .llm_manager import LLMManager

class MasterAIOrchestrator:
    def __init__(self, user_id: str, max_context: int = 5):
        self.user_id = user_id
        self.max_context = max_context
        
        # Create or inject a DB manager
        self.db_manager = DBManager()
        
        # Sub-managers
        self.conv_manager = ConversationManager(self.db_manager)
        self.profile_manager = UserProfileManager(self.db_manager)
        self.llm_manager = LLMManager()
    
    def handle_user_message(self, user_message: str) -> str:
        """
        1. Store user's message
        2. Get recent conversation
        3. (Optional) get user profile
        4. Build LLM prompt
        5. Call LLM
        6. Store LLM response
        7. Return response
        """
        # 1. Store user message
        self.conv_manager.store_user_message(self.user_id, user_message)
        
        # 2. Fetch recent messages
        recent_msgs = self.conv_manager.get_recent_messages(self.user_id, limit=self.max_context)
        
        # 3. (Optional) get user profile
        user_profile = self.profile_manager.get_user_profile(self.user_id)
        
        # 4. Construct system prompt
        system_prompt = self._build_system_prompt(user_profile)
        messages = [{"role": "system", "content": system_prompt}]
        
        # Convert conversation logs into LLM-friendly format
        for (sender, text) in recent_msgs:
            role = "user" if sender == "user" else "assistant"
            messages.append({"role": role, "content": text})
        
        # Add the new user message at the end
        messages.append({"role": "user", "content": user_message})
        
        # 5. Call the LLM
        ai_reply = self.llm_manager.generate_response(messages)
        
        # 6. Store system (AI) message
        self.conv_manager.store_system_message(self.user_id, ai_reply)
        
        # 7. Return
        return ai_reply
    
    def _build_system_prompt(self, user_profile) -> str:
        base = "You are a helpful assistant. Use the user's context to provide concise and friendly responses."
        if user_profile:
            name = user_profile.get("name", "User")
            base += f" The user's name is {name}."
        return base
    
    def update_user_profile(self, name, age, gender, profession, preferences):
        """Example method to update or create a user profile."""
        self.profile_manager.update_user_profile(self.user_id, name, age, gender, profession, preferences)
    
    def close(self):
        """Close DB connection if needed."""
        self.db_manager.close()
