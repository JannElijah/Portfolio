"""Comprehensive test of all views"""
import traceback
from database import DatabaseManager

print("=" * 60)
print("TESTING STUDENTOS VIEWS")
print("=" * 60)

# Initialize database
print("\n1. Testing Database...")
try:
    db = DatabaseManager()
    print("   [OK] Database initialized successfully")
except Exception as e:
    print(f"   [FAIL] Database error: {e}")
    traceback.print_exc()
    exit(1)

# Test each view import and initialization
views_to_test = [
    ("DashboardView", "views.dashboard", "DashboardView"),
    ("AcademicsView", "views.academics", "AcademicsView"),
    ("AssignmentsView", "views.assignments", "AssignmentsView"),
    ("CalendarView", "views.calendar_view", "CalendarView"),
    ("WeeklyScheduleView", "views.weekly_schedule", "WeeklyScheduleView"),
    ("ProjectsView", "views.projects", "ProjectsView"),
    ("ExpenseTracker", "views.finance", "ExpenseTracker"),
    ("FocusView", "views.focus", "FocusView"),
    ("FocusHistoryView", "views.focus_history", "FocusHistoryView"),
    ("StudyStatsView", "views.study_stats", "StudyStatsView"),
    ("GoalsView", "views.goals", "GoalsView"),
    ("TimeTrackingView", "views.time_tracking", "TimeTrackingView"),
    ("LibraryView", "views.library", "LibraryView"),
    ("NotesView", "views.notes", "NotesView"),
    ("SettingsView", "views.settings", "SettingsView"),
]

print("\n2. Testing View Imports and Initialization...")
failed_views = []

for name, module, class_name in views_to_test:
    try:
        # Import the module
        exec(f"from {module} import {class_name}")
        
        # Initialize the view
        if name == "FocusView":
            # FocusView requires notification_manager
            from notifications import NotificationManager
            notification_manager = NotificationManager(db)
            view = eval(f"{class_name}(db, notification_manager)")
        else:
            view = eval(f"{class_name}(db)")
        
        print(f"   [OK] {name}")
        
    except Exception as e:
        print(f"   [FAIL] {name}: {e}")
        failed_views.append((name, e))
        traceback.print_exc()

# Test database methods for new features
print("\n3. Testing New Database Methods...")
db_methods = [
    ("get_focus_logs_with_dates", lambda: db.get_focus_logs_with_dates("2026-01-01", "2026-12-31")),
    ("get_focus_statistics", lambda: db.get_focus_statistics()),
    ("get_study_statistics", lambda: db.get_study_statistics()),
    ("add_goal", lambda: db.add_goal("study_hours", 10.0, "weekly", "2026-02-13", "2026-02-20")),
    ("get_goals", lambda: db.get_goals("active")),
    ("add_time_entry", lambda: db.add_time_entry("subject", 1, "Test Subject", 30, "09:00", "09:30", "Test")),
    ("get_time_entries", lambda: db.get_time_entries("subject", 1, 10)),
    ("get_time_summary_by_entity", lambda: db.get_time_summary_by_entity("subject")),
    ("get_assignments_filtered", lambda: db.get_assignments_filtered(None, None, None, None)),
    ("get_events_filtered", lambda: db.get_events_filtered(None, None, None)),
    ("get_expenses_filtered", lambda: db.get_expenses_filtered(None, None, None, None)),
]

failed_methods = []
for method_name, method_call in db_methods:
    try:
        result = method_call()
        print(f"   [OK] {method_name}")
    except Exception as e:
        print(f"   [FAIL] {method_name}: {e}")
        failed_methods.append((method_name, e))
        traceback.print_exc()

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if failed_views:
    print(f"\nFailed Views ({len(failed_views)}):")
    for name, error in failed_views:
        print(f"  - {name}: {error}")
else:
    print("\n[OK] All 15 views passed!")

if failed_methods:
    print(f"\nFailed Database Methods ({len(failed_methods)}):")
    for name, error in failed_methods:
        print(f"  - {name}: {error}")
else:
    print("\n[OK] All database methods passed!")

if not failed_views and not failed_methods:
    print("\n[SUCCESS] ALL TESTS PASSED! StudentOS is ready to run.")
    exit(0)
else:
    print(f"\n[WARNING] {len(failed_views) + len(failed_methods)} tests failed.")
    exit(1)
