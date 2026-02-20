"""Unit tests for ytm.utils module."""

import pytest
from ytm.utils import clean_filename, format_timestamp, extract_video_id


class TestCleanFilename:
    """Tests for the clean_filename function."""

    def test_basic_title(self):
        assert clean_filename("Hello World") == "Hello World"

    def test_invalid_characters(self):
        result = clean_filename('Test: Video | "Best" <Ever>')
        assert ":" not in result
        assert "|" not in result
        assert '"' not in result
        assert "<" not in result
        assert ">" not in result

    def test_unicode_normalization(self):
        result = clean_filename("Café résumé")
        assert all(ord(c) < 128 for c in result)

    def test_empty_string(self):
        assert clean_filename("") == "untitled"
        assert clean_filename("   ") == "untitled"
        assert clean_filename(None) == "untitled"

    def test_long_filename(self):
        long_title = "A" * 200
        result = clean_filename(long_title)
        assert len(result) <= 150

    def test_non_breaking_space(self):
        result = clean_filename("Hello\xa0World")
        assert "\xa0" not in result

    def test_leading_trailing_cleanup(self):
        result = clean_filename("  .._test title_..  ")
        assert not result.startswith(" ")
        assert not result.startswith(".")
        assert not result.endswith(" ")
        assert not result.endswith(".")

    def test_slashes(self):
        result = clean_filename("path/to\\file")
        assert "/" not in result
        assert "\\" not in result


class TestFormatTimestamp:
    """Tests for the format_timestamp function."""

    def test_zero(self):
        assert format_timestamp(0) == "00:00"

    def test_seconds_only(self):
        assert format_timestamp(45) == "00:45"

    def test_minutes_and_seconds(self):
        assert format_timestamp(125) == "02:05"

    def test_hours(self):
        assert format_timestamp(3665) == "1:01:05"

    def test_negative(self):
        assert format_timestamp(-10) == "00:00"

    def test_float(self):
        assert format_timestamp(90.7) == "01:30"


class TestExtractVideoId:
    """Tests for the extract_video_id function."""

    def test_standard_url(self):
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_short_url(self):
        assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_embed_url(self):
        assert extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_shorts_url(self):
        assert extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_plain_id(self):
        assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_url_with_params(self):
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120") == "dQw4w9WgXcQ"

    def test_invalid(self):
        assert extract_video_id("not_a_url") is None
        assert extract_video_id("") is None
        assert extract_video_id(None) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
