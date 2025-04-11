
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

You can install the required libraries using pip:

```bash
pip install openai youtube-transcript-api
```

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

**Output File (`top_words.txt`)**:

```
the
and
to
of
in
...
```

If a word already exists in the file, it will not be added again.

## File Structure
- `youtube_transcript_summarizer.py`: The Python script.
- `most_frequent_words.txt`: (Optional) The output file containing the most frequent words.

## Error Handling
- If the YouTube video is not available or if there are issues with the API, the script will print an error message to the console.
- If the output file cannot be written, an error message will be displayed.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.