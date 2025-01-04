"""
This script fetches all video URLs from a YouTube channel based on a provided channel ID using the Scrapetube library.
The script prompts the user to input the channel ID, retrieves all video URLs for that channel, 
and then prints and saves the URLs into a text file named '_list.txt'.
"""

import os
import scrapetube
import sys

# Set the file path dynamically
path = os.path.join(os.path.dirname(__file__), '_urlfetchedlist.txt')

print('**********************\n')
print("The result will be saved in '_list.txt' file.")
print("Enter Channel ID (e.g., UCSvoBOtMz9AWVpk84XgVOeA):")

# Prints the output in the console and into the '_list.txt' file.
class Logger:
    def __init__(self, filename):
        self.console = sys.stdout
        self.file = open(filename, 'w')

    def write(self, message):
        self.console.write(message)
        self.file.write(message)

    def flush(self):
        self.console.flush()
        self.file.flush()

sys.stdout = Logger(path)

# Get the channel ID directly
channel_id = input().strip()

# Fetch all video URLs for the given channel ID
videos = scrapetube.get_channel(channel_id)

# Print and save the video URLs
for video in videos:
    video_url = f"https://www.youtube.com/watch?v={video['videoId']}"
    print(video_url)
    sys.stdout.flush()  # Ensure the output is flushed immediately to the file
