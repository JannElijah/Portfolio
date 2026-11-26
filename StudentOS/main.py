import flet as ft
from database import DatabaseManager
from notifications import NotificationManager
from views.dashboard import DashboardView
from views.academics import AcademicsView
from views.projects import ProjectsView
from views.finance import ExpenseTracker
from views.focus import FocusView
from views.library import LibraryView
from views.calendar_view import CalendarView
from views.weekly_schedule import WeeklyScheduleView
from views.assignments import AssignmentsView
from views.notes import NotesView
from views.settings import SettingsView
from views.focus_history import FocusHistoryView
from views.study_stats import StudyStatsView
from views.goals import GoalsView
from views.time_tracking import TimeTrackingView
from views.categories import CategoriesView
from views.quick_tasks import QuickTasksView

def main(page: ft.Page):
    page.title = "StudentOS — Academic & Productivity Workspace"
    page.padding = 0
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
    page.bgcolor = "#0F172A"
    
    # Initialize Database
    db = DatabaseManager()

    
    # Initialize Notification Manager
    notification_manager = NotificationManager(db)
    notification_manager.start_background_checks()
    
    # Load theme from settings
    saved_theme = db.get_setting("theme") or "dark"
    page.theme_mode = saved_theme

    # Views
    dashboard_view = DashboardView(db)
    academics_view = AcademicsView(db)
    projects_view = ProjectsView(db)
    finance_view = ExpenseTracker(db)
    focus_view = FocusView(db, notification_manager)
    focus_history_view = FocusHistoryView(db)
    study_stats_view = StudyStatsView(db)
    goals_view = GoalsView(db)
    time_tracking_view = TimeTrackingView(db)
    library_view = LibraryView(db)
    calendar_view = CalendarView(db)
    weekly_schedule_view = WeeklyScheduleView(db)
    assignments_view = AssignmentsView(db)
    notes_view = NotesView(db)
    categories_view = CategoriesView(db)
    quick_tasks_view = QuickTasksView(db)
    settings_view = SettingsView(db, page)

    # Main Content Area
    content_area = ft.Container(expand=True, padding=10)
    
    # Search Dialog
    search_field = ft.TextField(
        label="Search",
        hint_text="Search tasks, projects, assignments...",
        autofocus=True,
        width=500,
        on_change=lambda e: perform_search(e.control.value),
    )
    
    search_results = ft.Column(scroll=ft.ScrollMode.AUTO, height=300)
    
    search_dialog = ft.AlertDialog(
        title=ft.Text("🔍 Search", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                search_field,
                ft.Divider(),
                search_results,
            ]),
            width=500,
        ),
        actions=[
            ft.TextButton("Close", on_click=lambda _: close_search()),
        ],
    )
    
    def perform_search(query):
        """Search across all data"""
        search_results.controls.clear()
        
        if not query or len(query) < 2:
            search_results.controls.append(ft.Text("Type to search...", italic=True, color=ft.Colors.GREY_400))
            page.update()
            return
        
        query_lower = query.lower()
        found_items = []
        
        # Search tasks
        try:
            for task_id, time_slot, task_name, status in db.get_tasks_for_today():
                if query_lower in task_name.lower():
                    found_items.append(("Task", task_name, time_slot))
        except: pass
        
        # Search projects
        try:
            for proj_id, name, stack, status in db.get_projects():
                if query_lower in name.lower() or query_lower in stack.lower():
                    found_items.append(("Project", name, stack))
        except: pass
        
        # Search assignments
        try:
            for assign in db.get_assignments():
                if query_lower in assign[2].lower():
                    found_items.append(("Assignment", assign[2], assign[1]))
        except: pass
        
        # Search events
        try:
            for event in db.get_events():
                if query_lower in event[1].lower():
                    found_items.append(("Event", event[1], event[4]))
        except: pass
        
        # Search notes
        try:
            for note in db.get_notes():
                if query_lower in note[2].lower() or query_lower in note[3].lower():
                    found_items.append(("Note", note[2], note[1] or "General"))
        except: pass
        
        # Display results
        if not found_items:
            search_results.controls.append(ft.Text("No results found", italic=True, color=ft.Colors.GREY_400))
        else:
            for item_type, title, detail in found_items:
                search_results.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(item_type, weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.BLUE_300),
                            ft.Text(title, size=14),
                            ft.Text(detail, size=12, color=ft.Colors.GREY_400),
                        ], spacing=10),
                        padding=10,
                        bgcolor=ft.Colors.BLUE_GREY_900,
                        border_radius=5,
                    )
                )
        
        page.update()
    
    def close_search():
        """Close search dialog"""
        search_dialog.open = False
        search_field.value = ""
        search_results.controls.clear()
        page.update()
    
    def open_search():
        """Open search dialog"""
        page.dialog = search_dialog
        search_dialog.open = True
        search_field.value = ""
        search_results.controls.clear()
        search_results.controls.append(ft.Text("Type to search...", italic=True, color=ft.Colors.GREY_400))
        page.update()
    
    # Quick Capture Dialog
    quick_capture_field = ft.TextField(
        label="Quick Capture",
        hint_text="Type your task and press Enter...",
        autofocus=True,
        multiline=False,
        on_submit=lambda e: save_quick_capture(e.control.value),
    )
    
    quick_capture_dialog = ft.AlertDialog(
        title=ft.Text("⚡ Quick Capture", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=quick_capture_field,
            width=400,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda _: close_quick_capture()),
            ft.ElevatedButton(
                "Save",
                icon=ft.Icons.SAVE,
                on_click=lambda _: save_quick_capture(quick_capture_field.value),
                bgcolor=ft.Colors.BLUE_700,
                color="#FFFFFF",
            ),
        ],
    )
    
    def save_quick_capture(task_text):
        """Save quick capture task to database"""
        if task_text and task_text.strip():
            db.add_quick_task(task_text.strip())
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✅ Quick task saved: {task_text}", color="#FFFFFF"),
                bgcolor=ft.Colors.GREEN_700,
            )
            page.snack_bar.open = True
            close_quick_capture()
            # Refresh dashboard if it's the current view
            if content_area.content == dashboard_view:
                dashboard_view.refresh_data()
            page.update()
    
    def close_quick_capture():
        """Close quick capture dialog"""
        quick_capture_dialog.open = False
        quick_capture_field.value = ""
        page.update()
    
    def open_quick_capture():
        """Open quick capture dialog"""
        page.dialog = quick_capture_dialog
        quick_capture_dialog.open = True
        quick_capture_field.value = ""
        page.update()
    
    # Keyboard event handler
    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Space" and e.ctrl:
            open_quick_capture()
        elif e.key == "F" and e.ctrl:
            open_search()
    
    page.on_keyboard_event = on_keyboard

    def change_view(e):
        index = e.control.selected_index
        view = [
            dashboard_view,
            academics_view,
            assignments_view,
            calendar_view,
            weekly_schedule_view,
            projects_view,
            finance_view,
            focus_view,
            focus_history_view,
            study_stats_view,
            goals_view,
            time_tracking_view,
            library_view,
            notes_view,
            quick_tasks_view,
            categories_view,
            settings_view,
        ][index]
        
        content_area.content = view
        content_area.update()
        
        # Load initial data after view is added to page
        if hasattr(view, 'load_events'):
            view.load_events()
        elif hasattr(view, 'load_assignments'):
            view.load_assignments()
        elif hasattr(view, 'load_content'):
            view.load_content()
        elif hasattr(view, 'refresh_data'):
            view.refresh_data()
        elif hasattr(view, 'load_sessions'):
            view.load_sessions()
        elif hasattr(view, 'load_statistics'):
            view.load_statistics()
        elif hasattr(view, 'load_goals'):
            view.load_goals()
        elif hasattr(view, 'load_time_entries'):
            view.load_time_entries()

    # Sidebar
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        on_change=change_view,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD, 
                selected_icon=ft.Icons.DASHBOARD, 
                label="Dashboard"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SCHOOL, 
                selected_icon=ft.Icons.SCHOOL, 
                label="Academics"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.ASSIGNMENT, 
                selected_icon=ft.Icons.ASSIGNMENT, 
                label="Assignments"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CALENDAR_TODAY, 
                selected_icon=ft.Icons.CALENDAR_TODAY, 
                label="Calendar"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.VIEW_WEEK, 
                selected_icon=ft.Icons.VIEW_WEEK, 
                label="Weekly"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CODE, 
                selected_icon=ft.Icons.CODE, 
                label="Projects"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.ATTACH_MONEY, 
                selected_icon=ft.Icons.ATTACH_MONEY, 
                label="Finance"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.TIMER, 
                selected_icon=ft.Icons.TIMER, 
                label="Focus"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.HISTORY, 
                selected_icon=ft.Icons.HISTORY, 
                label="History"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.BAR_CHART, 
                selected_icon=ft.Icons.BAR_CHART, 
                label="Stats"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.FLAG, 
                selected_icon=ft.Icons.FLAG, 
                label="Goals"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.ACCESS_TIME, 
                selected_icon=ft.Icons.ACCESS_TIME, 
                label="Time"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.LIBRARY_BOOKS, 
                selected_icon=ft.Icons.LIBRARY_BOOKS, 
                label="Library"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.NOTE, 
                selected_icon=ft.Icons.NOTE, 
                label="Notes"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.TASK_ALT, 
                selected_icon=ft.Icons.TASK_ALT, 
                label="Quick Tasks"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CATEGORY, 
                selected_icon=ft.Icons.CATEGORY, 
                label="Categories"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS, 
                selected_icon=ft.Icons.SETTINGS, 
                label="Settings"
            ),
        ],
    )

    # Set initial view
    content_area.content = dashboard_view

    # Layout
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                content_area,
            ],
            expand=True,
        )
    )
    
    # Show shortcuts hint
    page.snack_bar = ft.SnackBar(
        content=ft.Text("💡 Shortcuts: Ctrl+Space (Quick Capture) | Ctrl+F (Search)", color="#FFFFFF"),
        bgcolor=ft.Colors.BLUE_700,
    )
    page.snack_bar.open = True
    page.update()

if __name__ == "__main__":
    ft.app(target=main)  # Using app() for now, run() requires view parameter in this version
