# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Webhook server for meeting notifications (meetings.ended, recordings.created, meetingTranscripts.created)

### Fixed

- Recording download now uses `temporaryDirectDownloadLinks.recordingDownloadLink` instead of `downloadUrl`. The latter points to a web page (lsr.php), not the binary; using it produced ~17KB HTML files instead of valid MP4s
- `meetings-exporter webhook` command to run webhook HTTP server
- `meetings-exporter webhook register --url <url>` and `webhook unregister` for Webex webhook lifecycle
- X-Spark-Signature verification when `WEBEX_WEBHOOK_SECRET` is set
- ngrok-based local testing documentation

## [0.1.0] - 2026-02-23

### Added

- Initial release
- List Webex meetings by date range (individual instances only)
- Export single meeting or date range to local folder or Google Drive
- Meeting Summaries API integration (summary, action items)
- Recording download and transcript export (VTT / plain text)
- Pluggable exporter architecture (local folder, Google Drive)
- `export_meeting()` function for programmatic use (CLI and future webhook integration)
- Webhook payload parsing utilities (`webhook_utils`) for Phase 2 webhook support

### License

Cisco Sample Code License v1.1. See [LICENSE](LICENSE) for details.
