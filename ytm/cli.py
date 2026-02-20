"""
Command-line interface for YouTube Transcript Manager.

Supports subcommands: fetch, search, combine, stats.
Falls back to interactive mode if no arguments are provided.
"""

import sys
import argparse
import logging

from . import __version__
from .utils import setup_logging

logger = logging.getLogger(__name__)


def create_parser():
    """Create the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="ytm",
        description="YouTube Transcript Manager — Fetch, search, and organize YouTube transcripts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s fetch --channel UCsXVk37bltHxD1rDPwtNM8Q
  %(prog)s fetch --video https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s search "machine learning" --dir Transcripts
  %(prog)s combine --dir Transcripts --format json
  %(prog)s stats --dir Transcripts
  %(prog)s interactive
        """,
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose (debug) logging."
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- fetch subcommand ---
    fetch_parser = subparsers.add_parser(
        "fetch", help="Fetch transcripts from YouTube."
    )
    fetch_group = fetch_parser.add_mutually_exclusive_group(required=True)
    fetch_group.add_argument(
        "--channel", "-c", type=str, help="YouTube channel ID to fetch all videos from."
    )
    fetch_group.add_argument(
        "--video", "-V", type=str, help="Single YouTube video URL or ID."
    )
    fetch_parser.add_argument(
        "--output", "-o", type=str, default="Transcripts",
        help="Output directory for transcript files (default: Transcripts)."
    )
    fetch_parser.add_argument(
        "--format", "-f", type=str, default="md", choices=["md", "json", "txt", "srt"],
        help="Output format (default: md)."
    )
    fetch_parser.add_argument(
        "--language", "-l", type=str, nargs="+", default=["en"],
        help="Preferred transcript language(s) (default: en)."
    )
    fetch_parser.add_argument(
        "--api-key", type=str, default=None,
        help="YouTube Data API key (optional — enhances title accuracy)."
    )
    fetch_parser.add_argument(
        "--no-skip", action="store_true",
        help="Re-download transcripts even if they already exist."
    )
    fetch_parser.add_argument(
        "--limit", type=int, default=0,
        help="Max number of videos to process (0 = all, default: 0)."
    )

    # --- search subcommand ---
    search_parser = subparsers.add_parser(
        "search", help="Search for keywords across saved transcripts."
    )
    search_parser.add_argument(
        "keyword", type=str, help="Keyword or phrase to search for."
    )
    search_parser.add_argument(
        "--dir", "-d", type=str, default="Transcripts",
        help="Directory containing transcript files (default: Transcripts)."
    )
    search_parser.add_argument(
        "--case-sensitive", action="store_true",
        help="Enable case-sensitive search."
    )
    search_parser.add_argument(
        "--context", type=int, default=2,
        help="Number of surrounding context lines (default: 2)."
    )
    search_parser.add_argument(
        "--max-results", type=int, default=50,
        help="Maximum number of results (default: 50)."
    )

    # --- combine subcommand ---
    combine_parser = subparsers.add_parser(
        "combine", help="Combine all transcripts into a single file."
    )
    combine_parser.add_argument(
        "--dir", "-d", type=str, default="Transcripts",
        help="Directory containing transcript files (default: Transcripts)."
    )
    combine_parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Output file path (default: auto-generated in transcript dir)."
    )
    combine_parser.add_argument(
        "--format", "-f", type=str, default="md", choices=["md", "json", "txt"],
        help="Output format (default: md)."
    )

    # --- stats subcommand ---
    stats_parser = subparsers.add_parser(
        "stats", help="Show statistics for saved transcripts."
    )
    stats_parser.add_argument(
        "--dir", "-d", type=str, default="Transcripts",
        help="Directory containing transcript files (default: Transcripts)."
    )

    # --- interactive subcommand ---
    subparsers.add_parser(
        "interactive", help="Run in interactive mode (guided prompts)."
    )

    return parser


def run_fetch(args):
    """Execute the fetch command."""
    from .fetcher import fetch_channel_transcripts, fetch_single_video_transcript

    if args.video:
        result = fetch_single_video_transcript(
            video_url_or_id=args.video,
            output_dir=args.output,
            api_key=args.api_key,
            fmt=args.format,
            languages=args.language,
        )
        if result:
            print(f"\n✅ Transcript saved to: {result}")
        else:
            print("\n❌ Failed to fetch transcript.")
            sys.exit(1)
    else:
        results = fetch_channel_transcripts(
            channel_id=args.channel,
            output_dir=args.output,
            api_key=args.api_key,
            fmt=args.format,
            languages=args.language,
            skip_existing=not args.no_skip,
            limit=args.limit,
        )
        print(f"\n✅ Fetch complete — Saved: {results['success']}, "
              f"Failed: {results['failed']}, Skipped: {results['skipped']}")


def run_search(args):
    """Execute the search command."""
    from .search import search_transcripts, format_search_results

    results = search_transcripts(
        directory=args.dir,
        keyword=args.keyword,
        case_sensitive=args.case_sensitive,
        context_lines=args.context,
        max_results=args.max_results,
    )
    print(format_search_results(results, args.keyword))


def run_combine(args):
    """Execute the combine command."""
    from .combiner import combine_transcripts

    result = combine_transcripts(
        directory=args.dir,
        output_file=args.output,
        fmt=args.format,
    )
    if result:
        print(f"\n✅ Combined transcripts saved to: {result}")
    else:
        print("\n❌ Failed to combine transcripts.")
        sys.exit(1)


def run_stats(args):
    """Execute the stats command."""
    from .stats import get_stats, format_stats

    stats = get_stats(directory=args.dir)
    if stats:
        print(format_stats(stats))
    else:
        print("\n❌ No transcripts found to analyze.")
        sys.exit(1)


def run_interactive():
    """Run the interactive mode with guided prompts."""
    from .fetcher import fetch_channel_transcripts, fetch_single_video_transcript
    from .search import search_transcripts, format_search_results
    from .combiner import combine_transcripts
    from .stats import get_stats, format_stats

    print("\n" + "=" * 60)
    print("  🎥 YouTube Transcript Manager — Interactive Mode")
    print("=" * 60 + "\n")

    while True:
        print("What would you like to do?\n")
        print("  1. Fetch transcripts for a YouTube channel")
        print("  2. Fetch transcript for a single video")
        print("  3. Search across saved transcripts")
        print("  4. Combine transcripts into a single file")
        print("  5. View transcript statistics")
        print("  6. Exit\n")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            channel_id = input("Enter YouTube Channel ID: ").strip()
            if not channel_id:
                print("❌ Channel ID cannot be empty.\n")
                continue
            output_dir = input("Output directory (default: Transcripts): ").strip() or "Transcripts"
            api_key = input("YouTube API key (press Enter to skip): ").strip() or None
            fmt = input("Format — md/json/txt/srt (default: md): ").strip() or "md"
            lang = input("Language (default: en): ").strip() or "en"

            results = fetch_channel_transcripts(
                channel_id=channel_id,
                output_dir=output_dir,
                api_key=api_key,
                fmt=fmt,
                languages=[lang],
            )
            print(f"\n✅ Done — Saved: {results['success']}, "
                  f"Failed: {results['failed']}, Skipped: {results['skipped']}\n")

        elif choice == "2":
            video_url = input("Enter YouTube video URL or ID: ").strip()
            if not video_url:
                print("❌ Video URL cannot be empty.\n")
                continue
            output_dir = input("Output directory (default: Transcripts): ").strip() or "Transcripts"
            api_key = input("YouTube API key (press Enter to skip): ").strip() or None
            fmt = input("Format — md/json/txt/srt (default: md): ").strip() or "md"
            lang = input("Language (default: en): ").strip() or "en"

            result = fetch_single_video_transcript(
                video_url_or_id=video_url,
                output_dir=output_dir,
                api_key=api_key,
                fmt=fmt,
                languages=[lang],
            )
            if result:
                print(f"\n✅ Transcript saved to: {result}\n")
            else:
                print("\n❌ Failed to fetch transcript.\n")

        elif choice == "3":
            keyword = input("Enter search keyword: ").strip()
            if not keyword:
                print("❌ Keyword cannot be empty.\n")
                continue
            directory = input("Transcript directory (default: Transcripts): ").strip() or "Transcripts"
            results = search_transcripts(directory=directory, keyword=keyword)
            print(format_search_results(results, keyword))

        elif choice == "4":
            directory = input("Transcript directory (default: Transcripts): ").strip() or "Transcripts"
            fmt = input("Format — md/json/txt (default: md): ").strip() or "md"
            result = combine_transcripts(directory=directory, fmt=fmt)
            if result:
                print(f"\n✅ Combined transcripts saved to: {result}\n")
            else:
                print("\n❌ Failed to combine transcripts.\n")

        elif choice == "5":
            directory = input("Transcript directory (default: Transcripts): ").strip() or "Transcripts"
            stats = get_stats(directory=directory)
            if stats:
                print(format_stats(stats))
            else:
                print("\n❌ No transcripts found.\n")

        elif choice == "6":
            print("Goodbye! 👋")
            break

        else:
            print("❌ Invalid choice. Please enter 1-6.\n")


def main():
    """Main entry point — runs CLI or falls back to interactive mode."""
    parser = create_parser()

    # If no arguments, launch interactive mode
    if len(sys.argv) == 1:
        setup_logging(verbose=False)
        run_interactive()
        return

    args = parser.parse_args()
    setup_logging(verbose=getattr(args, "verbose", False))

    if args.command == "fetch":
        run_fetch(args)
    elif args.command == "search":
        run_search(args)
    elif args.command == "combine":
        run_combine(args)
    elif args.command == "stats":
        run_stats(args)
    elif args.command == "interactive":
        run_interactive()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
