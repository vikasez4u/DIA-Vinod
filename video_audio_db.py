import sqlite3
from datetime import datetime

DATABASE = "video_transcriptions.db"


def connect_db():
    try:
        conn = sqlite3.connect(DATABASE)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def create_table():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_transcriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_filename TEXT NOT NULL,
                transcription_text TEXT NOT NULL,
                create_date TEXT NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()


def insert_transcription(video_filename, transcription_text):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        create_date = datetime.now(datetime.UTC).isoformat()
        cursor.execute("""
            INSERT INTO video_transcriptions (video_filename, transcription_text, create_date)
            VALUES (?, ?, ?)
        """, (video_filename, transcription_text, create_date))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Inserted transcription for {video_filename} into database.")


def fetch_all_transcriptions():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, video_filename, transcription_text, create_date FROM video_transcriptions ORDER BY create_date DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    return []


if __name__ == "__main__":
    create_table()
