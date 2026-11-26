"""Playwright Page Object Model for the UPHSD Document Management System web app."""

from __future__ import annotations

from playwright.sync_api import Locator, Page


class DmsPage:
    """Encapsulates selectors and workflows on the UPHSD-DMS Kanban queue."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

        self.role_select: Locator = page.locator("#roleSelect")
        self.title_input: Locator = page.locator("#titleInput")
        self.dept_input: Locator = page.locator("#deptInput")
        self.user_input: Locator = page.locator("#userInput")
        self.submit_btn: Locator = page.get_by_role("button", name="Submit to Queue")
        self.error_banner: Locator = page.locator("#msg")
        self.board: Locator = page.locator("#board")

    def goto(self) -> None:
        self.page.goto(f"{self.base_url}/", wait_until="networkidle")
        self.page.wait_for_selector("#board .col")

    def switch_role(self, role_value: str) -> None:
        self.role_select.select_option(role_value)

    def submit_document(self, title: str, department: str = "CCS", submitted_by: str = "QA Bot") -> None:
        self.title_input.fill(title)
        self.dept_input.select_option(department)
        self.user_input.fill(submitted_by)
        with self.page.expect_response(
            lambda r: "/api/documents" in r.url and r.request.method == "GET"
        ):
            self.submit_btn.click()

    def card_by_title(self, title: str) -> Locator:
        return self.page.locator("#board .doc", has_text=title)

    def card_in_stage(self, title: str, stage_label: str) -> Locator:
        col = self.page.locator("#board .panel.col").filter(
            has=self.page.locator("h3", has_text=stage_label)
        )
        return col.locator(".doc", has_text=title)

    def transition_document(self, title: str, action_label: str) -> None:
        card = self.card_by_title(title).first
        with self.page.expect_response(
            lambda r: "/api/documents" in r.url and r.request.method == "GET"
        ):
            card.get_by_role("button", name=action_label).click()

    def stage_header_text(self, stage_label: str) -> str:
        return self.page.locator("#board .col h3", has_text=stage_label).inner_text()
