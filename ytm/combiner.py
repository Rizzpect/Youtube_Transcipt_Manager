"""
Transcript combiner — merge transcript files into a single output.

Useful for AI training data preparation and bulk analysis.
"""

import os
import json
import logging

from .utils import get_transcript_files

logger = logging.getLogger(__name__)


def combine_transcripts(directory, output_file=None, fmt="md"):
    """
    Combine all transcript files in a directory into a single file.

    Args:
        directory: Path to the directory containing transcript .md files.
        output_file: Output file path. If None, auto-generated.
        fmt: Output format — 'md' (Markdown), 'json' (JSON), or 'txt' (plain text).

    Returns:
        Output file path on success, None on failure.
    """
    files = get_transcript_files(directory)
    if not files:
        logger.error(f"No transcript files found in: {directory}")
        return None

    if not output_file:
        extension = fmt if fmt in ("md", "json", "txt") else "md"
        output_file = os.path.join(directory, f"_combined_transcripts.{extension}")

    logger.info(f"Combining {len(files)} transcript files into: {output_file}")

    try:
        if fmt == "json":
            return _combine_as_json(files, output_file)
        elif fmt == "txt":
            return _combine_as_text(files, output_file)
        else:
            return _combine_as_markdown(files, output_file)
    except Exception as e:
        logger.error(f"Failed to combine transcripts: {e}")
        return None


def _combine_as_markdown(files, output_file):
    """Combine transcripts into a single Markdown file."""
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("# Combined Transcripts\n\n")
        out.write(f"**Total videos:** {len(files)}\n\n")
        out.write("---\n\n")

        for filepath in files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                out.write(content)
                out.write("\n\n---\n\n")
            except Exception as e:
                logger.error(f"Error reading {filepath}: {e}")

    logger.info(f"Combined Markdown saved to: {output_file}")
    return output_file


def _combine_as_json(files, output_file):
    """Combine transcripts into a single JSON file."""
    combined = {"total_videos": len(files), "transcripts": []}

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Parse the Markdown transcript
            title = os.path.basename(filepath).replace(".md", "")
            video_url = ""
            entries = []

            for line in lines:
                line = line.strip()
                if line.startswith("# "):
                    title = line[2:]
                elif line.startswith("**Video URL:**"):
                    # Extract URL from markdown link or plain text
                    url_start = line.find("http")
                    if url_start != -1:
                        url_end = line.find(")", url_start)
                        if url_end == -1:
                            url_end = len(line)
                        video_url = line[url_start:url_end]
                elif line.startswith("`") and "` — " in line:
                    parts = line.split("` — ", 1)
                    if len(parts) == 2:
                        timestamp = parts[0].strip("`")
                        text = parts[1].strip()
                        entries.append({"timestamp": timestamp, "text": text})
                elif line.startswith("`") and "` - " in line:
                    parts = line.split("` - ", 1)
                    if len(parts) == 2:
                        timestamp = parts[0].strip("`")
                        text = parts[1].strip()
                        entries.append({"timestamp": timestamp, "text": text})

            combined["transcripts"].append({
                "title": title,
                "video_url": video_url,
                "entries": entries,
            })

        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(combined, out, indent=2, ensure_ascii=False)

    logger.info(f"Combined JSON saved to: {output_file}")
    return output_file


def _combine_as_text(files, output_file):
    """Combine transcripts into a single plain text file (ideal for AI training)."""
    with open(output_file, "w", encoding="utf-8") as out:
        for filepath in files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                # Extract title
                title = os.path.basename(filepath).replace(".md", "")
                for line in lines:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break

                out.write(f"\n\n=== {title} ===\n\n")

                # Extract just the transcript text (no timestamps)
                for line in lines:
                    line = line.strip()
                    if line.startswith("`") and ("` — " in line or "` - " in line):
                        sep = "` — " if "` — " in line else "` - "
                        parts = line.split(sep, 1)
                        if len(parts) == 2:
                            out.write(parts[1].strip() + " ")

                out.write("\n")

            except Exception as e:
                logger.error(f"Error reading {filepath}: {e}")

    logger.info(f"Combined text saved to: {output_file}")
    return output_file
