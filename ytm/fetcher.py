"""
Core transcript fetching engine.

Fetches video URLs from YouTube channels or individual videos,
retrieves transcripts, and saves them in multiple formats.
"""

import os
import json
import logging

import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from tqdm import tqdm

from .utils import clean_filename, format_timestamp, extract_video_id

logger = logging.getLogger(__name__)


def get_channel_videos(channel_id):
    """
    Fetch all video details for a given YouTube channel.

    Uses scrapetube to scrape video list (no API key required).
    Extracts video ID, URL, and title from the scraped data.

    Args:
        channel_id: YouTube channel ID string.

    Returns:
        List of dicts with keys: 'id', 'url', 'title'.
        Returns None on failure.
    """
    videos_data = []
    try:
        logger.info(f"Fetching videos for channel ID: {channel_id}")
        videos = scrapetube.get_channel(channel_id)
        count = 0
        for video in videos:
            video_id = video.get("videoId")
            if video_id:
                # Extract title from scrapetube data (no API key needed!)
                title = "Untitled"
                title_obj = video.get("title", {})
                if isinstance(title_obj, dict):
                    runs = title_obj.get("runs", [])
                    if runs and isinstance(runs, list):
                        title = runs[0].get("text", "Untitled")
                    else:
                        accessibility = title_obj.get("accessibility", {})
                        label = accessibility.get("accessibilityData", {}).get("label", "")
                        if label:
                            title = label
                elif isinstance(title_obj, str):
                    title = title_obj

                video_url = f"https://www.youtube.com/watch?v={video_id}"
                videos_data.append({"id": video_id, "url": video_url, "title": title})
                count += 1
            else:
                logger.warning("Found item without videoId, skipping.")
        logger.info(f"Found {count} videos.")
        return videos_data
    except Exception as e:
        logger.error(f"Failed to fetch videos using scrapetube: {e}")
        return None


def get_video_title_from_api(youtube_api_client, video_id):
    """
    Fetch the video title using the YouTube Data API.

    Args:
        youtube_api_client: Authenticated YouTube API client.
        video_id: YouTube video ID.

    Returns:
        Video title string, or None on failure.
    """
    try:
        request = youtube_api_client.videos().list(part="snippet", id=video_id)
        response = request.execute()
        if "items" in response and response["items"]:
            title = response["items"][0]["snippet"]["title"]
            logger.debug(f"Fetched title for {video_id}: {title}")
            return title
        else:
            logger.warning(f"No title found in API response for video ID: {video_id}")
            return None
    except Exception as e:
        logger.error(f"Error fetching title for video ID {video_id}: {e}")
        return None


def get_transcript(video_id, languages=None):
    """
    Fetch transcript for a YouTube video.

    Prefers manually created transcripts, falls back to auto-generated.
    Supports multiple language preferences.

    Args:
        video_id: YouTube video ID.
        languages: List of language codes to try (default: ['en']).

    Returns:
        List of transcript entry dicts with 'text', 'start', 'duration' keys.
        Returns None if no transcript is available.
    """
    if languages is None:
        languages = ["en"]

    try:
        logger.debug(f"Attempting to fetch transcript for {video_id} (languages: {languages})")
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try manually created transcript first
        try:
            transcript = transcript_list.find_manually_created_transcript(languages)
            logger.info(f"Found manually created transcript for {video_id}")
            return transcript.fetch()
        except NoTranscriptFound:
            pass

        # Fallback to auto-generated
        try:
            generated = transcript_list.find_generated_transcript(languages)
            logger.info(f"Found auto-generated transcript for {video_id}")
            return generated.fetch()
        except NoTranscriptFound:
            logger.error(f"No transcript found for {video_id} in languages: {languages}")
            return None

    except TranscriptsDisabled:
        logger.error(f"Transcripts are disabled for video: {video_id}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching transcript for {video_id}: {e}")
        return None


def save_transcript(output_dir, title, video_id, video_url, transcript_data, fmt="md"):
    """
    Save transcript data to a file in the specified format.

    Supported formats:
    - 'md'  : Markdown with timestamps
    - 'json': JSON array of entries
    - 'txt' : Plain text (no timestamps)
    - 'srt' : SubRip subtitle format

    Args:
        output_dir: Directory to save the file in.
        title: Video title (used for filename).
        video_id: YouTube video ID.
        video_url: Full YouTube video URL.
        transcript_data: List of transcript entry dicts.
        fmt: Output format ('md', 'json', 'txt', 'srt').

    Returns:
        The output filepath on success, None on failure.
    """
    if not title:
        logger.warning(f"Video {video_id} missing title, using ID as filename.")
        title = video_id

    cleaned_title = clean_filename(title)
    extension = fmt if fmt in ("md", "json", "txt", "srt") else "md"
    filename = f"{cleaned_title}.{extension}"
    output_path = os.path.join(output_dir, filename)

    try:
        os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            if fmt == "md":
                _write_markdown(f, title, video_url, transcript_data)
            elif fmt == "json":
                _write_json(f, title, video_id, video_url, transcript_data)
            elif fmt == "txt":
                _write_text(f, title, video_url, transcript_data)
            elif fmt == "srt":
                _write_srt(f, transcript_data)
            else:
                _write_markdown(f, title, video_url, transcript_data)

        logger.info(f"Saved: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save transcript for {video_id} to {output_path}: {e}")
        return None


def _write_markdown(f, title, video_url, transcript_data):
    """Write transcript in Markdown format."""
    f.write(f"# {title}\n\n")
    f.write(f"**Video URL:** [{video_url}]({video_url})\n\n")
    f.write("## Transcript\n\n")
    for entry in transcript_data:
        timestamp = format_timestamp(entry["start"])
        text = entry["text"].replace("\n", " ").strip()
        if text:
            f.write(f"`{timestamp}` — {text}\n")


def _write_json(f, title, video_id, video_url, transcript_data):
    """Write transcript in JSON format."""
    output = {
        "title": title,
        "video_id": video_id,
        "video_url": video_url,
        "transcript": [
            {
                "timestamp": format_timestamp(entry["start"]),
                "start_seconds": round(entry["start"], 2),
                "duration": round(entry.get("duration", 0), 2),
                "text": entry["text"].replace("\n", " ").strip(),
            }
            for entry in transcript_data
            if entry["text"].strip()
        ],
    }
    json.dump(output, f, indent=2, ensure_ascii=False)


def _write_text(f, title, video_url, transcript_data):
    """Write transcript in plain text format."""
    f.write(f"{title}\n")
    f.write(f"URL: {video_url}\n")
    f.write("=" * 60 + "\n\n")
    for entry in transcript_data:
        text = entry["text"].replace("\n", " ").strip()
        if text:
            f.write(f"{text} ")
    f.write("\n")


def _write_srt(f, transcript_data):
    """Write transcript in SubRip (SRT) subtitle format."""
    index = 1
    for entry in transcript_data:
        text = entry["text"].replace("\n", " ").strip()
        if not text:
            continue
        start = entry["start"]
        duration = entry.get("duration", 2.0)
        end = start + duration

        f.write(f"{index}\n")
        f.write(f"{_srt_time(start)} --> {_srt_time(end)}\n")
        f.write(f"{text}\n\n")
        index += 1


def _srt_time(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def file_already_exists(output_dir, title, fmt="md"):
    """
    Check if a transcript file already exists (for resume support).

    Args:
        output_dir: Directory where transcripts are saved.
        title: Video title.
        fmt: File format extension.

    Returns:
        True if the file already exists.
    """
    cleaned_title = clean_filename(title)
    extension = fmt if fmt in ("md", "json", "txt", "srt") else "md"
    filename = f"{cleaned_title}.{extension}"
    return os.path.exists(os.path.join(output_dir, filename))


def fetch_channel_transcripts(
    channel_id,
    output_dir="Transcripts",
    api_key=None,
    fmt="md",
    languages=None,
    skip_existing=True,
    limit=0,
):
    """
    Fetch and save transcripts for all videos in a YouTube channel.

    This is the main high-level function for channel transcript fetching.

    Args:
        channel_id: YouTube channel ID.
        output_dir: Directory to save transcript files.
        api_key: YouTube Data API key (optional — titles come from scrapetube).
        fmt: Output format ('md', 'json', 'txt', 'srt').
        languages: List of preferred language codes.
        skip_existing: Skip videos whose transcripts already exist.
        limit: Maximum number of videos to process (0 = all).

    Returns:
        Dict with 'success', 'failed', 'skipped' counts.
    """
    youtube_api = None
    if api_key:
        try:
            from googleapiclient.discovery import build
            youtube_api = build("youtube", "v3", developerKey=api_key)
            logger.info("YouTube Data API client initialized (enhanced title fetching).")
        except Exception as e:
            logger.warning(f"Could not initialize YouTube API client: {e}. Using scrapetube titles.")

    # Get video list
    videos = get_channel_videos(channel_id)
    if videos is None:
        logger.error("Could not retrieve video list.")
        return {"success": 0, "failed": 0, "skipped": 0}
    if not videos:
        logger.info("No videos found for this channel.")
        return {"success": 0, "failed": 0, "skipped": 0}

    # Apply limit
    if limit > 0:
        videos = videos[:limit]

    results = {"success": 0, "failed": 0, "skipped": 0}

    for video in tqdm(videos, desc="Fetching transcripts", unit="video"):
        video_id = video["id"]
        video_url = video["url"]
        title = video.get("title", video_id)

        # Override title with API if available
        if youtube_api:
            api_title = get_video_title_from_api(youtube_api, video_id)
            if api_title:
                title = api_title

        # Skip existing
        if skip_existing and file_already_exists(output_dir, title, fmt):
            logger.info(f"Skipping (already exists): {title}")
            results["skipped"] += 1
            continue

        logger.info(f"Processing: {title} ({video_id})")

        # Fetch transcript
        transcript_data = get_transcript(video_id, languages)
        if transcript_data:
            saved_path = save_transcript(output_dir, title, video_id, video_url, transcript_data, fmt)
            if saved_path:
                results["success"] += 1
            else:
                results["failed"] += 1
        else:
            logger.error(f"No transcript available for: {title} ({video_id})")
            results["failed"] += 1

    logger.info(
        f"Complete — Saved: {results['success']}, "
        f"Failed: {results['failed']}, "
        f"Skipped: {results['skipped']}"
    )
    return results


def fetch_single_video_transcript(
    video_url_or_id,
    output_dir="Transcripts",
    api_key=None,
    fmt="md",
    languages=None,
):
    """
    Fetch and save transcript for a single YouTube video.

    Args:
        video_url_or_id: YouTube video URL or video ID.
        output_dir: Directory to save the transcript file.
        api_key: YouTube Data API key (optional).
        fmt: Output format ('md', 'json', 'txt', 'srt').
        languages: List of preferred language codes.

    Returns:
        Output filepath on success, None on failure.
    """
    video_id = extract_video_id(video_url_or_id)
    if not video_id:
        logger.error(f"Could not extract video ID from: {video_url_or_id}")
        return None

    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # Get title
    title = video_id
    if api_key:
        try:
            from googleapiclient.discovery import build
            youtube_api = build("youtube", "v3", developerKey=api_key)
            api_title = get_video_title_from_api(youtube_api, video_id)
            if api_title:
                title = api_title
        except Exception as e:
            logger.warning(f"Could not fetch title from API: {e}")
    else:
        # Try to get title from scrapetube by fetching video info
        try:
            import scrapetube
            video_info = scrapetube.get_video(video_id)
            if video_info:
                title_obj = video_info.get("title", {})
                if isinstance(title_obj, dict):
                    runs = title_obj.get("runs", [])
                    if runs:
                        title = runs[0].get("text", video_id)
                elif isinstance(title_obj, str):
                    title = title_obj
        except Exception:
            logger.info(f"Using video ID as title: {video_id}")

    # Fetch transcript
    transcript_data = get_transcript(video_id, languages)
    if not transcript_data:
        logger.error(f"No transcript available for video: {video_id}")
        return None

    # Save
    output_path = save_transcript(output_dir, title, video_id, video_url, transcript_data, fmt)
    if output_path:
        logger.info(f"Transcript saved to: {output_path}")
    return output_path
