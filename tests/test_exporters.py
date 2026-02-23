"""Tests for exporters: LocalFolderExporter and folder naming."""

import tempfile
from datetime import datetime
from pathlib import Path

from meetings_exporter.exporters.factory import get_exporter
from meetings_exporter.exporters.local_folder import LocalFolderExporter
from meetings_exporter.meeting_formatter import folder_name
from meetings_exporter.models import ActionItem, MeetingData, RecordingAsset


def test_folder_name_includes_title_and_sorts_by_start_time() -> None:
    data = MeetingData(
        meeting_id="meet-1",
        title="Sprint Planning",
        start_time=datetime(2025, 2, 20, 14, 0, 0),
    )
    assert folder_name(data) == "2025-02-20 14-00 - Sprint Planning"


def test_folder_name_fallback_to_meeting_id_when_no_date() -> None:
    data = MeetingData(meeting_id="meet-2", title="Standup")
    assert folder_name(data) == "Webex - Standup - meet-2"


def test_local_folder_exporter_writes_files() -> None:
    data = MeetingData(
        meeting_id="meet-3",
        title="Review",
        recordings=[
            RecordingAsset(filename="rec.mp4", content=b"fake-video-content"),
        ],
        transcript_text="Hello world",
        summary="Short summary",
        action_items=[ActionItem(text="Do something")],
    )
    with tempfile.TemporaryDirectory() as tmp:
        exporter = LocalFolderExporter(root_path=tmp)
        result = exporter.write(data)

        assert Path(result).is_dir()
        assert (Path(result) / "transcript.txt").exists()
        assert (Path(result) / "transcript.txt").read_text() == "Hello world"
        assert (Path(result) / "summary.txt").exists()
        assert "Short summary" in (Path(result) / "summary.txt").read_text()
        assert "Do something" in (Path(result) / "summary.txt").read_text()
        assert (Path(result) / "rec.mp4").exists()
        assert (Path(result) / "rec.mp4").read_bytes() == b"fake-video-content"
        assert (Path(result) / "meeting_details.txt").exists()
        details = (Path(result) / "meeting_details.txt").read_text()
        assert "Title: Review" in details
        assert "Meeting ID: meet-3" in details


def test_local_folder_exporter_writes_meeting_details_with_participants() -> None:
    data = MeetingData(
        meeting_id="meet-5",
        title="Team Sync",
        start_time=datetime(2025, 3, 1, 10, 0, 0),
        end_time=datetime(2025, 3, 1, 10, 30, 0),
        raw_metadata={"hostEmail": "host@example.com", "agenda": "Q1 review"},
        participants=[
            {"displayName": "Alice", "email": "alice@example.com"},
            {"email": "bob@example.com"},
        ],
    )
    with tempfile.TemporaryDirectory() as tmp:
        exporter = LocalFolderExporter(root_path=tmp)
        result = exporter.write(data)
        details = (Path(result) / "meeting_details.txt").read_text()
        assert "Title: Team Sync" in details
        assert "Meeting ID: meet-5" in details
        assert "Date: 2025-03-01" in details
        assert "Host: host@example.com" in details
        assert "Agenda: Q1 review" in details
        assert "Participants:" in details
        assert "Alice (alice@example.com)" in details
        assert "bob@example.com" in details


def test_local_folder_exporter_writes_vtt_and_summary_json() -> None:
    data = MeetingData(
        meeting_id="meet-4",
        title="Call",
        transcript_vtt="WEBVTT\n00:00:00.000 --> 00:00:01.000\nHi",
        summary_structured={"summary": "Notes", "actionItems": []},
    )
    with tempfile.TemporaryDirectory() as tmp:
        exporter = LocalFolderExporter(root_path=tmp)
        result = exporter.write(data)

        assert (Path(result) / "transcript.vtt").exists()
        assert "WEBVTT" in (Path(result) / "transcript.vtt").read_text()
        assert (Path(result) / "summary.json").exists()
        assert "Notes" in (Path(result) / "summary.json").read_text()


def test_get_exporter_local_returns_local_folder_exporter() -> None:
    exporter = get_exporter(backend="local", path="/tmp/out")
    assert isinstance(exporter, LocalFolderExporter)
    assert exporter.root_path == Path("/tmp/out").resolve()
