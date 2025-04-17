# Add the 'lib' directory to the Python path
import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from datetime import datetime
from lib.utils import get_parent_path

DB_FILE = get_parent_path('words.db')

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

    file_path = get_parent_path('new_words.txt')
    # Load words from the text file and insert them into the database
    with open(file_path, 'r') as file:
        words = file.readlines()

    for word in words:
        word = word.strip()  # Remove leading/trailing spaces or newlines
        if word:  # Ensure the line is not empty
            c.execute('INSERT OR IGNORE INTO words (word) VALUES (?)', (word,))

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
