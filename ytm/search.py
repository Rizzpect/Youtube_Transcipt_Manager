"""
Keyword search across saved transcript files.

Searches through Markdown transcript files and returns
results with context and timestamps.
"""

import os
import re
import logging

from .utils import get_transcript_files

logger = logging.getLogger(__name__)


def search_transcripts(directory, keyword, case_sensitive=False, context_lines=2, max_results=50):
    """
    Search for a keyword across all transcript files in a directory.

    Args:
        directory: Path to the directory containing transcript .md files.
        keyword: The search term or phrase.
        case_sensitive: Whether the search should be case-sensitive.
        context_lines: Number of surrounding lines to include in results.
        max_results: Maximum number of results to return.

    Returns:
        List of result dicts with keys:
        - 'file': filename
        - 'title': video title (from first line)
        - 'line_number': line number of the match
        - 'line': the matching line content
        - 'context': surrounding lines for context
        - 'timestamp': extracted timestamp if available
    """
    if not keyword or not keyword.strip():
        logger.error("Search keyword cannot be empty.")
        return []

    files = get_transcript_files(directory)
    if not files:
        logger.error(f"No transcript files found in: {directory}")
        return []

    results = []
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(re.escape(keyword), flags)

    logger.info(f"Searching for '{keyword}' in {len(files)} transcript files...")

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Extract title from first line (# Title format)
            title = os.path.basename(filepath).replace(".md", "")
            if lines and lines[0].startswith("# "):
                title = lines[0][2:].strip()

            for i, line in enumerate(lines):
                if pattern.search(line):
                    # Extract timestamp if present
                    timestamp = None
                    ts_match = re.search(r"`(\d{1,2}:\d{2}(?::\d{2})?)`", line)
                    if ts_match:
                        timestamp = ts_match.group(1)

                    # Get context lines
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 1)
                    context = [l.rstrip() for l in lines[start:end]]

                    results.append({
                        "file": os.path.basename(filepath),
                        "title": title,
                        "line_number": i + 1,
                        "line": line.rstrip(),
                        "context": context,
                        "timestamp": timestamp,
                    })

                    if len(results) >= max_results:
                        logger.info(f"Reached max results limit ({max_results}).")
                        return results

        except Exception as e:
            logger.error(f"Error reading file {filepath}: {e}")
            continue

    logger.info(f"Found {len(results)} matches for '{keyword}'.")
    return results


def format_search_results(results, keyword, show_context=True):
    """
    Format search results for terminal display.

    Args:
        results: List of result dicts from search_transcripts().
        keyword: The search keyword (for highlighting).
        show_context: Whether to show surrounding context lines.

    Returns:
        Formatted string for terminal output.
    """
    if not results:
        return f"No results found for '{keyword}'."

    output_lines = []
    output_lines.append(f"\n{'='*60}")
    output_lines.append(f"  Search Results for: '{keyword}'")
    output_lines.append(f"  Found {len(results)} match(es)")
    output_lines.append(f"{'='*60}\n")

    current_file = None
    for i, result in enumerate(results, 1):
        # Group by file
        if result["file"] != current_file:
            current_file = result["file"]
            output_lines.append(f"\n--- {result['title']} ---")
            output_lines.append(f"    File: {result['file']}")

        timestamp_str = f" [{result['timestamp']}]" if result["timestamp"] else ""
        output_lines.append(f"\n  Match #{i} (line {result['line_number']}){timestamp_str}:")

        if show_context and result["context"]:
            for ctx_line in result["context"]:
                marker = ">>>" if keyword.lower() in ctx_line.lower() else "   "
                output_lines.append(f"    {marker} {ctx_line}")
        else:
            output_lines.append(f"    >>> {result['line']}")

    output_lines.append(f"\n{'='*60}\n")
    return "\n".join(output_lines)
