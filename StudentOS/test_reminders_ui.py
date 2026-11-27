"""Non-destructive unit tests verifying StudentOS Reminder UI integration and DB helpers."""

import base64
import os
import tempfile

from charts import (
    compute_productivity_score,
    create_focus_chart,
    create_grades_chart,
    create_spending_chart,
    export_weekly_markdown,
)
from database import DatabaseManager
from views.assignments import AssignmentsView
from views.calendar_view import CalendarView


def test_calendar_and_assignment_reminder_integration() -> None:
    tmp_fd, tmp_db = tempfile.mkstemp(suffix=".db")
    os.close(tmp_fd)
    try:
        db = DatabaseManager(tmp_db)
        event_id = db.add_event(
            title="Capstone Defense Briefing",
            description="Final check",
            event_type="Meeting",
            start_date="2026-12-01 09:00",
        )
        assign_id = db.add_assignment(
            subject="IT402",
            title="Network Security Lab Report",
            description="OSPF & ACL documentation",
            due_date="2026-12-03",
        )

        rem_ev = db.add_reminder("event", event_id, "2026-12-01 08:00")
        rem_as = db.add_reminder("assignment", assign_id, "2026-12-02 18:00")

        assert len(db.get_reminders("event", event_id)) == 1
        assert len(db.get_reminders("assignment", assign_id)) == 1

        cal = CalendarView(db)
        cal.load_events()
        assert len(cal.events_list.controls) == 1

        asg = AssignmentsView(db)
        asg.load_assignments()
        assert len(asg.assignments_list.controls) == 1

        db.delete_reminder(rem_ev)
        db.delete_reminder(rem_as)
        assert len(db.get_reminders("event", event_id)) == 0
        assert len(db.get_reminders("assignment", assign_id)) == 0

        seeded_count = db.seed_demo_semester()
        assert seeded_count >= 12
        assert db.calculate_gpa() is not None

        sp_b64 = create_spending_chart([("2026-11-25", 18.0), ("2026-11-26", 32.5)], budget=50.0)
        gr_b64 = create_grades_chart([("IT402", 94.0), ("CS401", 88.5)])
        fc_b64 = create_focus_chart([("2026-11-25", 75), ("2026-11-26", 90)])
        assert base64.b64decode(sp_b64).startswith(b"\x89PNG")
        assert base64.b64decode(gr_b64).startswith(b"\x89PNG")
        assert base64.b64decode(fc_b64).startswith(b"\x89PNG")

        prod = compute_productivity_score(4, 5, 180, 7)
        assert prod["score"] == 90 and prod["tier"] == "Peak Flow"
        md_report = export_weekly_markdown(db.generate_weekly_report())
        assert "# StudentOS Weekly Report" in md_report and "Tasks:" in md_report
        print("StudentOS Reminder UI integration test passed!")
    finally:
        if os.path.exists(tmp_db):
            os.remove(tmp_db)


if __name__ == "__main__":
    test_calendar_and_assignment_reminder_integration()
