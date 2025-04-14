from flask import Flask, render_template, jsonify, request
import sqlite3
import os,sys
from datetime import datetime

# Add the 'lib' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.utils import get_parent_path
from lib.youtube import get_next_batch

app = Flask(__name__)
DB_FILE = 'words.db'

def init_db():
    # Connect to SQLite database
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create words table
    c.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            learn BOOLEAN DEFAULT FALSE
        )
    ''')

    # Create chosen_words table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chosen_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
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
            c.execute('INSERT INTO words (word) VALUES (?)', (word,))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/words")
def get_words():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT word, learn FROM words')
        rows = cursor.fetchall()
        return jsonify([{"word": row[0], "learn": bool(row[1])} for row in rows])

@app.route("/api/save", methods=["POST"])
def save_words():
    data = request.get_json()
    if not data or "words" not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    checked_words = data["words"]

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Clear previous entries in the 'chosen_words' table
        #cursor.execute("DELETE FROM chosen_words")
        
        # Insert the new checked words into the 'chosen_words' table
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.executemany(
            "INSERT INTO chosen_words (word, chosen_at) VALUES (?, ?)",
            [(word, current_time) for word in checked_words]
        )
        conn.commit()

    return jsonify({"status": "success"})

@app.route("/api/chosen_words")
def get_chosen_words():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT word, chosen_at FROM chosen_words')
        rows = cursor.fetchall()
        return jsonify([{"word": row[0], "chosen_at": row[1]} for row in rows])

# Route to get the next set of words
@app.route('/api/next_set_of_words', methods=['GET'])
def next_set_of_words():
    batch_size = 20  # Set batch size (you can adjust this)

    #get_video_transcript()
    words = get_next_batch("RkETqdBxY3c",10)
    word_list = [{'word': word[0]} for word in words]  # Extracting the word part from the tuple
    return jsonify(word_list)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
