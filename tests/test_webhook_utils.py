"""Tests for webhook payload parsing: extract meeting/recording IDs from sample JSON."""

import hashlib
import hmac

from meetings_exporter.webhook_utils import (
    extract_meeting_id_from_payload,
    extract_meeting_id_from_webhook_envelope,
    extract_recording_id_from_payload,
    is_exportable_event,
    verify_webhook_signature,
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


class TestExtractMeetingIdFromWebhookEnvelope:
    """Test extract_meeting_id_from_webhook_envelope for Webex envelope format."""

    def test_meetings_ended_data_id(self) -> None:
        payload = {"resource": "meetings", "event": "ended", "data": {"id": "meet-inst-123"}}
        assert extract_meeting_id_from_webhook_envelope(payload) == "meet-inst-123"

    def test_recordings_created_data_meeting_id(self) -> None:
        payload = {
            "resource": "recordings",
            "event": "created",
            "data": {"meetingId": "meet-rec-456", "id": "rec-xyz"},
        }
        assert extract_meeting_id_from_webhook_envelope(payload) == "meet-rec-456"

    def test_meeting_transcripts_created_data_meeting_id(self) -> None:
        payload = {
            "resource": "meetingTranscripts",
            "event": "created",
            "data": {"meetingId": "meet-trans-789"},
        }
        assert extract_meeting_id_from_webhook_envelope(payload) == "meet-trans-789"

    def test_empty_returns_none(self) -> None:
        assert extract_meeting_id_from_webhook_envelope({}) is None


class TestIsExportableEvent:
    """Test is_exportable_event for allowed and disallowed (resource, event) pairs."""

    def test_meetings_ended(self) -> None:
        assert is_exportable_event("meetings", "ended") is True

    def test_recordings_created(self) -> None:
        assert is_exportable_event("recordings", "created") is True

    def test_meeting_transcripts_created(self) -> None:
        assert is_exportable_event("meetingTranscripts", "created") is True

    def test_meetings_started_not_exportable(self) -> None:
        assert is_exportable_event("meetings", "started") is False

    def test_messages_created_not_exportable(self) -> None:
        assert is_exportable_event("messages", "created") is False

    def test_unknown_resource_not_exportable(self) -> None:
        assert is_exportable_event("unknown", "created") is False


class TestVerifyWebhookSignature:
    """Test verify_webhook_signature (HMAC-SHA1)."""

    def test_valid_signature(self) -> None:
        payload = b'{"resource":"meetings","event":"ended"}'
        secret = "my-secret"
        sig = hmac.new(secret.encode(), payload, hashlib.sha1).hexdigest()
        assert verify_webhook_signature(payload, sig, secret) is True

    def test_invalid_signature(self) -> None:
        payload = b'{"resource":"meetings"}'
        assert verify_webhook_signature(payload, "wrong-sig", "my-secret") is False

    def test_empty_signature_returns_false(self) -> None:
        assert verify_webhook_signature(b"{}", "", "secret") is False

    def test_empty_secret_returns_false(self) -> None:
        assert verify_webhook_signature(b"{}", "abc", "") is False
