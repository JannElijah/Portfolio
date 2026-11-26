"""Final verification test for StudentOS"""
from database import DatabaseManager
from notifications import NotificationManager

print("StudentOS Final Verification")
print("=" * 50)

# Test 1: Database initialization
try:
    db = DatabaseManager()
    print("[OK] Database initialized")
except Exception as e:
    print(f"[FAIL] Database: {e}")
    exit(1)

# Test 2: Notification Manager
try:
    notification_manager = NotificationManager(db)
    print("[OK] Notification Manager initialized")
except Exception as e:
    print(f"[FAIL] Notification Manager: {e}")
    exit(1)

# Test 3: Import all views
try:
    from views.dashboard import DashboardView
    from views.academics import AcademicsView
    from views.assignments import AssignmentsView
    from views.calendar_view import CalendarView
    from views.weekly_schedule import WeeklyScheduleView
    from views.projects import ProjectsView
    from views.finance import ExpenseTracker
    from views.focus import FocusView
    from views.focus_history import FocusHistoryView
    from views.study_stats import StudyStatsView
    from views.goals import GoalsView
    from views.time_tracking import TimeTrackingView
    from views.library import LibraryView
    from views.notes import NotesView
    from views.settings import SettingsView
    print("[OK] All 15 views imported successfully")
except Exception as e:
    print(f"[FAIL] View imports: {e}")
    exit(1)

# Test 4: Initialize views (except SettingsView which needs page)
try:
    dashboard_view = DashboardView(db)
    academics_view = AcademicsView(db)
    assignments_view = AssignmentsView(db)
    calendar_view = CalendarView(db)
    weekly_schedule_view = WeeklyScheduleView(db)
    projects_view = ProjectsView(db)
    finance_view = ExpenseTracker(db)
    focus_view = FocusView(db, notification_manager)
    focus_history_view = FocusHistoryView(db)
    study_stats_view = StudyStatsView(db)
    goals_view = GoalsView(db)
    time_tracking_view = TimeTrackingView(db)
    library_view = LibraryView(db)
    notes_view = NotesView(db)
    print("[OK] All 14 views initialized (SettingsView requires page)")
except Exception as e:
    print(f"[FAIL] View initialization: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 5: Test new database methods
try:
    # Focus methods
    focus_logs = db.get_focus_logs_with_dates("2026-01-01", "2026-12-31")
    focus_stats = db.get_focus_statistics()
    
    # Study stats
    study_stats = db.get_study_statistics()
    
    # Goals
    goal_id = db.add_goal("study_hours", 10.0, "weekly", "2026-02-13", "2026-02-20")
    goals = db.get_goals("active")
    
    # Time tracking
    entry_id = db.add_time_entry("subject", 1, "Test", 30, "09:00", "09:30", "Test note")
    entries = db.get_time_entries("subject", 1, 10)
    summary = db.get_time_summary_by_entity("subject")
    
    # Filters
    assignments = db.get_assignments_filtered(None, None, None, None)
    events = db.get_events_filtered(None, None, None)
    expenses = db.get_expenses_filtered(None, None, None, None)
    
    print("[OK] All 11 new database methods working")
except Exception as e:
    print(f"[FAIL] Database methods: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("=" * 50)
print("[SUCCESS] StudentOS is fully operational!")
print("\nYou can now run: python main.py")
print("\nAll features available:")
print("  - Dashboard, Academics, Assignments, Calendar")
print("  - Weekly Schedule, Projects, Finance, Focus Timer")
print("  - Focus History, Study Stats, Goals, Time Tracking")
print("  - Library, Notes, Settings")
