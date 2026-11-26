"""AI-powered email triage classifier and structured draft generator with Gemini + local fallback."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request


def _deterministic_triage(subject: str, body: str, sender: str) -> dict:
    text = f"{subject} {body}".lower()

    if any(k in text for k in ("outage", "down", "urgent", "502", "error", "incident", "timeout")):
        category = "Incident / Support"
        priority = "P1"
        confidence = 0.94
        actions = [
            "Acknowledge incident receipt and confirm SLA response window",
            "Inspect affected service logs or reverse-proxy health endpoint",
        ]
        reply = (
            f"Hi {sender.split('@')[0]},\n\n"
            f"Thank you for flagging this urgent issue regarding \"{subject}\". Our engineering support team has logged it as P1 priority and is inspecting telemetry now.\n\n"
            "We will share a status update within 30 minutes.\n\nBest regards,\nTechnical Support Team"
        )
    elif any(k in text for k in ("invoice", "billing", "payment", "quote", "po ")):
        category = "Billing / Quote"
        priority = "P2"
        confidence = 0.91
        actions = [
            "Verify Purchase Order or invoice reference against ledger",
            "Forward approved billing summary to Accounting",
        ]
        reply = (
            f"Hi {sender.split('@')[0]},\n\n"
            f"We have received your message concerning \"{subject}\" and routed the reference details to our billing queue for verification.\n\n"
            "Best regards,\nOperations Desk"
        )
    elif any(k in text for k in ("website", "WordPress", "domain", "ssl", "update", "landing", "bug", "maintenance")):
        category = "Website Maintenance"
        priority = "P2"
        confidence = 0.89
        actions = [
            "Audit page assets, SSL expiry, and responsive DOM updates",
            "Deploy fix in GitHub branch and confirm staging build passes",
        ]
        reply = (
            f"Hi {sender.split('@')[0]},\n\n"
            f"Thanks for the website maintenance update on \"{subject}\". We are queuing the requested changes in GitHub staging for QA verification and will confirm once live.\n\n"
            "Best regards,\nWeb Engineering"
        )
    elif any(k in text for k in ("ojt", "internship", "resume", "applicant", "interview", "application")):
        category = "HR / Recruitment"
        priority = "P2"
        confidence = 0.92
        actions = [
            "Review attached applicant resume and preferred focus areas",
            "Schedule initial screening interview slot",
        ]
        reply = (
            f"Hi {sender.split('@')[0]},\n\n"
            f"Thank you for your application regarding \"{subject}\". Our team has logged your profile and will reach out with available screening times.\n\n"
            "Best regards,\nTalent & Engineering Team"
        )
    else:
        category = "General Inquiry"
        priority = "P3"
        confidence = 0.85
        actions = ["Review message context and confirm next owner"]
        reply = (
            f"Hi {sender.split('@')[0]},\n\n"
            f"Thank you for reaching out regarding \"{subject}\". Your message has been received and will be answered shortly.\n\n"
            "Best regards,\nSupport Team"
        )

    return {
        "category": category,
        "priority": priority,
        "confidence": confidence,
        "engine": "Local Rule+NLP Engine",
        "action_items": actions,
        "draft_reply": reply,
    }


def classify_and_draft(
    subject: str,
    body: str,
    sender: str,
    gemini_api_key: str | None = None,
) -> dict:
    """Classify an incoming email and draft a structured reply using Gemini API with local fallback."""
    if gemini_api_key:
        prompt = (
            "Return strict JSON with keys category, priority (P1|P2|P3), confidence (0..1 float), "
            "action_items (list of max 3 short strings), draft_reply (concise email body). "
            f"Sender: {sender}\nSubject: {subject}\nBody: {body[:1500]}"
        )
        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.0-flash:generateContent?key={gemini_api_key}"
        )
        req_body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
        req = urllib.request.Request(endpoint, data=req_body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
                txt = raw["candidates"][0]["content"]["parts"][0]["text"]
                m = re.search(r"\{.*\}", txt, re.DOTALL)
                if m:
                    parsed = json.loads(m.group(0))
                    parsed["engine"] = "Gemini 2.0 Flash"
                    return parsed
        except (urllib.error.URLError, KeyError, IndexError, ValueError, OSError):
            pass

    return _deterministic_triage(subject=subject, body=body, sender=sender)
