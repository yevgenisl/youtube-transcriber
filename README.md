# YouTube Transcript Summarizer and Word Frequency Analyzer

This Python script retrieves a transcript from a YouTube video, summarizes the content using OpenAI's GPT model, and analyzes the most frequent words in the transcript. The script also ensures that only new words are added to an output file, skipping words that already exist in the file.

## Features
- Retrieve and summarize the transcript of a YouTube video.
- Analyze the most frequent words in the transcript.
- Avoid adding duplicate words to the output file.
- Save the most frequent words to a text file, with each word on a new line.

## Requirements
- Python 3.6+
- `openai` library for interacting with OpenAI API
- `youtube-transcript-api` for retrieving YouTube video transcripts
- Docker or Podman (for running LibreTranslate locally)

You can install the required libraries using pip:

```bash
pip install openai youtube-transcript-api
```

## Translation Service Setup

To run your own translation service locally using LibreTranslate:

1. Clone the LibreTranslate repository:
```bash
git clone https://github.com/LibreTranslate/LibreTranslate.git
cd LibreTranslate
```

2. Run the service using Docker or Podman:
```bash
./run.sh
```

This will start the LibreTranslate service on `http://localhost:5000`. The service provides a free, self-hosted alternative to paid hosted LibreTranslate APIs.

Alternatively, you can run it using Podman:
```bash
podman run -it --rm -p 5000:5000 libretranslate/libretranslate
```

The translation service will be available at `http://localhost:5000` and can be used to translate text between various languages without requiring an API key.

## Usage

### Command-Line Arguments:
1. `--video_id`: The YouTube video ID (e.g., `RkETqdBxY3c`).
2. `--openai_api_key`: Your OpenAI API key to use GPT for summarization.
3. `--top_x`: The number of most frequent words to analyze and display (default is 10).
4. `--output_file`: The name of the file to save the most frequent words (default is `most_frequent_words.txt`).

### Example Command:
To summarize a YouTube video with ID `RkETqdBxY3c`, find the top 5 most frequent words, and save them to a file called `top_words.txt`, run the following command:

```bash
python youtube_transcript_summarizer.py --video_id RkETqdBxY3c --openai_api_key your-openai-api-key --top_x 5 --output_file top_words.txt
```

### Explanation:
1. The script retrieves the transcript of the YouTube video.
2. It splits the transcript into chunks and sends each chunk to OpenAI's GPT model for summarization.
3. The top X most frequent words from the transcript are counted, and any word already present in the output file will be skipped.
4. The new words are appended to the output file, each on a new line.
5. If the file doesn't exist, it will be created automatically.

## Sample Output

**Terminal Output**:

```bash
--- Summarizing chunk 1/3 ---
Summary of chunk 1...

--- Summarizing chunk 2/3 ---
Summary of chunk 2...

=== Final Summary ===
Combined summary of all chunks.

=== Most Frequent Words ===
Most frequent words saved to top_words.txt
1. the: 50 times
2. and: 35 times
3. to: 28 times
4. of: 20 times
5. in: 18 times
...
```


# YouTube Transcriber Front-end

This is the front-end component of the YouTube Transcriber application, built using Flask. It provides a web interface for managing and learning words from YouTube video transcripts.

## Features

- Word management system
- YouTube video transcript integration
- Word selection and tracking
- Learning progress monitoring

## Database Structure

The application uses SQLite with two main tables:

### Words Table
- Stores all available words
- Tracks learning status for each word
- Fields:
  - `id`: Primary key
  - `word`: The word text
  - `learn`: Boolean flag indicating if the word should be learned

### Chosen Words Table
- Tracks selected words and when they were chosen
- Fields:
  - `id`: Primary key
  - `word`: The selected word
  - `chosen_at`: Timestamp of when the word was selected

## API Endpoints

### Main Page
- `GET /`: Serves the main index page

### Word Management
- `GET /api/words`: Retrieves all words and their learning status
- `POST /api/save`: Saves selected words to the chosen_words table
- `GET /api/chosen_words`: Retrieves previously chosen words and their selection timestamps
- `GET /api/next_set_of_words`: Gets a new batch of words from YouTube video transcripts

## Setup and Initialization

1. The application initializes the database on startup
2. Words are loaded from `new_words.txt` into the database
3. Database tables are created if they don't exist

## YouTube Integration

- Fetches words from YouTube video transcripts
- Supports batch processing (20 words at a time)

## Technical Details

- Built with Flask web framework
- Uses SQLite for data persistence
- Integrates with a backend library for YouTube transcript processing

## Running the Application

```bash
python front-end/app.py
```

The application will start in debug mode and be accessible at `http://localhost:5000`.


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.