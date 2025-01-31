# SmartStorage/db_manager.py

import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from typing import Optional, Dict, Any, List, Tuple

class DBManager:
    """
    A central class to manage all database operations:
      - Connecting to the DB
      - Creating necessary tables
      - Inserting and retrieving conversation logs
      - Fetching and updating user profiles
      - Closing the connection gracefully
    """

    def __init__(self):
        """
        Initializes the DBManager, attempting to connect to the DB
        using environment variables or fallback defaults.
        """
        self.db_name = os.getenv("DB_NAME", "your_db")
        self.db_user = os.getenv("DB_USER", "your_user")
        self.db_password = os.getenv("DB_PASSWORD", "your_password")
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = os.getenv("DB_PORT", "5432")

        self.conn = None
        self.connect()
        self.init_tables()

    def connect(self):
        """
        Establishes a connection to the PostgreSQL database.
        If you need a connection pool or async approach, you can adapt here.
        """
        try:
            self.conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
            # Optionally set autocommit: self.conn.autocommit = True
        except Exception as e:
            print(f"[ERROR] Failed to connect to the database: {e}")
            self.conn = None

    def init_tables(self):
        """
        Creates the necessary tables if they do not exist:
          1) conversation_logs  – short-term conversation data
          2) user_profiles      – long-term user data
        In production, you might prefer a migration tool like Alembic.
        """
        if not self.conn:
            print("[WARNING] init_tables called but no DB connection available.")
            return

        try:
            with self.conn.cursor() as cur:
                # Create conversation_logs
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_logs (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255),
                        sender VARCHAR(50),       -- "user" or "system"
                        message TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # Create user_profiles
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255),
                        age INT,
                        gender VARCHAR(50),
                        profession VARCHAR(255),
                        preferences JSONB,       -- store arbitrary user preferences as JSON
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            self.conn.commit()
        except Exception as e:
            print(f"[ERROR] init_tables failed: {e}")
            self.conn.rollback()

    # -------------------------------------------------------------------------
    # Conversation Log Methods
    # -------------------------------------------------------------------------
    def insert_conversation_log(self, user_id: str, sender: str, message: str):
        """
        Inserts a single message into the conversation_logs table.
        :param user_id: Unique identifier for the user (e.g., "demo_user").
        :param sender: "user" or "system" (the AI).
        :param message: The textual content of the message.
        """
        if not self.conn:
            print("[ERROR] Cannot insert log; no DB connection.")
            return

        try:
            with self.conn.cursor() as cur:
                query = """
                    INSERT INTO conversation_logs (user_id, sender, message)
                    VALUES (%s, %s, %s);
                """
                cur.execute(query, (user_id, sender, message))
            self.conn.commit()
        except Exception as e:
            print(f"[ERROR] insert_conversation_log failed: {e}")
            self.conn.rollback()

    def fetch_recent_messages(self, user_id: str, limit: int = 5) -> List[Tuple[str, str]]:
        """
        Retrieves the last `limit` conversation messages in DESC order (latest first),
        then returns them in ascending order (oldest first).
        
        :param user_id: The user ID whose messages we want.
        :param limit: Number of recent messages to fetch.
        :return: A list of (sender, message) tuples in chronological order.
        """
        if not self.conn:
            print("[ERROR] Cannot fetch messages; no DB connection.")
            return []

        try:
            with self.conn.cursor() as cur:
                query = """
                    SELECT sender, message
                    FROM conversation_logs
                    WHERE user_id = %s
                    ORDER BY id DESC
                    LIMIT %s;
                """
                cur.execute(query, (user_id, limit))
                rows = cur.fetchall()
            # rows are in reverse order, so reverse them to get chronological
            return rows[::-1]
        except Exception as e:
            print(f"[ERROR] fetch_recent_messages failed: {e}")
            return []

    # -------------------------------------------------------------------------
    # User Profile Methods
    # -------------------------------------------------------------------------
    def fetch_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches the user profile for a given user_id.
        :return: A dictionary with user fields (name, age, etc.) or None if not found.
        """
        if not self.conn:
            print("[ERROR] Cannot fetch profile; no DB connection.")
            return None

        try:
            with self.conn.cursor(cursor_factory=DictCursor) as cur:
                query = """
                    SELECT name, age, gender, profession, preferences
                    FROM user_profiles
                    WHERE user_id = %s;
                """
                cur.execute(query, (user_id,))
                row = cur.fetchone()
                if row:
                    return {
                        "name": row["name"],
                        "age": row["age"],
                        "gender": row["gender"],
                        "profession": row["profession"],
                        "preferences": row["preferences"]
                    }
            return None
        except Exception as e:
            print(f"[ERROR] fetch_user_profile failed: {e}")
            return None

    def create_or_update_profile(
        self,
        user_id: str,
        name: str,
        age: int,
        gender: str,
        profession: str,
        preferences: Dict[str, Any]
    ) -> None:
        """
        Insert a new profile or update an existing one based on user_id.
        Uses PostgreSQL's 'ON CONFLICT' for upsert logic.
        """
        if not self.conn:
            print("[ERROR] Cannot create/update profile; no DB connection.")
            return

        try:
            with self.conn.cursor() as cur:
                query = """
                    INSERT INTO user_profiles (user_id, name, age, gender, profession, preferences)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        age = EXCLUDED.age,
                        gender = EXCLUDED.gender,
                        profession = EXCLUDED.profession,
                        preferences = EXCLUDED.preferences,
                        updated_at = CURRENT_TIMESTAMP;
                """
                cur.execute(query, (user_id, name, age, gender, profession, preferences))
            self.conn.commit()
        except Exception as e:
            print(f"[ERROR] create_or_update_profile failed: {e}")
            self.conn.rollback()

    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    def close(self):
        """
        Closes the database connection.
        In a larger system with connection pooling, you'd release the pool here instead.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            print("[INFO] Database connection closed.")
