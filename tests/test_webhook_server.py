"""Tests for webhook HTTP server."""

import hashlib
import hmac
import json
from unittest.mock import patch

from meetings_exporter.webhook_server import process_webhook_payload


def test_process_webhook_exportable_event_returns_200_and_export_info() -> None:
    """Valid meetings.ended payload returns 200 and export_info with meeting ID."""
    with patch.dict("os.environ", {"WEBEX_ACCESS_TOKEN": "test"}, clear=False):
        payload = {
            "resource": "meetings",
            "event": "ended",
            "data": {"id": "meet-export-123"},
        }
        body = json.dumps(payload).encode()
        status, resp, export_info = process_webhook_payload(body, {})
        assert status == 200
        assert resp == {"status": "ok"}
        assert export_info is not None
        assert export_info[0] == "meet-export-123"
        assert export_info[1] == "meetings"
        assert export_info[2] == "ended"


def test_process_webhook_invalid_json_returns_400() -> None:
    """Invalid JSON returns 400."""
    status, resp, export_info = process_webhook_payload(b"not valid json", {})
    assert status == 400
    assert "error" in resp
    assert "Invalid" in resp["error"]
    assert export_info is None


def test_process_webhook_unknown_event_returns_200_no_export() -> None:
    """Unknown resource/event returns 200 but no export_info."""
    payload = {"resource": "messages", "event": "created", "data": {"id": "msg-1"}}
    body = json.dumps(payload).encode()
    status, resp, export_info = process_webhook_payload(body, {})
    assert status == 200
    assert resp == {"status": "ok"}
    assert export_info is None


def test_process_webhook_invalid_signature_returns_401() -> None:
    """Invalid X-Spark-Signature returns 401 when secret is set."""
    with patch.dict(
        "os.environ",
        {"WEBEX_ACCESS_TOKEN": "test", "WEBEX_WEBHOOK_SECRET": "secret"},
        clear=False,
    ):
        payload = {"resource": "meetings", "event": "ended", "data": {"id": "meet-1"}}
        body = json.dumps(payload).encode()
        headers = {"x-spark-signature": "invalid-signature"}
        status, resp, export_info = process_webhook_payload(body, headers)
        assert status == 401
        assert "error" in resp
        assert export_info is None


def test_process_webhook_valid_signature_accepts() -> None:
    """Valid X-Spark-Signature accepts the request."""
    with patch.dict(
        "os.environ",
        {"WEBEX_ACCESS_TOKEN": "test", "WEBEX_WEBHOOK_SECRET": "my-secret"},
        clear=False,
    ):
        payload = {"resource": "meetings", "event": "ended", "data": {"id": "meet-99"}}
        body = json.dumps(payload).encode()
        sig = hmac.new(b"my-secret", body, hashlib.sha1).hexdigest()
        headers = {"x-spark-signature": sig}
        status, resp, export_info = process_webhook_payload(body, headers)
        assert status == 200
        assert export_info is not None
        assert export_info[0] == "meet-99"
