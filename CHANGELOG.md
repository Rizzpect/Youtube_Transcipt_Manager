# Changelog

## [2.0.0] — 2026-02-20

### 🚀 New Features
- **Single Video Fetch** — Fetch transcript for one video URL, not just entire channels
- **Keyword Search** — Search across all saved transcripts with context and timestamps
- **Transcript Combiner** — Merge all transcripts into one file for AI training (Markdown, JSON, or plain text)
- **Export Formats** — Save transcripts as Markdown, JSON, TXT, or SRT (subtitle format)
- **Transcript Statistics** — Word counts, duration estimates, longest/shortest videos
- **Resume Support** — Skip already-downloaded transcripts to avoid re-fetching
- **No API Key Mode** — API key is now optional; video titles come from scrapetube by default
- **Progress Bar** — Visual progress indicator using `tqdm`
- **Multi-language** — Specify preferred transcript language(s)
- **CLI Interface** — Full command-line interface with subcommands: `fetch`, `search`, `combine`, `stats`
- **Interactive Mode** — Guided menu-driven mode (backward compatible with v1)

### 🔧 Improvements
- Restructured into a proper Python package (`ytm/`)
- Fixed `requirements.txt` format (was using `pip install` prefix)
- Added `.gitignore`
- Added `setup.py` for pip installability
- Improved error handling and logging
- Added unit tests for utilities, search, and combiner

### 📝 Documentation
- Complete README rewrite with accurate feature list and usage examples
- Added CHANGELOG

## [1.0.0] — Original

- Basic channel transcript fetching
- Markdown file output
- Interactive input only
