import redis
import json
from Configs.masterai_config import REDIS_HOST, REDIS_PORT, REDIS_DB

class RedisQueue:
    """Handles Redis-based caching of active conversations."""

    def __init__(self):
        self.redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

    def set_conversation_summary(self, conversation_id, summary):
        """Store the conversation summary in Redis."""
        self.redis_client.set(conversation_id, summary)

    def get_conversation_summary(self, conversation_id):
        """Retrieve the conversation summary from Redis."""
        return self.redis_client.get(conversation_id)

    def clear_conversation(self, conversation_id):
        """Clear cached messages & summary for a conversation."""
        self.redis_client.delete(conversation_id)
