import sqlite3

# Function to initialize the database
def init_db():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            learn BOOLEAN DEFAULT FALSE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS chosen_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            chosen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Function to get words from the database with pagination
def get_words(offset, limit):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute('SELECT * FROM words LIMIT ? OFFSET ?', (limit, offset))
    words = c.fetchall()
    conn.close()
    return words

# Function to insert chosen words into the database
def save_chosen_words(words):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    for word in words:
        c.execute('INSERT INTO chosen_words (word) VALUES (?)', (word,))
    conn.commit()
    conn.close()
