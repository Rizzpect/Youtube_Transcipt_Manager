"""Shared utility functions for YouTube Transcript Manager."""

import os
import re
import unicodedata
import logging

logger = logging.getLogger(__name__)


def setup_logging(log_file="transcript_fetcher.log", verbose=False):
    """Configure logging with console and file handlers."""
    level = logging.DEBUG if verbose else logging.INFO
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)

    # File handler
    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
    except (OSError, IOError) as e:
        logger.warning(f"Could not create log file '{log_file}': {e}")


def clean_filename(text):
    """
    Clean a string to be suitable for use as a filename.

    Handles Unicode normalization, invalid characters, and length limits.

    Args:
        text: The string to clean.

    Returns:
        A sanitized filename string.
    """
    if not isinstance(text, str) or not text.strip():
        return "untitled"

    # Replace invalid filesystem characters with underscores
    invalid_chars = r'[\\/:*?"<>|]'
    text = re.sub(invalid_chars, "_", text)

    # Normalize Unicode (remove weird spaces and accents)
    try:
        text = unicodedata.normalize("NFKD", text)
        text = text.replace("\xa0", " ")  # Replace non-breaking space
        # Keep only basic ASCII, replace others with '_'
        text = "".join(c if ord(c) < 128 else "_" for c in text)
    except TypeError:
        logger.warning(f"Could not normalize filename: {text}")
        return "untitled"

    # Collapse multiple underscores/spaces
    text = re.sub(r"[_\s]+", " ", text)

    # Remove leading/trailing whitespace, underscores, and periods
    text = text.strip(" ._")

    # Limit length for filesystem compatibility
    max_len = 150
    if len(text) > max_len:
        text = text[:max_len].rsplit(" ", 1)[0]

    return text if text else "untitled"


def format_timestamp(seconds):
    """
    Convert seconds to a human-readable timestamp string.

    Args:
        seconds: Time in seconds (float or int).

    Returns:
        Formatted timestamp string (e.g., '01:23' or '1:01:23').
    """
    seconds = max(0, float(seconds))
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def extract_video_id(url_or_id):
    """
    Extract a YouTube video ID from a URL or return the ID if already valid.

    Supports various YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://youtube.com/shorts/VIDEO_ID
    - Plain VIDEO_ID

    Args:
        url_or_id: A YouTube URL or video ID string.

    Returns:
        The extracted video ID string, or None if invalid.
    """
    if not url_or_id:
        return None

    url_or_id = url_or_id.strip()

    # YouTube URL patterns
    patterns = [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    # Check if it's already a valid video ID (11 chars, alphanumeric + _ -)
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url_or_id):
        return url_or_id

    return None


def get_transcript_files(directory):
    """
    Get all Markdown transcript files in a directory.

    Args:
        directory: Path to the directory to scan.

    Returns:
        List of absolute file paths to .md files.
    """
    if not os.path.isdir(directory):
        logger.error(f"Directory does not exist: {directory}")
        return []

    files = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".md"):
            files.append(os.path.join(directory, filename))
    return files
