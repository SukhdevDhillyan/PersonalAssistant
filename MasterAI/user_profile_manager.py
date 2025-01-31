# MasterAI/user_profile_manager.py

from SmartStorage.db_manager import DBManager
from typing import Optional, Dict, Any

class UserProfileManager:
    """
    Manages user profile data (long-term context).
    """
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.db_manager.fetch_user_profile(user_id)
    
    def update_user_profile(
        self,
        user_id: str,
        name: str,
        age: int,
        gender: str,
        profession: str,
        preferences: Dict[str, Any]
    ) -> None:
        self.db_manager.create_or_update_profile(
            user_id,
            name,
            age,
            gender,
            profession,
            preferences
        )
