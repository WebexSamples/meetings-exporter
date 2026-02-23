# Security

## Reporting Vulnerabilities

If you discover a security vulnerability in this project, please report it responsibly:

- **Do not** open a public GitHub issue for security vulnerabilities
- Email the Webex Developer Relations team at devrel@webex.com with details
- Include steps to reproduce, impact assessment, and any suggested fixes
- We aim to acknowledge reports within 48 hours and provide an initial assessment

## Token and Credential Handling

- **Never commit** `.env`, `token.json`, or `*.credentials.json` to the repository. These are listed in `.gitignore`
- Store Webex access tokens and Google OAuth credentials securely (e.g. environment variables, secrets manager)
- Rotate tokens periodically and revoke access when no longer needed
- Use minimal scopes: the app uses `drive.file` for Google Drive (only files the app creates)

## Dependencies

- We pin dependency versions in `pyproject.toml` and `package-lock.json`
- Run `pip audit` and `npm audit` periodically to check for known vulnerabilities
- Keep dependencies updated when security patches are released
