#!/usr/bin/env python3
"""Test cases for Topic Radar JSON parsing improvements."""

import json
import sys
from pathlib import Path

# Add parent to path so we can import topic_radar
sys.path.insert(0, str(Path(__file__).parent))

from topic_radar import extract_json


def test_raw_json():
    """Test parsing raw JSON."""
    raw = '{"assignments": [{"title": "Test", "bucket": "TEST"}], "candidates": []}'
    result = extract_json(raw)
    assert isinstance(result, dict)
    assert "assignments" in result
    print("✓ Raw JSON parsing")


def test_json_with_markdown_fences():
    """Test parsing JSON inside ```json fences."""
    raw = '''```json
{
  "assignments": [{"title": "Test", "bucket": "TEST"}],
  "candidates": []
}
```'''
    result = extract_json(raw)
    assert isinstance(result, dict)
    assert "assignments" in result
    print("✓ JSON with markdown fences")


def test_json_with_trailing_commas():
    """Test parsing JSON with trailing commas before closing braces."""
    raw = '''
{
  "assignments": [
    {"title": "Test", "bucket": "TEST",},
  ],
  "candidates": [],
}
'''
    result = extract_json(raw)
    assert isinstance(result, dict)
    assert "assignments" in result
    print("✓ JSON with trailing commas")


def test_json_with_extra_text_before_and_after():
    """Test parsing JSON with extra text before and after."""
    raw = '''
Here is the JSON response:

{
  "assignments": [{"title": "Test", "bucket": "TEST"}],
  "candidates": []
}

That's all!
'''
    result = extract_json(raw)
    assert isinstance(result, dict)
    assert "assignments" in result
    print("✓ JSON with extra text before/after")


def test_json_with_multiple_issues():
    """Test parsing JSON with multiple issues combined."""
    raw = '''
```json
{
  "assignments": [
    {
      "title": "Test Story",
      "bucket": "AI_FRONTIER",
      "section_slug": "science",
      "section_name": "Science",
      "why_now": "Recent AI announcement",
      "core_question": "How does this matter?",
      "angle": "Report angle",
      "source_urls": ["https://example.com",],
      "tags": ["ai", "tech",],
    },
  ],
  "candidates": [
    {"title": "Another", "bucket": "WEIRD_BUT_REAL",},
  ],
}
```

Some commentary about the response.
'''
    result = extract_json(raw)
    assert isinstance(result, dict)
    assert "assignments" in result
    assert len(result["assignments"]) == 1
    assert result["assignments"][0]["title"] == "Test Story"
    print("✓ JSON with multiple issues combined")


def test_json_with_nested_arrays():
    """Test parsing JSON with nested arrays and objects."""
    raw = '''
{
  "candidates": [
    {
      "title": "Story 1",
      "source_urls": ["https://a.com", "https://b.com",],
      "tags": ["tag1", "tag2",],
    },
    {
      "title": "Story 2",
      "source_urls": [],
    },
  ],
  "assignments": [],
}
'''
    result = extract_json(raw)
    assert isinstance(result, dict)
    assert len(result["candidates"]) == 2
    assert result["candidates"][0]["source_urls"] == ["https://a.com", "https://b.com"]
    print("✓ JSON with nested arrays")


def test_empty_response_raises():
    """Test that empty response raises an error."""
    try:
        extract_json("")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "empty" in str(e).lower()
        print("✓ Empty response raises ValueError")


def test_no_json_object_raises():
    """Test that response without JSON object raises an error."""
    try:
        extract_json("Just some text with no JSON at all")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "no json object" in str(e).lower()
        print("✓ No JSON object raises ValueError")


def test_invalid_json_raises():
    """Test that invalid JSON raises an error with helpful message."""
    try:
        extract_json('{"key": "value" invalid}')
        assert False, "Should have raised JSONDecodeError"
    except json.JSONDecodeError as e:
        # Error message should include context
        assert "parse error" in str(e).lower() or "snippet" in str(e).lower()
        print("✓ Invalid JSON raises helpful JSONDecodeError")


def main():
    """Run all tests."""
    print("Running Topic Radar JSON parsing tests...\n")
    
    test_raw_json()
    test_json_with_markdown_fences()
    test_json_with_trailing_commas()
    test_json_with_extra_text_before_and_after()
    test_json_with_multiple_issues()
    test_json_with_nested_arrays()
    test_empty_response_raises()
    test_no_json_object_raises()
    test_invalid_json_raises()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()
