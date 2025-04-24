# Add the 'lib' directory to the Python path
import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from datetime import datetime
from lib.utils import get_parent_path

# Get database and file paths from environment variables or use defaults
DB_FILE = os.getenv('DB_FILE', get_parent_path('words.db'))
NEW_WORDS_FILE = os.getenv('NEW_WORDS_FILE', get_parent_path('new_words.txt'))
MOST_FREQUENT_WORDS_FILE = os.getenv('MOST_FREQUENT_WORDS_FILE', get_parent_path('most_frequent_words.txt'))

# Function to initialize the database
def init_db():
    # Connect to SQLite database
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create words table
    c.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL UNIQUE,
            learn BOOLEAN DEFAULT FALSE
        )
    ''')

    # Create chosen_words table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chosen_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL UNIQUE,
            translation TEXT,
            chosen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create last_viewed_videos table
    c.execute('''
        CREATE TABLE IF NOT EXISTS last_viewed_videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL UNIQUE,
            video_title TEXT NOT NULL,
            viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Load words from the text file and insert them into the database
    try:
        with open(NEW_WORDS_FILE, 'r') as file:
            words = file.readlines()

        for word in words:
            word = word.strip()  # Remove leading/trailing spaces or newlines
            if word:  # Ensure the line is not empty
                c.execute('INSERT OR IGNORE INTO words (word) VALUES (?)', (word,))
    except FileNotFoundError:
        print(f"Warning: {NEW_WORDS_FILE} not found. Database will be initialized without initial words.")

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Function to get words from the database with pagination
def get_words(offset, limit):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM words LIMIT ? OFFSET ?', (limit, offset))
    words = c.fetchall()
    conn.close()
    return words

# Function to insert chosen words into the database
def save_chosen_words(words, translator):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Insert the new checked words into the 'chosen_words' table with translations
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for word in words:
            # Get translation for each word
            translation_response = translator.translate(word)
            translation = translation_response if translation_response else None
            
            cursor.execute(
                "INSERT OR IGNORE INTO chosen_words (word, translation, chosen_at) VALUES (?, ?, ?)",
                (word, translation, current_time)
            )
        conn.commit()

def get_all_words():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT word, learn FROM words')
        rows = cursor.fetchall()
        return [{"word": row[0], "learn": bool(row[1])} for row in rows]

def get_chosen_words():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT word, translation, chosen_at FROM chosen_words')
        rows = cursor.fetchall()
        return [{"word": row[0], "translation": row[1], "chosen_at": row[2]} for row in rows]

def save_last_viewed_video(video_id, video_title):
    """
    Save or update the last viewed video in the database.
    
    Args:
        video_id (str): The YouTube video ID
        video_title (str): The title of the video
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Use INSERT OR REPLACE to update if video_id exists
        cursor.execute(
            "INSERT OR REPLACE INTO last_viewed_videos (video_id, video_title, viewed_at) VALUES (?, ?, ?)",
            (video_id, video_title, current_time)
        )
        conn.commit()

def get_last_viewed_videos(limit=5):
    """
    Get the most recently viewed videos.
    
    Args:
        limit (int): Maximum number of videos to return (default: 5)
    
    Returns:
        list: List of dictionaries containing video_id, video_title, and viewed_at
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT video_id, video_title, viewed_at 
            FROM last_viewed_videos 
            ORDER BY viewed_at DESC 
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        return [{
            "video_id": row[0],
            "video_title": row[1],
            "viewed_at": row[2]
        } for row in rows]

def delete_video_and_data(video_id):
    """Delete a video and all its associated data from the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        
        # Delete from video_history table
        cur.execute("DELETE FROM last_viewed_videos WHERE video_id = ?", (video_id,))
        
        conn.commit()

        return {'status': 'success'}
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return {'status': 'error', 'message': str(e)}
