"""Tests for webhook payload parsing: extract meeting/recording IDs from sample JSON."""

from meetings_exporter.webhook_utils import (
    extract_meeting_id_from_payload,
    extract_recording_id_from_payload,
)


class TestWebhookPayloadParsing:
    """Test parsing of webhook payloads to get meeting and recording IDs."""

    def test_extract_meeting_id_from_data_nested(self) -> None:
        payload = {"data": {"meetingId": "meet-abc-123"}, "event": "meeting.ended"}
        assert extract_meeting_id_from_payload(payload) == "meet-abc-123"

    def test_extract_meeting_id_flat(self) -> None:
        payload = {"meetingId": "meet-flat"}
        assert extract_meeting_id_from_payload(payload) == "meet-flat"

    def test_extract_meeting_id_snake_case(self) -> None:
        payload = {"data": {"meeting_id": "meet-snake"}}
        assert extract_meeting_id_from_payload(payload) == "meet-snake"

    def test_extract_meeting_id_fallback_id(self) -> None:
        payload = {"data": {"id": "meet-id-only"}}
        assert extract_meeting_id_from_payload(payload) == "meet-id-only"

    def test_extract_meeting_id_empty_returns_none(self) -> None:
        assert extract_meeting_id_from_payload({}) is None
        assert extract_meeting_id_from_payload({"data": {}}) is None

    def test_extract_recording_id_from_payload(self) -> None:
        payload = {"data": {"recordingId": "rec-xyz", "meetingId": "meet-1"}}
        assert extract_recording_id_from_payload(payload) == "rec-xyz"

    def test_extract_recording_id_session_id_fallback(self) -> None:
        payload = {"data": {"sessionId": "sess-123"}}
        assert extract_recording_id_from_payload(payload) == "sess-123"
