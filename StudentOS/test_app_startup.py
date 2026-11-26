"""Test app startup to identify errors"""
import sys
import traceback

try:
    print("Importing modules...")
    import flet as ft
    from database import Database
    
    print("Creating database...")
    db = Database()
    
    print("Importing views...")
    from views.dashboard import DashboardView
    from views.academics import AcademicsView
    from views.assignments import AssignmentsView
    from views.calendar_view import CalendarView
    from views.weekly_schedule import WeeklyScheduleView
    from views.projects import ProjectsView
    from views.finance import FinanceView
    from views.focus import FocusTimerView
    from views.focus_history import FocusHistoryView
    from views.study_stats import StudyStatsView
    from views.goals import GoalsView
    from views.time_tracking import TimeTrackingView
    from views.library import LibraryView
    from views.notes import NotesView
    from views.settings import SettingsView
    
    print("Initializing views...")
    dashboard_view = DashboardView(db)
    print("✓ Dashboard")
    
    academics_view = AcademicsView(db)
    print("✓ Academics")
    
    assignments_view = AssignmentsView(db)
    print("✓ Assignments")
    
    calendar_view = CalendarView(db)
    print("✓ Calendar")
    
    weekly_schedule_view = WeeklyScheduleView(db)
    print("✓ Weekly Schedule")
    
    projects_view = ProjectsView(db)
    print("✓ Projects")
    
    finance_view = FinanceView(db)
    print("✓ Finance")
    
    focus_view = FocusTimerView(db)
    print("✓ Focus Timer")
    
    focus_history_view = FocusHistoryView(db)
    print("✓ Focus History")
    
    study_stats_view = StudyStatsView(db)
    print("✓ Study Stats")
    
    goals_view = GoalsView(db)
    print("✓ Goals")
    
    time_tracking_view = TimeTrackingView(db)
    print("✓ Time Tracking")
    
    library_view = LibraryView(db)
    print("✓ Library")
    
    notes_view = NotesView(db)
    print("✓ Notes")
    
    settings_view = SettingsView(db)
    print("✓ Settings")
    
    print("\n✅ All views initialized successfully!")
    
except Exception as e:
    print(f"\n❌ Error occurred:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
