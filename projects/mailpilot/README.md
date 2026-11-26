# MailPilot AI — Email Client & Draft Automation Console

AI-powered email triage, intent classification, IMAPS/STARTTLS configuration verification, and human-in-the-loop reply drafting built in Python (`email.parser`, SQLite, REST HTTP API, Gemini API + deterministic local NLP fallback).

## Key Capabilities
- **Email Client Security Validator**: Audits IMAP (993) and SMTP (465/587) TLS posture and parses RFC-822 `.eml` payloads.
- **AI Intent & Priority Triage**: Classifies messages (`Incident / Support`, `Website Maintenance`, `Billing / Quote`, `HR / Recruitment`), extracts action items, and generates editable reply drafts.
- **Web Triage Queue & Outbox Log**: SQLite-backed inbox queue with one-click Outbox approval.

## Run Locally
```bash
cd projects/mailpilot
python -m mailpilot.server
python -m pytest -v
```
