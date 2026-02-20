# 🎥 YouTube Transcript Manager

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A powerful tool to **fetch, search, organize, and manage** YouTube video transcripts. Designed for content creators, researchers, and anyone building AI-powered knowledge bases.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **📥 Channel Fetch** | Fetch transcripts for all videos in a YouTube channel |
| **🎯 Single Video** | Fetch transcript for a single YouTube video URL |
| **🔍 Keyword Search** | Search across all saved transcripts with context and timestamps |
| **📦 Combine** | Merge all transcripts into a single file for AI training |
| **📊 Statistics** | Word counts, durations, and video analytics |
| **💾 Multi-Format** | Export as Markdown, JSON, TXT, or SRT subtitles |
| **⏩ Resume Support** | Skip already-downloaded transcripts |
| **🌍 Multi-Language** | Specify preferred transcript languages |
| **📈 Progress Bar** | Visual progress for long-running operations |

---

## 🚀 Installation

```bash
git clone https://github.com/Rizzpect/Youtube_Transcipt_Manager.git
cd Youtube_Transcipt_Manager
pip install -r requirements.txt
```

**Optional:** Install as a package for the `ytm` command:
```bash
pip install -e .
```

### Dependencies

- [`scrapetube`](https://github.com/dermasmid/scrapetube) — Scrape YouTube channel videos (no API key needed)
- [`youtube-transcript-api`](https://github.com/jdepoix/youtube-transcript-api) — Fetch video transcripts
- [`google-api-python-client`](https://github.com/googleapis/google-api-python-client) — YouTube Data API (optional, for enhanced title accuracy)
- [`tqdm`](https://github.com/tqdm/tqdm) — Progress bars

---

## 📖 Usage

### CLI Mode (Recommended)

The tool supports powerful CLI commands:

```bash
# Fetch all transcripts for a channel
python -m ytm fetch --channel UCsXVk37bltHxD1rDPwtNM8Q

# Fetch a single video transcript
python -m ytm fetch --video https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Fetch in JSON format with Spanish language preference
python -m ytm fetch --channel UC_CHANNEL_ID --format json --language es

# Search for a keyword across all transcripts
python -m ytm search "machine learning" --dir Transcripts

# Combine all transcripts into one file (great for AI training)
python -m ytm combine --dir Transcripts --format txt

# View transcript statistics
python -m ytm stats --dir Transcripts
```

### Interactive Mode

If you prefer a guided menu, simply run without arguments:

```bash
python -m ytm
```

Or use the legacy script:

```bash
python fetch_transcripts.py
```

### API Key (Optional)

By default, video titles are extracted from **scrapetube** — no API key is required. However, if you want enhanced title accuracy, you can provide a **YouTube Data API v3** key:

```bash
python -m ytm fetch --channel UCsXVk37bltHxD1rDPwtNM8Q --api-key YOUR_API_KEY
```

To get an API key:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable the **YouTube Data API v3**
3. Generate an API key under **Credentials**

---

## 📁 Output Formats

| Format | Extension | Best For |
|--------|-----------|----------|
| **Markdown** | `.md` | Obsidian, Notion, note-taking |
| **JSON** | `.json` | Programmatic access, AI training |
| **Text** | `.txt` | Plain text analysis, LLM input |
| **SRT** | `.srt` | Subtitles, video editing |

---

## 🔍 Keyword Search

Search across all your saved transcripts with context:

```bash
python -m ytm search "neural networks" --dir Transcripts --context 3
```

Output:
```
============================================================
  Search Results for: 'neural networks'
  Found 5 match(es)
============================================================

--- Deep Learning Fundamentals ---
    File: Deep Learning Fundamentals.md

  Match #1 (line 12) [05:23]:
       `05:15` — ...the basics of deep learning...
    >>> `05:23` — Today we'll discuss neural networks in detail.
       `05:40` — Starting with perceptrons...
```

---

## 📊 Statistics

Get a quick overview of your transcript library:

```bash
python -m ytm stats --dir Transcripts
```

```
============================================================
  Transcript Statistics
============================================================

  Total transcript files:     42
  Total words:                385,210
  Total transcript entries:   18,432
  Average words per video:    9,172
  Estimated total duration:   32.5 hours

  Longest transcript:  5-Hour Masterclass on AI
                       (45,230 words)
  Shortest transcript: Quick Tips #7
                       (892 words)
```

---

## 🧪 Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## 📑 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## 🤝 Acknowledgments

- [jdepoix](https://github.com/jdepoix) for creating [`youtube-transcript-api`](https://github.com/jdepoix/youtube-transcript-api)
- [dermasmid](https://github.com/dermasmid) for [`scrapetube`](https://github.com/dermasmid/scrapetube)

## 📧 Contact

For questions or suggestions, feel free to open an [issue](https://github.com/Rizzpect/Youtube_Transcipt_Manager/issues).
