import os

def get_parent_path(filename):
     # Load words from the text file located in the parent directory
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))  # Get the parent directory path
    return os.path.join(parent_dir, filename)  # Construct the full file path
