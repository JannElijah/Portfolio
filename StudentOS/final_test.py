"""Final comprehensive test - checking all views can initialize"""
from database import DatabaseManager
from notifications import NotificationManager
import traceback

print("=" * 60)
print("STUDENTOS - FINAL STARTUP TEST")
print("=" * 60)

errors = []
success_count = 0

# 1. Database
print("\n[1/4] Initializing Database...")
try:
    db = DatabaseManager()
    print("      [OK] Database ready")
    success_count += 1
except Exception as e:
    print(f"      [FAIL] {e}")
    errors.append(("Database", str(e)))
    traceback.print_exc()

# 2. Notifications
print("\n[2/4] Initializing Notification Manager...")
try:
    notification_manager = NotificationManager(db)
    print("      [OK] Notifications ready")
    success_count += 1
except Exception as e:
    print(f"      [FAIL] {e}")
    errors.append(("NotificationManager", str(e)))
    traceback.print_exc()

# 3. Import all views
print("\n[3/4] Importing all views...")
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
    print("      [OK] All 15 views imported")
    success_count += 1
except Exception as e:
    print(f"      [FAIL] {e}")
    errors.append(("View Imports", str(e)))
    traceback.print_exc()

# 4. Initialize all views (except Settings which needs page)
print("\n[4/4] Initializing all views...")
view_tests = [
    ("DashboardView", lambda: DashboardView(db)),
    ("AcademicsView", lambda: AcademicsView(db)),
    ("AssignmentsView", lambda: AssignmentsView(db)),
    ("CalendarView", lambda: CalendarView(db)),
    ("WeeklyScheduleView", lambda: WeeklyScheduleView(db)),
    ("ProjectsView", lambda: ProjectsView(db)),
    ("ExpenseTracker", lambda: ExpenseTracker(db)),
    ("FocusView", lambda: FocusView(db, notification_manager)),
    ("FocusHistoryView", lambda: FocusHistoryView(db)),
    ("StudyStatsView", lambda: StudyStatsView(db)),
    ("GoalsView", lambda: GoalsView(db)),
    ("TimeTrackingView", lambda: TimeTrackingView(db)),
    ("LibraryView", lambda: LibraryView(db)),
    ("NotesView", lambda: NotesView(db)),
]

failed_views = []
for name, init_func in view_tests:
    try:
        view = init_func()
        print(f"      [OK] {name}")
    except Exception as e:
        print(f"      [FAIL] {name}: {e}")
        failed_views.append((name, str(e)))
        traceback.print_exc()

if not failed_views:
    success_count += 1
    print(f"      [OK] All 14 views initialized successfully")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if errors:
    print(f"\n[ERROR] {len(errors)} critical errors:")
    for component, error in errors:
        print(f"  - {component}: {error}")

if failed_views:
    print(f"\n[ERROR] {len(failed_views)} view initialization errors:")
    for name, error in failed_views:
        print(f"  - {name}: {error}")

if not errors and not failed_views:
    print("\n[SUCCESS] ALL SYSTEMS OPERATIONAL!")
    print("\nStudentOS is ready to launch.")
    print("\nRun: python main.py")
    print("\nAll 15 features available:")
    print("  1. Dashboard       - Overview & Quick Stats")
    print("  2. Academics       - Subjects & GPA Tracking")
    print("  3. Assignments     - Assignment Management")
    print("  4. Calendar        - Event Calendar")
    print("  5. Weekly Schedule - Week View of Events")
    print("  6. Projects        - Project Tracking")
    print("  7. Finance         - Expense Tracking")
    print("  8. Focus Timer     - Pomodoro Timer")
    print("  9. Focus History   - Session Analytics")
    print(" 10. Study Stats     - Study Statistics")
    print(" 11. Goals           - Goal Setting & Tracking")
    print(" 12. Time Tracking   - Manual Time Logs")
    print(" 13. Library         - Resource Management")
    print(" 14. Notes           - Note Taking")
    print(" 15. Settings        - App Configuration")
    exit(0)
else:
    print(f"\n[WARNING] Please fix the errors above before running.")
    exit(1)
