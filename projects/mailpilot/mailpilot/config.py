"""Email client IMAP/SMTP profile validator and MIME parser."""

from __future__ import annotations

from email import policy
from email.parser import Parser
from email.utils import parseaddr

KNOWN_PROVIDERS = {
    "gmail": {"imap_host": "imap.gmail.com", "imap_port": 993, "smtp_host": "smtp.gmail.com", "smtp_port": 587},
    "microsoft365": {"imap_host": "outlook.office365.com", "imap_port": 993, "smtp_host": "smtp.office365.com", "smtp_port": 587},
    "custom": {"imap_host": "mail.company.local", "imap_port": 993, "smtp_host": "smtp.company.local", "smtp_port": 465},
}


def validate_email_client_profile(
    email_address: str,
    imap_host: str,
    imap_port: int,
    smtp_host: str,
    smtp_port: int,
    use_tls: bool = True,
) -> dict:
    """Validate IMAP/SMTP client configuration security rules (encrypted ports, valid address)."""
    issues: list[str] = []
    _, addr = parseaddr(email_address)
    if "@" not in addr or "." not in addr.split("@")[-1]:
        issues.append("Invalid sender email address format.")
    if not imap_host.strip():
        issues.append("IMAP hostname is required.")
    if not smtp_host.strip():
        issues.append("SMTP hostname is required.")
    if not use_tls or imap_port not in {993} or smtp_port not in {465, 587}:
        issues.append("Insecure plaintext port detected; require IMAPS (993) and SMTPS/STARTTLS (465/587).")

    return {
        "valid": len(issues) == 0,
        "email": addr,
        "imap": f"{imap_host.strip()}:{imap_port}",
        "smtp": f"{smtp_host.strip()}:{smtp_port}",
        "tls_enforced": bool(use_tls and imap_port == 993 and smtp_port in {465, 587}),
        "issues": issues,
    }


def parse_raw_email(raw_rfc822: str) -> dict:
    """Extract clean sender, subject, and body text from a raw RFC-822 .eml message."""
    msg = Parser(policy=policy.default).parsestr(raw_rfc822)
    sender = str(msg.get("From") or "unknown@sender.local")
    subject = str(msg.get("Subject") or "(No Subject)")
    body_part = msg.get_body(preferencelist=("plain", "html"))
    body = body_part.get_content() if body_part is not None else str(msg.get_payload() or "")
    return {"sender": sender.strip(), "subject": subject.strip(), "body": str(body).strip()}
