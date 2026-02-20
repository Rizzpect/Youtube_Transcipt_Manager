"""
Legacy entry point for backward compatibility.

This file is kept for users who run `python fetch_transcripts.py` directly.
It launches the interactive mode from the new ytm package.

For full CLI usage, use: python -m ytm
"""

import sys
import os

# Add parent directory to path so ytm package can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ytm.cli import run_interactive
from ytm.utils import setup_logging


def main():
    print("\n⚠️  Note: This script is a legacy wrapper.")
    print("   For full CLI features, use: python -m ytm")
    print("   Run 'python -m ytm --help' to see all commands.\n")
    setup_logging()
    run_interactive()


if __name__ == "__main__":
    main()