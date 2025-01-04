"""
This script fetches auto-generated YouTube video transcripts and saves them as Markdown files. 
It processes a list of video URLs from an input file, extracts the video ID, retrieves the auto-generated transcript 
using the YouTube Transcript API, and writes the transcript along with video details into a Markdown file. 
Each file is named based on the video title and ID.
"""


import re
import os
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(video_url):
    # Use regular expression to find the video ID in the URL
    match = re.search(r'(?<=v=)[^&]+', video_url)
    return match.group(0) if match else None

def get_auto_generated_transcript(video_id, language_code='en'):
    try:
        # Get the transcript list for the video
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Find the auto-generated transcript for the specified language
        auto_generated_transcript = transcript_list.find_generated_transcript([language_code])

        # Fetch and return the auto-generated transcript data
        return auto_generated_transcript.fetch()
    
    except Exception as e:
        # Handle exceptions (e.g., if the video does not have auto-generated captions)
        print(f"Error: {e}")
        return None

def process_videos(input_file_path, output_folder):
    with open(input_file_path, 'r') as file:
        for line in file:
            # Extract video ID from the video URL using the improved method
            video_url = line.strip()
            video_id = extract_video_id(video_url)

            if video_id:
                # Print the video ID (you can remove this line if not needed)
                print(f"Processing video: {video_id}")

                # Get the auto-generated transcript
                transcript_data = get_auto_generated_transcript(video_id)

                if transcript_data:
                    # Extract video title from the video URL
                    video_title = video_url.split('/')[-1].split('?')[0]

                    # Create markdown file
                    output_file_path = os.path.join(output_folder, f"{video_title}_{video_id}.md")

                    # Write information to markdown file
                    with open(output_file_path, 'w', encoding='utf-8') as output_file:
                        output_file.write(f"# {video_title}\n\n")
                        output_file.write(f"**Video URL:** {video_url}\n\n")
                        output_file.write("## Transcript\n\n")

                        for entry in transcript_data:
                            # Include timestamps in minutes and seconds
                            start_time = entry['start']
                            minutes, seconds = divmod(start_time, 60)
                            timestamp = f"{int(minutes):02d}:{int(seconds):02d}"
                            
                            output_file.write(f"{timestamp} - {entry['text']}\n\n")

                    print(f"Transcription saved to: {output_file_path}")
                else:
                    print(f"Unable to retrieve transcript for video: {video_id}")
            else:
                print(f"Unable to extract video ID from URL: {video_url}")

# Replace 'R:\\VS\\ERRORS.txt' with the actual path to your text file
input_file_path = 'D:\VS\Python\_urlfetchedlist.txt'
# Replace 'R:\\VS\\errors' with the actual path to the folder where you want to save markdown files
output_folder = 'D:\VS\Python\Andrew kirby'

# Call the function to process videos
process_videos(input_file_path, output_folder)
