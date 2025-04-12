from flask import Flask, render_template, jsonify, request
import sqlite3
import os

app = Flask(__name__)
DB_FILE = 'words.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                learn BOOLEAN NOT NULL
            )
        ''')

        # Only populate if empty
        cursor.execute('SELECT COUNT(*) FROM words')
        if cursor.fetchone()[0] == 0:
            sample_words = [f"Word_{i}" for i in range(1, 201)]
            cursor.executemany('INSERT INTO words (word, learn) VALUES (?, ?)',
                               [(w, False) for w in sample_words])
        conn.commit()

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
        cursor.execute("UPDATE words SET learn = 0")  # Reset all
        cursor.executemany(
            "UPDATE words SET learn = 1 WHERE word = ?",
            [(word,) for word in checked_words]
        )
        conn.commit()

    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
