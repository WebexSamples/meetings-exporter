"""Utilities for parsing Webex webhook payloads.

Used when webhook server is added (Phase 2). A future webhook handler can
extract meeting and recording IDs from incoming events to trigger exports.
"""

from __future__ import annotations


def extract_meeting_id_from_payload(payload: dict) -> str | None:
    """Extract meeting ID from a Webex webhook-style payload."""
    if not payload:
        return None
    data = payload.get("data") or payload
    return data.get("meetingId") or data.get("meeting_id") or data.get("id")


def extract_recording_id_from_payload(payload: dict) -> str | None:
    """Extract recording/session ID from a Webex webhook-style payload if present."""
    if not payload:
        return None
    data = payload.get("data") or payload
    return data.get("recordingId") or data.get("recording_id") or data.get("sessionId")
