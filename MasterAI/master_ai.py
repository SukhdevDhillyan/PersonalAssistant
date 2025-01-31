import os
import openai
import sqlite3
import time

#########################
# 1. Database Utilities #
#########################

DB_NAME = "master_ai.db"

def init_db():
    """
    Creates the conversation_logs table if it doesn't exist.
    For a production system, you might want more tables (user_profiles, etc.).
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS conversation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        sender TEXT,         -- "user" or "system"
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def insert_message(user_id, sender, message):
    """
    Inserts a single conversation turn into the conversation_logs table.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO conversation_logs (user_id, sender, message)
    VALUES (?, ?, ?)
    """, (user_id, sender, message))
    conn.commit()
    conn.close()

def fetch_recent_messages(user_id, limit=5):
    """
    Fetches the most recent 'limit' messages for a given user_id.
    Returns them in chronological order (oldest first).
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    SELECT sender, message
    FROM conversation_logs
    WHERE user_id = ?
    ORDER BY id DESC
    LIMIT ?
    """, (user_id, limit))
    rows = cur.fetchall()
    conn.close()

    # rows is currently in reverse order (most recent first),
    # so reverse it to get chronological order
    return rows[::-1]


#############################
# 2. LLM (OpenAI) Utilities #
#############################

# Read your OpenAI API key from env variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_llm_response(prompt):
    """
    Calls OpenAI's text completion (GPT-3.5/GPT-4) or chat endpoint
    to generate a response.
    
    Note: This example uses ChatCompletion with GPT-3.5.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,  # We'll pass a list of role-content dicts
            max_tokens=150,
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return "Sorry, I had an error generating a response."


###################
# 3. Master AI    #
###################

class MasterAI:
    """
    The "Master AI" orchestrates:
      - Taking user input
      - Maintaining short-term context (recent conversation)
      - Calling the LLM
      - Storing conversation logs
    """
    def __init__(self, user_id):
        self.user_id = user_id

    def handle_user_message(self, user_message):
        """
        1. Insert user's message into DB
        2. Retrieve short-term context
        3. Build a prompt for the LLM
        4. Get LLM response
        5. Insert the LLM response into DB
        6. Return the LLM response
        """
        # 1. Insert user message
        insert_message(self.user_id, "user", user_message)

        # 2. Fetch recent messages (including this one)
        recent_msgs = fetch_recent_messages(self.user_id, limit=5)

        # 3. Build an LLM-compatible prompt structure
        # The ChatCompletion endpoint expects a list of dicts with "role" and "content".
        # We'll map "user" and "system" from our logs accordingly.
        messages_for_llm = []
        for sender, msg in recent_msgs:
            role = "user" if sender == "user" else "assistant"
            messages_for_llm.append({"role": role, "content": msg})

        # 4. Call the LLM
        llm_reply = get_llm_response(messages_for_llm)

        # 5. Insert system (AI) response in DB
        insert_message(self.user_id, "system", llm_reply)

        # 6. Return the AI response
        return llm_reply


###################
# 4. Main Program #
###################

def main():
    # Initialize the database
    init_db()

    # Create an instance of MasterAI for a specific user (e.g. "demo_user")
    user_id = "demo_user"
    master_ai = MasterAI(user_id)

    print("Welcome to the Minimal Master AI!\nType 'quit' or 'exit' to stop.")

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break

        # Pass user message to MasterAI
        ai_response = master_ai.handle_user_message(user_input)
        print("AI:", ai_response)


if __name__ == "__main__":
    main()
