# SmartStorage/db_manager.py
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from Configs.masterai_config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

class DBManager:
    """Handles all PostgreSQL database operations."""

    def __init__(self):
        """Initialize and connect to PostgreSQL."""
        self.conn = None
        self.connect()

    def connect(self):
        """Establish a connection to PostgreSQL."""
        try:
            self.conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
        except Exception as e:
            print(f"[ERROR] Failed to connect to PostgreSQL: {e}")


    def execute_queries(self, queries):
        """Execute a batch of queries."""
        if self.conn:
            try:
                with self.conn.cursor() as cur:
                    for query in queries:
                        cur.execute(query)
                self.conn.commit()
            except Exception as e:
                print(f"[ERROR] Database query failed: {e}")
                self.conn.rollback()

    def insert_conversation_log(self, conversation_id, message_id, user_id, user_name, user_prompt, bot_reply):
        """Store a conversation message."""
        query = """
            INSERT INTO conversation_logs (conversation_id, message_id, user_id, user_name, user_prompt, bot_reply)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        self.execute_query(query, (conversation_id, message_id, user_id, user_name, user_prompt, bot_reply))

    def insert_conversation_summary(self, prompt_payload, updated_summary):
        """Store or update conversation summary in the database."""
        query = """
            INSERT INTO conversation_summary (conversation_id, message_id, user_id, summary, timestamp)
            VALUES (%s, %s, %s, %s, NOW())
            ON CONFLICT (conversation_id) DO UPDATE SET summary = EXCLUDED.summary, timestamp = NOW();
        """
        self.execute_query(query, (prompt_payload["conversation_id"], prompt_payload["message_id"], prompt_payload["user_id"], updated_summary))

    def fetch_recent_messages(self, user_id, conversation_id, limit=5):
        """Retrieve the last few messages."""
        query = """
            SELECT sender, message FROM conversation_logs
            WHERE user_id = %s AND conversation_id = %s
            ORDER BY timestamp DESC LIMIT %s;
        """
        return self.fetch_query_results(query, (user_id, conversation_id, limit))

    def execute_query(self, query, params):
        """Execute a single query."""
        if self.conn:
            try:
                with self.conn.cursor() as cur:
                    cur.execute(query, params)
                self.conn.commit()
            except Exception as e:
                print(f"[ERROR] Query execution failed: {e}")
                self.conn.rollback()

    def fetch_query_results(self, query, params):
        """Fetch query results."""
        if self.conn:
            try:
                with self.conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(query, params)
                    return cur.fetchall()
            except Exception as e:
                print(f"[ERROR] Fetch query failed: {e}")
                return None

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("[INFO] Database connection closed.")