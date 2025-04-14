import argparse
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import textwrap
import re
from collections import Counter
from lib.utils import get_parent_path

def get_video_transcript(video_id):
    try:
        transcript=YouTubeTranscriptApi().fetch(video_id, languages=['es'])
        full_text = " ".join([entry.text for entry in transcript])
        return full_text
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

    return top_new_words


    # Print the most common words
    print(f"Most frequent words saved to {output_file}")
    for i, (word, count) in enumerate(top_new_words, 1):
        print(f"{i}. {word}: {count} times")


# Main entry point
def get_next_batch(video_id,batch_size):
    transcript_text=get_video_transcript(video_id)
    output_file = get_parent_path("most_frequent_words.txt")
    return find_most_frequent_words(transcript_text,batch_size,output_file)
