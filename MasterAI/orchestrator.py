# MasterAI/orchestrator.py
from MasterAI.conversation_manager import ConversationManager
from MasterAI.llm_manager import LLMManager
from SmartStorage.db_manager import DBManager
from SmartStorage.redis_queue import RedisQueue
from SentimentAnalyser.sentimentAnalyser import SentimentAnalyser
import uuid 
import asyncio

class MasterAIOrchestrator:
    """Orchestrates AI logic by managing conversations and calling the LLM."""

    def __init__(self, user_id):
        self.user_id = user_id
        self.db_manager = DBManager()
        self.conv_manager = ConversationManager(self.db_manager)
        self.llm_manager = LLMManager()  # Uses Ollama now
        self.redis_queue = RedisQueue()
        self.sentiment_analyser = SentimentAnalyser()

    def handle_user_message(self, prompt_payload):
        """Handles user input, stores messages, and generates AI responses."""

        conversation_summary = self.redis_queue.get_conversation_summary(prompt_payload["conversation_id"])
        print("conversation_summary", conversation_summary)

        # Construct prompt for LLM
        prompt = []
        
        human_like_prompt = f"You are a friendly, empathetic human assistant. You speak in a warm, casual tone, use contractions, and ask clarifying questions. You continue this conversation with short to medium-length sentences that flow naturally, almost like spoken language. You do not sound like a robot.\nConversation: "
        if conversation_summary:
            prompt.append({"role": "system", "content": f"Here is the conversation so far: {conversation_summary}"})
            print("Conversation Summary till now...\n:", conversation_summary)
            human_like_prompt = human_like_prompt + f"\nPrevious Conversation Summary: {conversation_summary}\n"
        human_like_prompt = human_like_prompt + "\nUser: " + prompt_payload['user_prompt'] + "\nAssistant: "

        prompt.append({"role": "user", "content": human_like_prompt})

        print("prompt sent to LLM: ", human_like_prompt)
        ai_reply = self.llm_manager.generate_response(prompt)
        ai_reply = ai_reply.split('</think>')[-1].strip()
        print("Reply from LLM: ", ai_reply)

        prompt_payload["bot_reply"] = ai_reply
        # Fire async task to generate summary
        asyncio.run(self.generate_conversation_summary_and_update_database(prompt_payload, conversation_summary))

        # Store system message
        self.conv_manager.store_message(prompt_payload)
    
    async def generate_conversation_summary_and_update_database(self, prompt_payload, previous_summary):
        """Generate conversation summary asynchronously using only previous summary & new message."""
        
        if not previous_summary:
            prompt = f"""You are a summarization assistant. Your task is to update the summary of below conversation.

                     Conversation: 
                        User: {prompt_payload["user_prompt"]}"
                        AI: {prompt_payload["bot_reply"]}"
                     
                    Provide a concise, updated summary of the entire conversation."""
        else:
            prompt = f"""You are a summarization assistant. Your task is to update the summary of below conversation.

                     Previous Summary: {previous_summary}
                     New Exchange: 
                        User: {prompt_payload["user_prompt"]}
                        AI: {prompt_payload["bot_reply"]}
                     
                    Provide a concise, updated summary of the entire conversation."""

        # Call LLM asynchronously to generate the updated summary
        print("\nprompt sent to summary: ", prompt, "\n")
        updated_summary = await asyncio.to_thread(self.llm_manager.generate_response, [{"role": "system", "content": prompt}])
        updated_summary = updated_summary.split("</think>")[-1].strip()

        print("\nupdated summary: ", updated_summary.split("</think>")[-1].strip(), "\n")
        
        # Update Redis & Database asynchronously
        self.redis_queue.set_conversation_summary(prompt_payload["conversation_id"], updated_summary)

        self.db_manager.insert_conversation_summary(prompt_payload, updated_summary)