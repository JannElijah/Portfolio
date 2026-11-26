"""Weekly Schedule View for StudentOS"""
import flet as ft
from datetime import datetime, timedelta

class WeeklyScheduleView(ft.Container):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20
        
        # Current week start (Monday)
        today = datetime.now()
        self.current_week_start = today - timedelta(days=today.weekday())
        
        # Event type colors
        self.event_colors = {
            "Exam": ft.Colors.RED_700,
            "Deadline": ft.Colors.ORANGE_700,
            "Class": ft.Colors.BLUE_700,
            "Meeting": ft.Colors.PURPLE_700,
            "Study Session": ft.Colors.GREEN_700,
            "Other": ft.Colors.GREY_700,
        }
        
        # Week grid
        self.week_grid = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        
        self.build_ui()
    
    def build_ui(self):
        """Build the weekly schedule UI"""
        # Header with navigation
        header = ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=self.previous_week,
                tooltip="Previous Week"
            ),
            ft.Text(
                self.get_week_title(),
                size=20,
                weight=ft.FontWeight.BOLD,
                expand=True,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.IconButton(
                icon=ft.Icons.ARROW_FORWARD,
                on_click=self.next_week,
                tooltip="Next Week"
            ),
            ft.IconButton(
                icon=ft.Icons.TODAY,
                on_click=self.go_to_today,
                tooltip="Go to Today",
                bgcolor=ft.Colors.BLUE_700,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        self.content = ft.Column([
            ft.Text("📅 Weekly Schedule", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            header,
            ft.Divider(),
            self.week_grid,
        ], spacing=15, expand=True)
        
        self.load_week()
    
    def get_week_title(self):
        """Get week title string"""
        week_end = self.current_week_start + timedelta(days=6)
        return f"{self.current_week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
    
    def previous_week(self, e):
        """Navigate to previous week"""
        self.current_week_start -= timedelta(weeks=1)
        self.load_week()
    
    def next_week(self, e):
        """Navigate to next week"""
        self.current_week_start += timedelta(weeks=1)
        self.load_week()
    
    def go_to_today(self, e):
        """Go to current week"""
        today = datetime.now()
        self.current_week_start = today - timedelta(days=today.weekday())
        self.load_week()
    
    def load_week(self):
        """Load events for the current week"""
        self.week_grid.controls.clear()
        
        # Get events for this week
        week_start_str = self.current_week_start.strftime("%Y-%m-%d")
        events = self.db.get_events_for_week(week_start_str)
        
        # Organize events by day
        events_by_day = {i: [] for i in range(7)}
        for event in events:
            # Handle both "YYYY-MM-DD" and "YYYY-MM-DD HH:MM" formats
            date_str = event[4].split()[0] if ' ' in event[4] else event[4]
            event_date = datetime.strptime(date_str, "%Y-%m-%d")
            day_offset = (event_date - self.current_week_start).days
            if 0 <= day_offset < 7:
                events_by_day[day_offset].append(event)
        
        # Update header to show current week
        if hasattr(self, 'content') and len(self.content.controls) > 2:
            header_row = self.content.controls[2]
            if isinstance(header_row, ft.Row) and len(header_row.controls) > 1:
                header_row.controls[1].value = self.get_week_title()
        
        # Create day columns
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        today = datetime.now().date()
        
        day_columns = []
        for i in range(7):
            day_date = self.current_week_start + timedelta(days=i)
            is_today = day_date.date() == today
            
            # Day header
            day_header = ft.Container(
                content=ft.Column([
                    ft.Text(days[i], size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(day_date.strftime("%b %d"), size=12, color=ft.Colors.GREY_400),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
                padding=10,
                bgcolor=ft.Colors.BLUE_700 if is_today else ft.Colors.BLUE_GREY_900,
                border_radius=8,
            )
            
            # Events for this day
            day_events = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
            
            if events_by_day[i]:
                for event in events_by_day[i]:
                    event_card = self.create_event_card(event)
                    day_events.controls.append(event_card)
            else:
                day_events.controls.append(
                    ft.Container(
                        content=ft.Text("No events", size=12, color=ft.Colors.GREY_600, italic=True),
                        padding=10,
                    )
                )
            
            # Day container
            day_container = ft.Container(
                content=ft.Column([day_header, day_events], spacing=10),
                expand=True,
                padding=5,
            )
            
            day_columns.append(day_container)
        
        # Add days in a row
        self.week_grid.controls.append(
            ft.Row(
                day_columns,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
        )
        
        # Update only if already on page
        try:
            if self.page:
                self.update()
        except:
            pass  # Not yet added to page
    
    def create_event_card(self, event):
        """Create an event card"""
        if len(event) >= 9:
            # New format with all columns
            event_id, title, description, event_type, start_date, end_date, location, recurrence_pattern, parent_event_id = event[:9]
        else:
            # Legacy format for weekly view
            event_id, title, description, event_type, start_date, end_date, location = event
        
        color = self.event_colors.get(event_type, ft.Colors.GREY_700)
        
        # Event type badge
        type_badge = ft.Container(
            content=ft.Text(event_type or "Event", size=10, color="white", weight=ft.FontWeight.BOLD),
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            bgcolor=color,
            border_radius=12,
        )
        
        # Location if available
        location_row = None
        if location:
            location_row = ft.Row([
                ft.Icon(ft.Icons.LOCATION_ON, size=14, color=ft.Colors.GREY_500),
                ft.Text(location, size=11, color=ft.Colors.GREY_500),
            ], spacing=5)
        
        card_content = ft.Column([
            ft.Row([
                type_badge,
            ]),
            ft.Text(title, size=13, weight=ft.FontWeight.BOLD, max_lines=2),
        ], spacing=5)
        
        if location_row:
            card_content.controls.append(location_row)
        
        if description:
            card_content.controls.append(
                ft.Text(description, size=11, color=ft.Colors.GREY_400, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)
            )
        
        return ft.Container(
            content=card_content,
            padding=10,
            bgcolor=ft.Colors.BLUE_GREY_900,
            border_radius=8,
            border=ft.border.all(2, color),
            on_click=lambda e: self.show_event_details(event),
        )
    
    def show_event_details(self, event):
        """Show event details in a dialog"""
        event_id, title, description, event_type, start_date, end_date, location = event
        
        details = ft.Column([
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([
                ft.Icon(ft.Icons.CATEGORY, size=16),
                ft.Text(f"Type: {event_type or 'Event'}", size=14),
            ], spacing=10),
            ft.Row([
                ft.Icon(ft.Icons.CALENDAR_TODAY, size=16),
                ft.Text(f"Date: {start_date}", size=14),
            ], spacing=10),
        ], spacing=10)
        
        if location:
            details.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.LOCATION_ON, size=16),
                    ft.Text(f"Location: {location}", size=14),
                ], spacing=10)
            )
        
        if description:
            details.controls.append(ft.Divider())
            details.controls.append(ft.Text("Description:", size=14, weight=ft.FontWeight.BOLD))
            details.controls.append(ft.Text(description, size=13, color=ft.Colors.GREY_400))
        
        dialog = ft.AlertDialog(
            title=ft.Text("Event Details"),
            content=details,
            actions=[
                ft.TextButton("Close", on_click=lambda e: self.close_dialog()),
            ],
        )
        
        if hasattr(self, 'page') and self.page:
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
    
    def close_dialog(self):
        """Close the current dialog"""
        if hasattr(self, 'page') and self.page and self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
