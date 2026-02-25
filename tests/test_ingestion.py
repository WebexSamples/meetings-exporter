"""Tests for ingestion layer: action items parsing and collect_meeting_data with mocked client."""

from unittest.mock import MagicMock

from meetings_exporter.ingestion import (
    _action_items_from_summary_response,
    _normalize_mime_type,
    collect_meeting_data,
)
from meetings_exporter.models import MeetingData


class TestNormalizeMimeType:
    """Test _normalize_mime_type maps Webex format to valid MIME types."""

    def test_mp4_uppercase_maps_to_video_mp4(self) -> None:
        assert _normalize_mime_type("MP4") == "video/mp4"

    def test_webm_maps_to_video_webm(self) -> None:
        assert _normalize_mime_type("webm") == "video/webm"

    def test_empty_or_none_defaults_to_video_mp4(self) -> None:
        assert _normalize_mime_type(None) == "video/mp4"
        assert _normalize_mime_type("") == "video/mp4"

    def test_unknown_format_defaults_to_video_mp4(self) -> None:
        assert _normalize_mime_type("unknown") == "video/mp4"


class TestActionItemsFromSummaryResponse:
    """Test parsing of Meeting Summaries API response into ActionItem list."""

    def test_empty_payload_returns_empty_list(self) -> None:
        assert _action_items_from_summary_response({}) == []
        assert _action_items_from_summary_response({"summary": "foo"}) == []

    def test_action_items_camel_case(self) -> None:
        payload = {
            "actionItems": [
                {"text": "Follow up with eng", "assignee": "alice", "due": "2025-03-01"},
                {"title": "Send deck"},
            ],
        }
        items = _action_items_from_summary_response(payload)
        assert len(items) == 2
        assert items[0].text == "Follow up with eng"
        assert items[0].assignee == "alice"
        assert items[0].due == "2025-03-01"
        assert items[1].text == "Send deck"

    def test_action_items_snake_case(self) -> None:
        payload = {"action_items": [{"text": "Review PR"}]}
        items = _action_items_from_summary_response(payload)
        assert len(items) == 1
        assert items[0].text == "Review PR"

    def test_string_action_items(self) -> None:
        payload = {"actionItems": ["Item one", "Item two"]}
        items = _action_items_from_summary_response(payload)
        assert len(items) == 2
        assert items[0].text == "Item one"
        assert items[1].text == "Item two"


class TestCollectMeetingData:
    """Test collect_meeting_data with mocked Webex client."""

    def test_returns_meeting_data_with_metadata_and_summary(self) -> None:
        mock_client = MagicMock()
        mock_client.get_meeting.return_value = {
            "id": "meet-123",
            "title": "Team Sync",
            "start": "2025-02-20T14:00:00Z",
            "end": "2025-02-20T14:30:00Z",
        }
        mock_client.list_recordings.return_value = []
        mock_client.list_meeting_transcripts.return_value = []
        mock_client.get_meeting_summary_by_meeting_id.return_value = {
            "summary": "We discussed Q1 goals.",
            "actionItems": [{"text": "Send notes"}],
        }

        result = collect_meeting_data(mock_client, "meet-123")

        assert isinstance(result, MeetingData)
        assert result.meeting_id == "meet-123"
        assert result.title == "Team Sync"
        assert result.summary == "We discussed Q1 goals."
        assert len(result.action_items) == 1
        assert result.action_items[0].text == "Send notes"
        mock_client.get_meeting.assert_called_once_with("meet-123")
        mock_client.get_meeting_summary_by_meeting_id.assert_called_with("meet-123")

    def test_uses_meeting_id_for_title_when_missing(self) -> None:
        mock_client = MagicMock()
        mock_client.get_meeting.return_value = {"id": "meet-456"}
        mock_client.list_recordings.return_value = []
        mock_client.list_meeting_transcripts.return_value = []
        mock_client.get_meeting_summary_by_meeting_id.return_value = {}

        result = collect_meeting_data(mock_client, "meet-456")

        assert result.title == "Meeting meet-456"

    def test_recordings_use_recording_download_link_not_download_url(self) -> None:
        """Recordings use recordingDownloadLink, not downloadUrl (which is a web page)."""
        mock_client = MagicMock()
        mock_client.get_meeting.return_value = {
            "id": "meet-789",
            "title": "Recording Test",
            "start": "2025-02-20T14:00:00Z",
        }
        mock_client.list_recordings.return_value = [
            {
                "id": "rec-1",
                "hostEmail": "host@test.com",
                "topic": "Test Recording",
                "format": "MP4",
            },
        ]
        mock_client.get_recording_details.return_value = {
            "downloadUrl": "https://site.webex.com/lsr.php?RCID=xxx",  # web page - must NOT be used
            "temporaryDirectDownloadLinks": {
                "recordingDownloadLink": "https://cdn.webex.com/nbr/recording.mp4",
            },
        }
        mock_client._get_binary_no_auth.return_value = b"\x00\x00\x00\x20ftypiso6"  # MP4 header
        mock_client.list_meeting_transcripts.return_value = []
        mock_client.get_meeting_summary_by_meeting_id.return_value = {}

        result = collect_meeting_data(mock_client, "meet-789")

        assert len(result.recordings) == 1
        assert result.recordings[0].content == b"\x00\x00\x00\x20ftypiso6"
        assert result.recordings[0].filename == "Test Recording.mp4"
        mock_client.get_recording_details.assert_called_once_with("rec-1", "host@test.com")
        mock_client._get_binary_no_auth.assert_called_once_with(
            "https://cdn.webex.com/nbr/recording.mp4"
        )
