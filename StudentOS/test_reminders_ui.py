"""Non-destructive unit tests verifying StudentOS Reminder UI integration and DB helpers."""

import os
import tempfile

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
        print("StudentOS Reminder UI integration test passed!")
    finally:
        if os.path.exists(tmp_db):
            os.remove(tmp_db)


if __name__ == "__main__":
    test_calendar_and_assignment_reminder_integration()
