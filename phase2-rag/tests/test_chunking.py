"""Chunking is pure logic - fast, free, and a real regression risk."""
import pytest

from rag.chunking import chunk_text


def test_basic_chunking_and_overlap():
    text = "word " * 300                      # ~1500 chars
    chunks = chunk_text(text, 500, 80)
    assert len(chunks) > 1
    assert all(len(c) <= 500 for c in chunks)
    # consecutive chunks must share the overlap window
    assert chunks[0][-80:] == chunks[1][:80]


def test_short_text_is_one_chunk():
    assert chunk_text("hello world", 500, 80) == ["hello world"]


def test_empty_and_whitespace_only():
    assert chunk_text("", 500, 80) == []
    assert chunk_text("   \n  ", 500, 80) == []


def test_whitespace_is_normalized():
    assert chunk_text("a\n\nb   c", 500, 80) == ["a b c"]


def test_overlap_must_be_smaller_than_chunk():
    with pytest.raises(ValueError):
        chunk_text("some text", 80, 80)
