"""
This script extracts transcripts from YouTube videos using the YouTube Transcript API.
It reads a list of video URLs from a text file, fetches the transcript for each video, 
and saves it as a Markdown file. The script handles cases where subtitles are disabled 
or errors occur during the transcript fetching process, logging these issues to an error file.
"""


import os
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

# Replace with the path to your file containing URLs and titles
file_path = r"D:\GITHUB\video_titles_and_urls.txt" #filepath


# Read URLs and titles from the file with explicit encoding (UTF-8)
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Create a directory to store Markdown files
output_directory = 'transcripts'
os.makedirs(output_directory, exist_ok=True)

# Create a file to store errors
errors_file_path = 'ERRORS.txt'
with open(errors_file_path, 'w', encoding='utf-8') as errors_file:
    errors_file.write("Videos with Subtitle Fetch Errors:\n\n")

    # Loop through all the videos in the file
    for line in lines:
        # Print the line to identify the issue
        print(f"Processing line: {line.strip()}")

        # Extract video ID from the URL
        parsed_url = urlparse(line.strip())
        video_id = parse_qs(parsed_url.query).get('v', [''])[0]

        if not video_id:
            # Attempt to extract video ID from the end of the URL
            video_id = parsed_url.path.split('/')[-1]

            if not video_id:
                print(f"Error: Invalid URL format for line: {line.strip()}")
                continue

        # Fetch transcript using YouTubeTranscriptApi
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        except TranscriptsDisabled:
            # Handle TranscriptsDisabled exception
            error_message = f"Subtitles are disabled for the video {line.strip()}\n"
            errors_file.write(error_message)
            print(error_message)
            continue
        except Exception as e:
            # Log other errors in ERRORS.txt
            error_message = f"Error fetching transcript for {video_id}: {e}\n"
            errors_file.write(error_message)
            print(error_message)
            continue

        # Create a Markdown file for each video
        output_file_path = os.path.join(output_directory, f"{video_id}.md")

        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            # Write title and URL as header
            output_file.write(f"# {video_id}\n")
            output_file.write(f"Video URL: {line.strip()}\n\n")

            # Write transcript with timestamps
            for entry in transcript:
                start_time = entry['start']
                minutes = int(start_time // 60)
                seconds = int(start_time % 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"
                output_file.write(f"{timestamp} - {entry['text']}\n")

        print(f"Transcription for {video_id} saved to {output_file_path}")

print("Transcription process for all videos completed.")
