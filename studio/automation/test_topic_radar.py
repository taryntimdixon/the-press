#!/usr/bin/env python3
"""Test cases for Topic Radar JSON parsing improvements."""

import json
import sys
from io import StringIO
from tempfile import TemporaryDirectory
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import patch

# Add parent to path so we can import topic_radar
sys.path.insert(0, str(Path(__file__).parent))

from topic_radar import build_issue_plan, extract_json


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


def _allowed_sections() -> list[tuple[str, str]]:
    return [
        ("world", "World"),
        ("science", "Science"),
        ("culture", "Culture"),
    ]


def _candidate(title: str) -> dict:
    return {
        "title": title,
        "bucket": "AI_FRONTIER",
        "section_slug": "science",
        "section_name": "Science",
        "why_now": "Fresh, high-signal development with clear stakes.",
        "core_question": "What changed and why does it matter now?",
        "angle": "Lead with concrete actors and measurable implications.",
        "source_urls": ["https://example.com/story"],
        "score": 4.2,
    }


def _run_build_issue_plan(payload: dict, story_count: int = 1, strict_story_count: bool = False) -> list[dict]:
    with TemporaryDirectory() as tmp:
        env = {"TOPIC_RADAR_STRICT_STORY_COUNT": "1" if strict_story_count else "0"}
        with patch.dict("os.environ", env, clear=False), patch(
            "topic_radar.topic_radar_enabled", return_value=True
        ), patch("topic_radar.topic_radar_required", return_value=True), patch(
            "topic_radar.request_topic_payload", return_value=payload
        ):
            return build_issue_plan(
                client=object(),
                story_count=story_count,
                date_label="2026-04-27",
                edition_date="2026-04-27",
                recent_memory=[],
                allowed_sections=_allowed_sections(),
                root=Path(tmp),
            )


def test_build_issue_plan_with_assignments():
    """Topic radar should accept payloads with normal assignments."""
    payload = {
        "assignments": [_candidate("Assignment Story")],
        "candidates": [_candidate("Candidate Backup")],
    }
    plan = _run_build_issue_plan(payload)
    assert len(plan) == 1
    assert plan[0]["title"] == "Assignment Story"
    print("✓ build_issue_plan accepts payload with assignments")


def test_build_issue_plan_with_empty_assignments_and_candidates():
    """Topic radar should derive assignments from candidates when assignments are empty."""
    payload = {
        "assignments": [],
        "candidates": [_candidate("Candidate Derived Story")],
    }
    plan = _run_build_issue_plan(payload)
    assert len(plan) == 1
    assert plan[0]["title"] == "Candidate Derived Story"
    print("✓ build_issue_plan accepts empty assignments with candidates")


def test_build_issue_plan_with_candidates_only():
    """Topic radar should derive assignments from candidates when assignments are missing."""
    payload = {"candidates": [_candidate("Candidates Only Story")]}
    plan = _run_build_issue_plan(payload)
    assert len(plan) == 1
    assert plan[0]["title"] == "Candidates Only Story"
    print("✓ build_issue_plan accepts candidates-only payload")


def test_build_issue_plan_fails_with_neither_assignments_nor_candidates():
    """Topic radar should still fail when both assignments and candidates are empty."""
    try:
        _run_build_issue_plan({"assignments": [], "candidates": []})
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "neither assignments nor candidates" in str(e).lower()
        print("✓ build_issue_plan fails when neither assignments nor candidates exist")


def test_build_issue_plan_partial_assignments_warns_and_pads():
    """Partial usable radar plans should warn and pad missing slots."""
    payload = {
        "assignments": [_candidate("Only One Usable Assignment")],
        "candidates": [_candidate("Candidate Backup")],
    }
    output = StringIO()
    with redirect_stdout(output):
        plan = _run_build_issue_plan(payload, story_count=3, strict_story_count=False)

    assert len(plan) == 3
    assert plan[0]["title"] == "Only One Usable Assignment"
    assert "warning: topic radar returned only 1 usable assignments" in output.getvalue().lower()
    assert "fallback assignment" in plan[1]["title"].lower()
    assert "fallback assignment" in plan[2]["title"].lower()
    print("✓ build_issue_plan warns and pads when partial assignments are usable")


def test_build_issue_plan_fails_with_zero_usable_assignments():
    """Zero usable assignments should still fail even if candidate payload exists."""
    payload = {
        "assignments": [{"bucket": "AI_FRONTIER", "section_slug": "science"}],
        "candidates": [_candidate("Valid Candidate")],
    }
    try:
        _run_build_issue_plan(payload, story_count=2, strict_story_count=False)
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "no usable assignments" in str(e).lower()
        print("✓ build_issue_plan fails when usable assignment count is zero")


def test_build_issue_plan_strict_mode_fails_on_partial_assignments():
    """Strict mode should preserve hard-fail behavior on partial usable assignments."""
    payload = {
        "assignments": [_candidate("Strict Mode Assignment")],
        "candidates": [_candidate("Candidate Backup")],
    }
    try:
        _run_build_issue_plan(payload, story_count=3, strict_story_count=True)
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "returned only 1 usable assignments" in str(e).lower()
        print("✓ strict story-count mode fails on partial usable assignments")


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
    test_build_issue_plan_with_assignments()
    test_build_issue_plan_with_empty_assignments_and_candidates()
    test_build_issue_plan_with_candidates_only()
    test_build_issue_plan_fails_with_neither_assignments_nor_candidates()
    test_build_issue_plan_partial_assignments_warns_and_pads()
    test_build_issue_plan_fails_with_zero_usable_assignments()
    test_build_issue_plan_strict_mode_fails_on_partial_assignments()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()
