import argparse
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import textwrap
import re
from collections import Counter
from lib.utils import get_parent_path
import urllib.request
import json
import urllib
import pprint
import os
import pickle


def get_video_meta(video_id):
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    try:
        with urllib.request.urlopen(url) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            return {
                'title': data.get('title', 'Unknown Title'),
                'oembed_html': data.get('html', '')
            }
    except Exception as e:
        print(f"Error getting video metadata: {e}")
        return {'title': 'Unknown Title', 'oembed_html': ''}


def get_video_transcript(video_id):
    cache_dir = os.path.join(get_parent_path("data/cache"))
    cache_file = os.path.join(cache_dir, f"transcript_{video_id}.pkl")
    
    # Check if cached file exists
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as f:
                transcript = pickle.load(f)
            full_text = " ".join([entry.text for entry in transcript])
            return full_text
        except Exception as e:
            print(f"Error reading cached transcript: {e}")
    
    try:
        # If no cache exists or cache read failed, fetch from API
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=['es'])
        
        # Save to cache
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(transcript, f)
        except Exception as e:
            print(f"Error saving transcript to cache: {e}")
        
        full_text = " ".join([entry.text for entry in transcript])
        return full_text
    except Exception as e:
        print(f"Error: {e}")
        return None

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

def find_sentences_with_word(video_id, target_word):
    """
    Find all sentences containing a specific word in the transcript, along with their timestamps.
    
    Args:
        video_id (str): The YouTube video ID
        target_word (str): The word to search for
        
    Returns:
        list: List of tuples containing (sentence, timestamp) where the target word appears
    """
    try:
        # Get the transcript with timestamps
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=['es'])
        
        # Convert target word to lowercase for case-insensitive search
        target_word = target_word.lower()
        
        # Find sentences containing the target word
        matching_sentences = []
        for entry in transcript:
            if target_word in entry.text.lower():
                # Clean up the sentence (remove extra whitespace)
                cleaned_sentence = ' '.join(entry.text.split())
                # Format timestamp as MM:SS
                timestamp = f"{int(entry.start // 60):02d}:{int(entry.start % 60):02d}"
                matching_sentences.append((cleaned_sentence, timestamp))
        
        return matching_sentences
    except Exception as e:
        print(f"Error: {e}")
        return []

# Main entry point
def get_next_batch(video_id,batch_size):
    transcript_text=get_video_transcript(video_id)
    output_file = get_parent_path("most_frequent_words.txt")
    return find_most_frequent_words(transcript_text,batch_size,output_file)
