# main.py
from MasterAI.orchestrator import MasterAIOrchestrator
import uuid

user_id = "demo_user"
master_ai = MasterAIOrchestrator(user_id)

message_cnt = 0
conversation_id = str(uuid.uuid4())

while True:
    user_input = input("User: ")
    message_cnt = message_cnt + 1
    
    prompt_payload = {
        "conversation_id": conversation_id,
        "message_id": message_cnt,
        "user_id": "1",
        "user_name": "sukhu",
        "user_prompt": user_input
    }

    if user_input.lower() == "exit":
        break
    master_ai.handle_user_message(prompt_payload)
