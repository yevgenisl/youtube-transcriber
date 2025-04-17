from flask import Flask, render_template, jsonify, request
import os,sys
from datetime import datetime

# Add the 'lib' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.utils import get_parent_path
from lib.youtube import get_next_batch
from lib.translation import translator
from lib.db_logic import init_db, get_all_words, save_chosen_words, get_chosen_words

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/words")
def get_words():
    return jsonify(get_all_words())

@app.route("/api/save", methods=["POST"])
def save_words():
    data = request.get_json()
    if not data or "words" not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    checked_words = data["words"]
    save_chosen_words(checked_words, translator)
    return jsonify({"status": "success"})

@app.route("/api/chosen_words")
def get_chosen_words_route():
    return jsonify(get_chosen_words())

# Route to get the next set of words
@app.route('/api/next_set_of_words', methods=['GET'])
def next_set_of_words():
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({"error": "Video ID is required"}), 400

    batch_size = 20  # Set batch size (you can adjust this)
    words = get_next_batch(video_id, batch_size)
    word_list = [{'word': word[0]} for word in words]  # Extracting the word part from the tuple
    return jsonify(word_list)

@app.route("/api/translate", methods=["POST"])
def translate_word():
    data = request.get_json()
    if not data or "word" not in data:
        return jsonify({"error": "Word is required"}), 400
    
    word = data["word"]
    translation = translator.translate(word)
    
    if translation is None:
        return jsonify({"error": "Translation failed"}), 500
    
    return jsonify({"translation": translation})

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5002)
