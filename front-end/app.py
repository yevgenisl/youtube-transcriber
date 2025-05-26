from flask import Flask, render_template, jsonify, request, Response
import os,sys
from datetime import datetime
import io
import csv

# Add the 'lib' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.utils import get_parent_path
from lib.youtube import get_next_batch, find_sentences_with_word, get_video_meta
from lib.translation import translator
from lib.db_logic import init_db, get_all_words, save_chosen_words, get_chosen_words, save_last_viewed_video, get_last_viewed_videos,delete_video_and_data, delete_chosen_words
from memory_profiler import profile

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/words")
@profile
def get_words():
    return jsonify(get_all_words())

@app.route("/api/save", methods=["POST"])
@profile
def save_words():
    data = request.get_json()
    if not data or "words" not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    checked_words = data["words"]
    save_chosen_words(checked_words, translator)
    return jsonify({"status": "success"})

@app.route("/api/chosen_words")
@profile
def get_chosen_words_route():
    return jsonify(get_chosen_words())

# Route to get the next set of words
@app.route('/api/next_set_of_words', methods=['GET'])
@profile
def next_set_of_words():
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({"error": "Video ID is required"}), 400

    batch_size = 20  # Set batch size (you can adjust this)
    words = get_next_batch(video_id, batch_size)
    word_list = [{'word': word[0]} for word in words]  # Extracting the word part from the tuple
    return jsonify(word_list)

@app.route("/api/translate", methods=["POST"])
@profile
def translate_word():
    data = request.get_json()
    if not data or "word" not in data:
        return jsonify({"error": "Word is required"}), 400
    
    word = data["word"]
    translation = translator.translate(word)
    
    if translation is None:
        return jsonify({"error": "Translation failed"}), 500
    
    return jsonify({"translation": translation})

@app.route("/api/search_sentences", methods=["GET"])
@profile
def search_sentences():
    word = request.args.get('word')
    video_id = request.args.get('video_id')
    
    if not word or not video_id:
        return jsonify({"error": "Word and video_id are required"}), 400
    
    try:
        # Find sentences containing the word with timestamps
        sentences_with_timestamps = find_sentences_with_word(video_id, word)
        
        # Format the results for the frontend
        formatted_results = [
            {
                "sentence": sentence,
                "timestamp": timestamp
            }
            for sentence, timestamp in sentences_with_timestamps
        ]
        
        return jsonify({"sentences": formatted_results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/video_metadata')
@profile
def get_video_metadata():
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({'error': 'Video ID is required'}), 400

    try:
        metadata = get_video_meta(video_id)
        # Save the viewed video to the database
        save_last_viewed_video(video_id, metadata['title'])
        return jsonify(metadata)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/last_viewed_videos')
def get_last_viewed_videos_route():
    limit = request.args.get('limit', default=5, type=int)
    return jsonify(get_last_viewed_videos(limit))

@app.route('/api/last_viewed_video')
def get_last_viewed_video_route():
    try:
        videos = get_last_viewed_videos(1)  # Get only the most recent video
        if videos:
            return jsonify({'status': 'success', 'video': videos[0]})
        return jsonify({'status': 'success', 'video': None})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/delete_video', methods=['POST'])
def delete_video():
    try:
        data = request.get_json()
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({'status': 'error', 'message': 'Video ID is required'}), 400
            
        #return jsonify({'status': 'error', 'message': 'Video ID is required'}), 400
        result = delete_video_and_data(video_id)
        
        if result['status'] == 'error':
            return jsonify(result), 500
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route("/api/delete_chosen_words", methods=["POST"])
def delete_chosen_words_route():
    data = request.get_json()
    if not data or "words" not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    words = data["words"]
    delete_chosen_words(words)
    return jsonify({"status": "success"})

@app.route('/api/export_words', methods=['POST'])
@profile
def export_words():
    try:
        # Check if the request has JSON content
        if not request.is_json:
            return jsonify({'status': 'error', 'message': 'Content-Type must be application/json'}), 415

        data = request.get_json()
        if not data or 'words' not in data:
            return jsonify({'status': 'error', 'message': 'No words provided'}), 400

        words_data = data['words']
        if not words_data:
            return jsonify({'status': 'error', 'message': 'Empty words list provided'}), 400

        # Create a CSV file in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Word', 'Translation'])
        
        # Write data
        for word in words_data:
            writer.writerow([word['word'], word['translation']])
        
        # Prepare the response
        output.seek(0)
        csv_data = output.getvalue()
        output.close()
        
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={
                "Content-disposition": "attachment; filename=exported_words.csv"
            }
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    init_db()
    # NOTE: For production deployments, debug=True should be turned off.
    # Flask's debug mode is not recommended for production due to performance, security, and memory implications.
    app.run(debug=True, port=5002,host='0.0.0.0')
