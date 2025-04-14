import argparse
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import textwrap
import re
from collections import Counter

# Set up argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description="YouTube Transcript Summarizer using ChatGPT.")
    parser.add_argument('--video_id', type=str, required=True, help='YouTube video ID')
    parser.add_argument('--openai_api_key', type=str, required=True, help='Your OpenAI API key')
    parser.add_argument('-s','--summarize', type=bool,required=False,default=False,help='Summarize Transcript using ChatGPT')
    parser.add_argument('--top_x', type=int, default=10, help='Number of most frequent words to display')
    parser.add_argument('--output_file', type=str, default='most_frequent_words.txt', help='File to save the most frequent words')

    return parser.parse_args()

def get_video_transcript(video_id):
    try:
        transcript=YouTubeTranscriptApi().fetch(video_id, languages=['es'])
        full_text = " ".join([entry.text for entry in transcript])
        return full_text
    except Exception as e:
        print(f"Error: {e}")

def summarize_transcript(transcript_text, openai_api_key):
    # Set your OpenAI API key
    openai.api_key = openai_api_key
    chunk_size = 3000  # Adjust based on model input limits
    model = "gpt-4o"    # Or "gpt-3.5-turbo" if you prefer
    print ("Summarizing text")
    try:
    # Split into chunks
        chunks = textwrap.wrap(transcript_text, chunk_size)

        summaries = []

        for i, chunk in enumerate(chunks):
            print(f"\n--- Summarizing chunk {i+1}/{len(chunks)} ---")

            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant who summarizes YouTube video transcripts."},
                    {"role": "user", "content": f"Summarize this portion of a YouTube transcript:\n\n{chunk}"}
                ],
                temperature=0.5,
                max_tokens=500
            )

            summary = response['choices'][0]['message']['content']
            summaries.append(f"Chunk {i+1} summary:\n{summary}")

        # Combine all chunk summaries
        full_summary = "\n\n".join(summaries)
        print("\n=== Final Summary ===\n")
        print(full_summary)

    except Exception as e:
        print(f"Error: {e}")

# Function to analyze and find the most used words
def find_most_frequent_words(text, top_x,output_file):
    # Normalize text by converting to lowercase and removing punctuation
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)

    # Split the text into words
    words = text.split()

    # Count the frequency of each word
    word_counts = Counter(words)

    # Read existing words from the output file to avoid duplicates
    existing_words = set()
    try:
        with open(output_file, 'r') as f:
            existing_words = set(line.strip() for line in f)
    except FileNotFoundError:
        # If the file doesn't exist, it will be created later
        pass

    # Filter out words that are already in the existing file
    #filtered_words = [(word, count) for word, count in word_counts.most_common(top_x) if word not in existing_words]
    filtered_words = [(word, count) for word, count in word_counts.items() if word not in existing_words]
    top_new_words = sorted(filtered_words, key=lambda x: x[1], reverse=True)[:top_x]



    # Get the most common words
    # most_common_words = word_counts.most_common(top_x)

    # Save the most common words to a file (skip existing words)
    with open(output_file, 'a') as f:  # Open in append mode to avoid overwriting
        for word, count in top_new_words:
            f.write(f"{word}\n")


    # save the new words only
    with open('new_words.txt', 'w') as f:  # Open in append mode to avoid overwriting
        for word, count in top_new_words:
            f.write(f"{word}\n")



    # Print the most common words
    print(f"Most frequent words saved to {output_file}")
    for i, (word, count) in enumerate(top_new_words, 1):
        print(f"{i}. {word}: {count} times")


# Main entry point
if __name__ == "__main__":
    args = parse_arguments()
    transcript_text=get_video_transcript(args.video_id)
    find_most_frequent_words(transcript_text,args.top_x,args.output_file)
    if args.summarize:
        summarize_transcript(transcript_text, args.openai_api_key)