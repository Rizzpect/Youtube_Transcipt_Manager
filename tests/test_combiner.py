"""Unit tests for ytm.combiner module."""

import os
import json
import pytest
from ytm.combiner import combine_transcripts


@pytest.fixture
def sample_transcripts(tmp_path):
    """Create sample transcript files for testing."""
    transcript1 = tmp_path / "First Video.md"
    transcript1.write_text(
        "# First Video Title\n\n"
        "**Video URL:** https://www.youtube.com/watch?v=abc123\n\n"
        "## Transcript\n\n"
        "`00:00` — Hello world.\n"
        "`00:10` — This is the first video.\n",
        encoding="utf-8",
    )

    transcript2 = tmp_path / "Second Video.md"
    transcript2.write_text(
        "# Second Video Title\n\n"
        "**Video URL:** https://www.youtube.com/watch?v=def456\n\n"
        "## Transcript\n\n"
        "`00:00` — Welcome back.\n"
        "`00:15` — This is video number two.\n",
        encoding="utf-8",
    )

    return tmp_path


class TestCombineTranscripts:
    """Tests for the combine_transcripts function."""

    def test_combine_markdown(self, sample_transcripts):
        result = combine_transcripts(sample_transcripts, fmt="md")
        assert result is not None
        assert os.path.exists(result)

        with open(result, "r", encoding="utf-8") as f:
            content = f.read()
        assert "First Video Title" in content
        assert "Second Video Title" in content
        assert "Combined Transcripts" in content

    def test_combine_json(self, sample_transcripts):
        result = combine_transcripts(sample_transcripts, fmt="json")
        assert result is not None
        assert os.path.exists(result)

        with open(result, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["total_videos"] == 2
        assert len(data["transcripts"]) == 2

    def test_combine_text(self, sample_transcripts):
        result = combine_transcripts(sample_transcripts, fmt="txt")
        assert result is not None
        assert os.path.exists(result)

        with open(result, "r", encoding="utf-8") as f:
            content = f.read()
        assert "First Video Title" in content
        assert "Hello world." in content

    def test_custom_output_path(self, sample_transcripts, tmp_path):
        output_file = str(tmp_path / "custom_output.md")
        result = combine_transcripts(sample_transcripts, output_file=output_file, fmt="md")
        assert result == output_file
        assert os.path.exists(output_file)

    def test_empty_directory(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        result = combine_transcripts(str(empty_dir))
        assert result is None

    def test_nonexistent_directory(self):
        result = combine_transcripts("/nonexistent/path")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
