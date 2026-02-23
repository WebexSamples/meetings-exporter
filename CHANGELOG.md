# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
