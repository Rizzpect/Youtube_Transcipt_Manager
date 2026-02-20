"""
Transcript statistics and analytics.

Provides word counts, duration estimates, and other
useful metrics about saved transcripts.
"""

import os
import re
import logging

from .utils import get_transcript_files

logger = logging.getLogger(__name__)


def get_stats(directory):
    """
    Calculate statistics for all transcript files in a directory.

    Args:
        directory: Path to the directory containing transcript .md files.

    Returns:
        Dict with statistics:
        - 'total_files': number of transcript files
        - 'total_words': total word count across all transcripts
        - 'total_entries': total number of transcript entries
        - 'avg_words_per_video': average words per video
        - 'longest_video': dict with 'title' and 'words'
        - 'shortest_video': dict with 'title' and 'words'
        - 'per_file': list of per-file stats
    """
    files = get_transcript_files(directory)
    if not files:
        logger.error(f"No transcript files found in: {directory}")
        return None

    per_file_stats = []
    total_words = 0
    total_entries = 0

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            title = os.path.basename(filepath).replace(".md", "")
            word_count = 0
            entry_count = 0
            last_timestamp_seconds = 0

            for line in lines:
                stripped = line.strip()
                if stripped.startswith("# "):
                    title = stripped[2:]

                # Count transcript entries (lines with timestamps)
                if stripped.startswith("`") and ("` — " in stripped or "` - " in stripped):
                    entry_count += 1
                    sep = "` — " if "` — " in stripped else "` - "
                    parts = stripped.split(sep, 1)
                    if len(parts) == 2:
                        text = parts[1].strip()
                        word_count += len(text.split())

                    # Extract timestamp for duration estimate
                    ts_match = re.search(r"`(\d{1,2}):(\d{2})(?::(\d{2}))?`", stripped)
                    if ts_match:
                        hours_or_mins = int(ts_match.group(1))
                        mins_or_secs = int(ts_match.group(2))
                        secs = int(ts_match.group(3)) if ts_match.group(3) else 0
                        if ts_match.group(3):  # H:MM:SS format
                            total_secs = hours_or_mins * 3600 + mins_or_secs * 60 + secs
                        else:  # MM:SS format
                            total_secs = hours_or_mins * 60 + mins_or_secs
                        last_timestamp_seconds = max(last_timestamp_seconds, total_secs)

            file_stat = {
                "file": os.path.basename(filepath),
                "title": title,
                "words": word_count,
                "entries": entry_count,
                "estimated_duration_minutes": round(last_timestamp_seconds / 60, 1),
            }
            per_file_stats.append(file_stat)
            total_words += word_count
            total_entries += entry_count

        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")

    total_files = len(per_file_stats)
    avg_words = round(total_words / total_files) if total_files > 0 else 0

    # Find longest and shortest
    sorted_by_words = sorted(per_file_stats, key=lambda x: x["words"], reverse=True)
    longest = sorted_by_words[0] if sorted_by_words else None
    shortest = sorted_by_words[-1] if sorted_by_words else None

    total_duration = sum(s["estimated_duration_minutes"] for s in per_file_stats)

    return {
        "total_files": total_files,
        "total_words": total_words,
        "total_entries": total_entries,
        "avg_words_per_video": avg_words,
        "total_estimated_duration_hours": round(total_duration / 60, 1),
        "longest_video": {"title": longest["title"], "words": longest["words"]} if longest else None,
        "shortest_video": {"title": shortest["title"], "words": shortest["words"]} if shortest else None,
        "per_file": per_file_stats,
    }


def format_stats(stats):
    """
    Format statistics for terminal display.

    Args:
        stats: Dict from get_stats().

    Returns:
        Formatted string for terminal output.
    """
    if not stats:
        return "No statistics available."

    lines = []
    lines.append(f"\n{'='*60}")
    lines.append("  Transcript Statistics")
    lines.append(f"{'='*60}\n")
    lines.append(f"  Total transcript files:     {stats['total_files']}")
    lines.append(f"  Total words:                {stats['total_words']:,}")
    lines.append(f"  Total transcript entries:   {stats['total_entries']:,}")
    lines.append(f"  Average words per video:    {stats['avg_words_per_video']:,}")
    lines.append(f"  Estimated total duration:   {stats['total_estimated_duration_hours']} hours")

    if stats["longest_video"]:
        lines.append(f"\n  Longest transcript:  {stats['longest_video']['title']}")
        lines.append(f"                       ({stats['longest_video']['words']:,} words)")
    if stats["shortest_video"]:
        lines.append(f"  Shortest transcript: {stats['shortest_video']['title']}")
        lines.append(f"                       ({stats['shortest_video']['words']:,} words)")

    lines.append(f"\n{'='*60}\n")
    return "\n".join(lines)
