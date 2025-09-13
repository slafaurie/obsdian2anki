import pytest
from src.obsidian2anki import _match_tag_pattern

def test_basic_tag_match():
    """Test basic exact tag match in a simple sentence."""
    assert _match_tag_pattern("#anki/export", "This note has #anki/export tag")

def test_standalone_tag():
    """Test tag without any surrounding text."""
    assert _match_tag_pattern("#anki/export", "#anki/export")

def test_tag_with_newlines():
    """Test tag with surrounding newlines."""
    assert _match_tag_pattern("#anki/export", "\n#anki/export\n")

def test_tag_in_multiple_tags():
    """Test finding tag among other tags."""
    assert _match_tag_pattern("#anki/export", "Multiple #tags #anki/export #other/tag")

def test_reject_tag_as_substring():
    """Test cases where tag is part of a larger string."""
    cases = [
        "This has #anki/export/extra",  # Extra path component
        "This has #anki/export2",       # Extra number
        "Wrong#anki/export",            # No space before
        "#anki/exportextra"            # Extra text without separator
    ]
    for case in cases:
        assert not _match_tag_pattern("#anki/export", case)

def test_case_sensitivity():
    """Test that tags are case sensitive."""
    assert not _match_tag_pattern("#anki/export", "#Anki/Export")

def test_tag_at_different_positions():
    """Test tag matching at start, middle, and end of text."""
    assert _match_tag_pattern("#anki/export", "#anki/export at start")
    assert _match_tag_pattern("#anki/export", "middle #anki/export here")
    assert _match_tag_pattern("#anki/export", "at end #anki/export")