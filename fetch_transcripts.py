"""
Consolidated script to fetch YouTube video transcripts for a channel.

Fetches video URLs, retrieves titles using the YouTube Data API,
gets transcripts (preferring manual, falling back to auto-generated),
cleans filenames based on titles, and saves transcripts to Markdown files.
"""

import os
import sys
import re
import scrapetube
import unicodedata
import argparse
import logging
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# --- Configuration ---

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log_file_handler = logging.FileHandler('transcript_fetcher.log', encoding='utf-8')
log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(log_file_handler)


# --- Helper Functions ---

def clean_filename(text):
    """Cleans a string to be suitable for use as a filename."""
    # Replace invalid characters with underscores
    invalid_chars = r'[\/:*?"<>|]'
    text = re.sub(invalid_chars, '_', text)

    # Normalize Unicode (remove weird spaces and accents)
    try:
        text = unicodedata.normalize("NFKD", text)
        text = text.replace('\xa0', ' ')  # Replace non-breaking space
        # Keep only basic ASCII, replace others with '_'
        text = ''.join(c if ord(c) < 128 else '_' for c in text)
    except TypeError:
        logging.warning(f"Could not normalize filename: {text}")
        # Fallback for non-string types or unexpected errors
        text = "invalid_filename"


    # Remove leading/trailing whitespace and underscores/periods
    text = text.strip(' ._')

    # Limit length (optional, but good practice for filesystems)
    max_len = 150
    if len(text) > max_len:
        text = text[:max_len].rsplit(' ', 1)[0] # Try to cut at last space

    # Handle empty filenames after cleaning
    if not text:
        text = "untitled"

    return text

def get_channel_videos(channel_id):
    """Fetches video details (ID and URL) for a given channel ID using scrapetube."""
    videos_data = []
    try:
        logging.info(f"Fetching videos for channel ID: {channel_id}")
        videos = scrapetube.get_channel(channel_id)
        count = 0
        for video in videos:
            video_id = video.get('videoId')
            if video_id:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                videos_data.append({'id': video_id, 'url': video_url})
                count += 1
            else:
                logging.warning("Found item without videoId, skipping.")
        logging.info(f"Found {count} videos.")
        return videos_data
    except Exception as e:
        logging.error(f"Failed to fetch videos using scrapetube: {e}")
        return None

def get_video_title(youtube_api_client, video_id):
    """Fetches the video title using the YouTube Data API."""
    try:
        request = youtube_api_client.videos().list(part="snippet", id=video_id)
        response = request.execute()
        if "items" in response and response["items"]:
            title = response["items"][0]["snippet"]["title"]
            logging.debug(f"Fetched title for {video_id}: {title}")
            return title
        else:
            logging.warning(f"No title found in API response for video ID: {video_id}")
            return None
    except Exception as e:
        logging.error(f"Error fetching title for video ID {video_id}: {e}")
        return None

def get_transcript(video_id):
    """Fetches transcript, preferring manual, falling back to auto-generated ('en')."""
    try:
        # Try getting any available transcript (often prioritizes manual)
        logging.debug(f"Attempting to fetch default transcript for {video_id}")
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_manually_created_transcript(['en']) # Prioritize manual English
        logging.info(f"Found manually created English transcript for {video_id}")
        return transcript.fetch()
    except NoTranscriptFound:
        logging.warning(f"No manual English transcript found for {video_id}. Trying auto-generated.")
        try:
            # Fallback to auto-generated English transcript
            generated_transcript = transcript_list.find_generated_transcript(['en'])
            logging.info(f"Found auto-generated English transcript for {video_id}")
            return generated_transcript.fetch()
        except NoTranscriptFound:
            logging.error(f"No manual or auto-generated English transcript found for {video_id}.")
            return None
    except TranscriptsDisabled:
        logging.error(f"Transcripts are disabled for video: {video_id}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred fetching transcript for {video_id}: {e}")
        return None

def save_transcript(output_dir, title, video_id, video_url, transcript_data):
    """Saves the transcript data to a Markdown file."""
    if not title:
        logging.warning(f"Video {video_id} missing title, using ID as filename.")
        title = video_id # Use ID if title fetch failed

    cleaned_title = clean_filename(title)
    filename = f"{cleaned_title}.md"
    output_path = os.path.join(output_dir, filename)

    try:
        logging.debug(f"Saving transcript for {video_id} to {output_path}")
        os.makedirs(output_dir, exist_ok=True) # Ensure directory exists
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Video URL:** {video_url}\n\n")
            f.write("## Transcript\n\n")

            for entry in transcript_data:
                start_time = entry['start']
                minutes = int(start_time // 60)
                seconds = int(start_time % 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"
                text = entry['text'].replace('\n', ' ').strip() # Clean up text slightly
                if text: # Avoid writing empty lines if text is just whitespace
                    f.write(f"`{timestamp}` - {text}\n") # Using backticks for timestamp

        logging.info(f"Successfully saved: {output_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to save transcript for {video_id} to {output_path}: {e}")
        return False

# --- Main Execution ---

def main():
    # Remove argparse completely as we handle all inputs interactively
    # parser = argparse.ArgumentParser(description="Fetch YouTube transcripts for a given channel.")
    # parser.add_argument("-o", "--output-dir", default="Transcripts", help="Directory to save transcript files (default: Transcripts).")
    # args = parser.parse_args()

    # --- Get User Inputs ---
    channel_id = input("Please enter the YouTube Channel ID: ").strip()
    api_key = input("Please enter your YouTube Data API v3 Key: ").strip()

    # Input for base directory path
    base_save_path = input("Enter the base directory path to save the transcript folder in: ").strip()

    # Validate base path
    if not os.path.isdir(base_save_path):
        logging.error(f"Error: The specified save path '{base_save_path}' does not exist or is not a directory.")
        sys.exit(1)

    # Input for transcript folder name
    transcript_folder_name = input("Enter the desired name for the transcript folder (e.g., 'Transcripts'): ").strip()
    if not transcript_folder_name: # Use default if empty
        transcript_folder_name = "Transcripts"
        logging.info("Using default folder name 'Transcripts'.")

    # Construct the final output directory path
    output_dir = os.path.join(base_save_path, transcript_folder_name)

    logging.info(f"Starting transcript fetcher for channel: {channel_id}")
    logging.info(f"Transcripts will be saved to: {output_dir}") # Log the final path

    # Basic validation for channel ID and API key
    if not channel_id:
        logging.error("Channel ID cannot be empty.")
        sys.exit(1)
    if not api_key:
        logging.error("YouTube Data API key cannot be empty.")
        sys.exit(1)

    # 1. Get Video List
    videos = get_channel_videos(channel_id) # Use variable from input()
    if videos is None:
        logging.error("Could not retrieve video list. Exiting.")
        sys.exit(1)
    if not videos:
        logging.info("No videos found for this channel.")
        sys.exit(0)

    # 2. Initialize YouTube Data API client
    try:
        youtube_api = build("youtube", "v3", developerKey=api_key) # Use variable from input()
    except Exception as e:
        logging.error(f"Failed to build YouTube API client: {e}")
        sys.exit(1)

    # 3. Process Videos
    success_count = 0
    fail_count = 0
    # videos_to_process = videos[:args.limit] if args.limit > 0 else videos # Apply limit if specified

    for video in videos: # Use videos_to_process if limit is enabled
        video_id = video['id']
        video_url = video['url']
        logging.info(f"--- Processing video ID: {video_id} ---")

        # 4. Get Title
        title = get_video_title(youtube_api, video_id)
        if not title:
            logging.warning(f"Proceeding without title for {video_id}")
            title = video_id # Use ID as fallback title for filename generation

        # 5. Get Transcript (with fallback)
        transcript_data = get_transcript(video_id)

        # 6. Save Transcript
        if transcript_data:
            if save_transcript(output_dir, title, video_id, video_url, transcript_data):
                success_count += 1
            else:
                fail_count += 1
        else:
            logging.error(f"Failed to get transcript for video {video_id} ({title}). Skipping save.")
            fail_count += 1

    logging.info("--- Processing Complete ---")
    logging.info(f"Successfully saved transcripts: {success_count}")
    logging.info(f"Failed to process/save: {fail_count}")
    logging.info(f"Log file saved to: transcript_fetcher.log")

if __name__ == "__main__":
    main() 