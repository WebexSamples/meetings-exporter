# Code Tour: Webex Meeting Data Exporter

A quick walkthrough of the codebase and how it maps to Webex meeting APIs.

## Overview

This project exports Webex meeting data (recordings, transcripts, summaries, action items) to local folders or Google Drive. It uses two Webex API families:

1. **Webex Meetings API** – meetings, participants, recordings, transcripts
2. **Meeting Summaries API** – AI-generated summaries and action items

## Flow: CLI → Ingestion → Webex → Export

```
CLI (list/export) → WebexClient (HTTP) → Ingestion (collect_meeting_data) → MeetingData → Exporter (write)
```

## 1. Entry Point: `cli.py`

- **`list`** – Lists past meetings in a date range
- **`export`** – Exports one meeting by ID or all meetings in a date range

Both commands use `WebexClient` and `export_meeting()` from the ingestion layer.

## 2. Webex API Client: `webex_client.py`

All Webex calls go through `WebexClient`. Base URL: `https://webexapis.com/v1`.

| Method                                | Webex API Endpoint                       | Purpose                                                   |
| ------------------------------------- | ---------------------------------------- | --------------------------------------------------------- |
| `list_meetings()`                     | `GET /meetings`                          | List meetings with `meetingType=meeting` (instances only) |
| `get_meeting()`                       | `GET /meetings/{id}`                     | Get a single meeting                                      |
| `list_meeting_participants()`         | `GET /meetingParticipants?meetingId=...` | List participants                                         |
| `list_recordings()`                   | `GET /recordings?meetingId=...`          | List recordings                                           |
| `list_meeting_transcripts()`          | `GET /meetingTranscripts?meetingId=...`  | List transcripts                                          |
| `get_meeting_summary_by_meeting_id()` | `GET /meetingSummaries?meetingId=...`    | Get AI summary and action items                           |
| `download_transcript_from_item()`     | `GET {txtDownloadLink}`                  | Download transcript (URL from transcript item)            |

**Important details:**

- **Instance IDs** – Summaries, recordings, and transcripts require instance IDs (e.g. `..._I_...`), not series IDs. `list_meetings()` uses `meetingType=meeting` to return instances.
- **Meeting Summaries API** – Uses `GET /meetingSummaries?meetingId=...` (not the Summary Report API). See [Get Summary by Meeting ID](https://developer.webex.com/meeting/docs/api/v1/meeting-summaries/get-summary-by-meeting-id).
- **Recordings** – Uses `temporaryDirectDownloadLinks.recordingDownloadLink` from get-recording-details (not `downloadUrl`, which points to a web page).

## 3. Ingestion: `ingestion.py`

`collect_meeting_data()` fetches everything for a meeting and returns a normalized `MeetingData` object:

1. **Meeting details** – `get_meeting()` → title, start/end, host, etc.
2. **Participants** – `list_meeting_participants()`
3. **Recordings** – `list_recordings()` → `get_recording_details()` → `recordingDownloadLink` → `_get_binary_no_auth()`
4. **Transcript** – `list_meeting_transcripts()` → `txtDownloadLink` → download
5. **Summary & action items** – `get_meeting_summary_by_meeting_id()` → parses `summary`, `actionItems` (or `action_items`)

`export_meeting()` orchestrates: `collect_meeting_data()` → then passes `MeetingData` to the exporter.

## 4. Data Model: `models.py`

| Model            | Role                                                                                                |
| ---------------- | --------------------------------------------------------------------------------------------------- |
| `MeetingData`    | Normalized meeting data (title, times, recordings, transcript, summary, action items, participants) |
| `RecordingAsset` | Recording file (filename, content, download_url, mime_type)                                         |
| `ActionItem`     | Action item (text, assignee, due, raw)                                                              |

## 5. Formatting: `meeting_formatter.py`

Shared formatting used by exporters:

- `folder_name()` – e.g. `2026-02-05 14-00 - Meeting Title`
- `meeting_details_text()` – Content for `meeting_details.txt`
- `summary_txt_content()` – Summary + action items for `summary.txt`
- `safe_filename()` – Sanitizes names for file/folder use

## 6. Exporters: `exporters/`

| File              | Class                 | Role                                                                                        |
| ----------------- | --------------------- | ------------------------------------------------------------------------------------------- |
| `base.py`         | `MeetingExporter`     | ABC with `write(MeetingData) -> str`                                                        |
| `local_folder.py` | `LocalFolderExporter` | Writes to disk (meeting_details.txt, transcript.vtt, summary.txt, summary.json, recordings) |
| `google_drive.py` | `GoogleDriveExporter` | Uploads same structure to Google Drive                                                      |
| `factory.py`      | `get_exporter()`      | Chooses exporter from `EXPORT_BACKEND` env var                                              |

## 7. Webhook Utilities: `webhook_utils.py`

Helpers for future webhook support:

- `extract_meeting_id_from_payload()` – Gets `meetingId` from Webex webhook payloads
- `extract_recording_id_from_payload()` – Gets `recordingId` from payloads

## Webex API → Output Mapping

| Webex API Data                                | Output File / Content                                        |
| --------------------------------------------- | ------------------------------------------------------------ |
| `GET /meetings/{id}`                          | `meeting_details.txt` (title, date, host, participants)      |
| `GET /meetingParticipants`                    | Participant list in `meeting_details.txt`                    |
| `GET /recordings` + `recordingDownloadLink`   | `recording_*.mp4` (or `.webm`, `.m4a`)                       |
| `GET /meetingTranscripts` → `txtDownloadLink` | `transcript.vtt` or `transcript.txt`                         |
| `GET /meetingSummaries`                       | `summary.txt`, `summary.json`, action items in `summary.txt` |

## File Layout (Per Meeting)

```
{output_dir}/
  2026-02-05 14-00 - Meeting Title/
    meeting_details.txt   # Title, date, host, participants
    transcript.vtt        # Or transcript.txt
    summary.txt           # Summary + action items
    summary.json          # Raw Meeting Summaries API response
    recording_1.mp4       # Downloaded recordings
```

## Quick Reference: Webex Docs

- [Meetings API](https://developer.webex.com/docs/meetings)
- [Meeting Summaries API – Get Summary by Meeting ID](https://developer.webex.com/meeting/docs/api/v1/meeting-summaries/get-summary-by-meeting-id)
- [Recordings](https://developer.webex.com/docs/meetings#recordings)
- [Transcripts](https://developer.webex.com/docs/meetings#meeting-transcripts)
