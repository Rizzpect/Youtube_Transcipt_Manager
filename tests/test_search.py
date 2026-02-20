"""Unit tests for ytm.search module."""

import os
import tempfile
import pytest
from ytm.search import search_transcripts, format_search_results


@pytest.fixture
def sample_transcripts(tmp_path):
    """Create sample transcript files for testing."""
    # Create a sample transcript
    transcript1 = tmp_path / "Video About Machine Learning.md"
    transcript1.write_text(
        "# Video About Machine Learning\n\n"
        "**Video URL:** https://www.youtube.com/watch?v=test123\n\n"
        "## Transcript\n\n"
        "`00:00` — Welcome to this video about machine learning.\n"
        "`00:15` — Today we'll discuss neural networks.\n"
        "`00:30` — Deep learning is a subset of machine learning.\n"
        "`01:00` — Let's talk about training data.\n"
        "`01:30` — Thank you for watching.\n",
        encoding="utf-8",
    )

    # Create another transcript
    transcript2 = tmp_path / "Python Programming Tutorial.md"
    transcript2.write_text(
        "# Python Programming Tutorial\n\n"
        "**Video URL:** https://www.youtube.com/watch?v=test456\n\n"
        "## Transcript\n\n"
        "`00:00` — Welcome to Python programming.\n"
        "`00:20` — Python is great for machine learning.\n"
        "`00:45` — Let's write some code today.\n"
        "`01:10` — Functions are important in Python.\n",
        encoding="utf-8",
    )

    return tmp_path


class TestSearchTranscripts:
    """Tests for the search_transcripts function."""

    def test_basic_search(self, sample_transcripts):
        results = search_transcripts(sample_transcripts, "machine learning")
        assert len(results) > 0
        assert any("machine learning" in r["line"].lower() for r in results)

    def test_case_insensitive(self, sample_transcripts):
        results = search_transcripts(sample_transcripts, "MACHINE LEARNING")
        assert len(results) > 0

    def test_case_sensitive(self, sample_transcripts):
        results = search_transcripts(
            sample_transcripts, "MACHINE LEARNING", case_sensitive=True
        )
        assert len(results) == 0

    def test_no_results(self, sample_transcripts):
        results = search_transcripts(sample_transcripts, "quantum computing")
        assert len(results) == 0

    def test_empty_keyword(self, sample_transcripts):
        results = search_transcripts(sample_transcripts, "")
        assert len(results) == 0

    def test_timestamp_extraction(self, sample_transcripts):
        results = search_transcripts(sample_transcripts, "neural networks")
        assert len(results) > 0
        assert results[0]["timestamp"] is not None

    def test_max_results(self, sample_transcripts):
        results = search_transcripts(sample_transcripts, "a", max_results=3)
        assert len(results) <= 3

    def test_context_lines(self, sample_transcripts):
        results = search_transcripts(
            sample_transcripts, "neural networks", context_lines=1
        )
        assert len(results) > 0
        assert len(results[0]["context"]) >= 1

    def test_invalid_directory(self):
        results = search_transcripts("/nonexistent/path", "test")
        assert len(results) == 0

    def test_cross_file_search(self, sample_transcripts):
        """Keyword that appears in both files."""
        results = search_transcripts(sample_transcripts, "machine learning")
        files = set(r["file"] for r in results)
        assert len(files) == 2  # Should find in both files


class TestFormatSearchResults:
    """Tests for the format_search_results function."""

    def test_no_results(self):
        output = format_search_results([], "test")
        assert "No results found" in output

    def test_with_results(self, sample_transcripts):
        results = search_transcripts(sample_transcripts, "Python")
        output = format_search_results(results, "Python")
        assert "Python" in output
        assert "Match #" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
