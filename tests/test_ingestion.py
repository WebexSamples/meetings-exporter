"""Tests for ingestion layer: action items parsing and collect_meeting_data with mocked client."""

from unittest.mock import MagicMock

from meetings_exporter.ingestion import (
    _action_items_from_summary_response,
    collect_meeting_data,
)
from meetings_exporter.models import MeetingData


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
