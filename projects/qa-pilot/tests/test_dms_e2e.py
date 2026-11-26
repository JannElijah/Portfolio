"""Headless Chromium Playwright E2E Page-Object-Model tests against live UPHSD-DMS."""

from __future__ import annotations

from playwright.sync_api import expect

from qa_pilot.pages.dms_page import DmsPage


def test_e2e_submit_review_and_approve_document(live_dms_url: str, browser_page) -> None:
    dms = DmsPage(browser_page, live_dms_url)
    dms.goto()

    unique_title = "QA-Pilot OJT Endorsement E2E"
    dms.switch_role("DEAN")
    dms.submit_document(title=unique_title, department="CCS", submitted_by="Jann QA")

    expect(dms.card_by_title(unique_title)).to_be_visible()

    dms.transition_document(unique_title, "Review")
    expect(dms.card_in_stage(unique_title, "In Review")).to_be_visible()

    dms.transition_document(unique_title, "Approve")
    expect(dms.card_in_stage(unique_title, "Approved")).to_be_visible()


def test_e2e_staff_role_blocked_with_ui_error_banner(live_dms_url: str, browser_page) -> None:
    dms = DmsPage(browser_page, live_dms_url)
    dms.goto()

    unique_title = "QA-Pilot Staff Guard Check"
    dms.switch_role("STAFF")
    dms.submit_document(title=unique_title, department="IT Lab", submitted_by="Student")

    dms.transition_document(unique_title, "Approve")
    expect(dms.error_banner).to_contain_text("Reviewer or Dean role required")
