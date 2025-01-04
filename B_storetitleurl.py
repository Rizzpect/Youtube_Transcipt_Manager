"""
This script extracts the titles of YouTube videos from a list of URLs using the YouTube Data API.
It reads video URLs from an input file, fetches the title for each video, and writes the title along 
with the URL to an output file. The video ID is extracted from each URL using a regular expression.
API key is required to access the YouTube Data API.
"""

import re
import os
from googleapiclient.discovery import build

def extract_video_id(url):
    match = re.search(r"(?<=v=)[\w-]+", url)
    return match.group(0) if match else None

def get_video_title(api_key, video_id):
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.videos().list(part="snippet", id=video_id)
    response = request.execute()

    if "items" in response and response["items"]:
        return response["items"][0]["snippet"]["title"]
    else:
        return None

def main():
    # Your YouTube Data API key
    api_key = "AIzaSyBjEZ2btLRX1KKUiBydL3D_EmiLQfMxmjM"#Enter Api Key

    # File path containing video URLs
    file_path = r"D:\GITHUB\_urlfetchedlist.txt"

    # Output file path for storing video titles and URLs
    output_file_path = "video_titles_and_urls.txt"

    with open(file_path, 'r') as file:
        # Read video URLs from the file
        video_urls = [line.strip() for line in file]

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for video_url in video_urls:
            video_id = extract_video_id(video_url)

            if video_id:
                video_title = get_video_title(api_key, video_id)
                if video_title:
                    # Print to console
                    print(f"Video Title: {video_title}, URL: {video_url}")

                    # Write to output file
                    output_file.write(f"{video_title} - {video_url}\n")
                else:
                    print(f"Unable to fetch title for {video_url}")
            else:
                print(f"Invalid video URL: {video_url}")

if __name__ == "__main__":
    main()
