"""Tests for meeting_formatter: folder names, meeting details, summary text."""

from datetime import datetime

from meetings_exporter.meeting_formatter import (
    folder_name,
    meeting_details_text,
    safe_filename,
    summary_txt_content,
)
from meetings_exporter.models import ActionItem, MeetingData


def test_safe_filename_strips_special_chars() -> None:
    assert safe_filename("foo/bar\\baz") == "foobarbaz"
    assert safe_filename("  spaces  ") == "spaces"


def test_folder_name_includes_date_prefix() -> None:
    data = MeetingData(
        meeting_id="meet-1",
        title="Sprint Planning",
        start_time=datetime(2025, 2, 20, 14, 0, 0),
    )
    assert folder_name(data) == "2025-02-20 14-00 - Sprint Planning"


def test_meeting_details_text_includes_title_and_host() -> None:
    data = MeetingData(
        meeting_id="meet-5",
        title="Team Sync",
        start_time=datetime(2025, 3, 1, 10, 0, 0),
        raw_metadata={"hostEmail": "host@example.com", "agenda": "Q1 review"},
        participants=[
            {"displayName": "Alice", "email": "alice@example.com"},
        ],
    )
    text = meeting_details_text(data)
    assert "Title: Team Sync" in text
    assert "Meeting ID: meet-5" in text
    assert "Host: host@example.com" in text
    assert "Agenda: Q1 review" in text
    assert "Participants:" in text
    assert "Alice (alice@example.com)" in text


def test_summary_txt_content_includes_action_items() -> None:
    data = MeetingData(
        meeting_id="meet-3",
        title="Review",
        summary="Short summary",
        action_items=[ActionItem(text="Do something", assignee="alice")],
    )
    content = summary_txt_content(data)
    assert content is not None
    assert "Short summary" in content
    assert "## Action Items" in content
    assert "Do something" in content
    assert "assignee: alice" in content


def test_summary_txt_content_returns_none_when_empty() -> None:
    data = MeetingData(meeting_id="meet-1", title="Empty")
    assert summary_txt_content(data) is None
