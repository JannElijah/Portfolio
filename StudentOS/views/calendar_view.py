import flet as ft
from datetime import datetime, timedelta
from .reminder_dialog import open_reminders_dialog

class CalendarView(ft.Container):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20
        
        # Event form fields
        self.event_title = ft.TextField(label="Event Title", width=300)
        self.event_description = ft.TextField(label="Description", multiline=True, width=300)
        self.event_type = ft.Dropdown(
            label="Event Type",
            width=300,
            options=[],  # Will be loaded from database
            value=None
        )
        
        # Load categories from database
        self.load_categories()
        self.event_date = ft.TextField(
            label="Start Date (YYYY-MM-DD)",
            width=300,
            value=datetime.now().strftime("%Y-%m-%d")
        )
        self.event_time = ft.TextField(label="Time (HH:MM)", width=300, value="09:00")
        self.event_location = ft.TextField(label="Location (Optional)", width=300)
        
        # Recurrence options
        self.recurrence_pattern = ft.Dropdown(
            label="Repeat",
            width=300,
            options=[
                ft.dropdown.Option("none", "No Repeat"),
                ft.dropdown.Option("daily", "Daily"),
                ft.dropdown.Option("weekly", "Weekly"),
                ft.dropdown.Option("monthly", "Monthly"),
            ],
            value="none"
        )
        self.recurrence_end = ft.TextField(
            label="Repeat Until (YYYY-MM-DD)",
            width=300,
            visible=False
        )
        
        # Update visibility when recurrence changes
        def on_recurrence_change(e):
            self.recurrence_end.visible = self.recurrence_pattern.value != "none"
            if hasattr(self, 'page') and self.page:
                self.update()
        
        self.recurrence_pattern.on_change = on_recurrence_change
        
        self.events_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)
        
        self.content = ft.Column(
            [
                ft.Text("📅 Calendar & Events", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                ft.Row(
                    [
                        # Left panel - Add Event
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Add New Event", size=20, weight=ft.FontWeight.BOLD),
                                    self.event_title,
                                    self.event_description,
                                    self.event_type,
                                    self.event_date,
                                    self.event_time,
                                    self.event_location,
                                    self.recurrence_pattern,
                                    self.recurrence_end,
                                    ft.ElevatedButton(
                                        "Add Event",
                                        icon=ft.Icons.ADD_CIRCLE,
                                        on_click=self.add_event,
                                        bgcolor=ft.Colors.BLUE_700,
                                        color="#FFFFFF"
                                    ),
                                ],
                                spacing=15,
                            ),
                            bgcolor=ft.Colors.BLUE_GREY_900,
                            padding=20,
                            border_radius=10,
                            width=380,
                        ),
                        
                        # Right panel - Events List
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text("Upcoming Events", size=20, weight=ft.FontWeight.BOLD),
                                            ft.IconButton(
                                                icon=ft.Icons.REFRESH,
                                                on_click=lambda _: self.load_events(),
                                                tooltip="Refresh events"
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    self.events_list,
                                ],
                                spacing=10,
                                scroll=ft.ScrollMode.AUTO,
                            ),
                            bgcolor=ft.Colors.BLUE_GREY_900,
                            padding=20,
                            border_radius=10,
                            expand=True,
                        ),
                    ],
                    spacing=20,
                    expand=True,
                    alignment=ft.MainAxisAlignment.START,
                )
            ],
            spacing=20,
            expand=True,
        )
        
        # Don't load events in constructor - will be loaded when view is displayed
        # self.load_events()
    
    def add_event(self, e):
        """Add new event to database"""
        if not self.event_title.value or not self.event_date.value:
            if hasattr(self.page, 'snack_bar'):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ Please fill in title and date", color="#FFFFFF"),
                    bgcolor=ft.Colors.RED_700,
                )
                self.page.snack_bar.open = True
                self.page.update()
            return
        
        # Combine date and time
        start_datetime = f"{self.event_date.value} {self.event_time.value}"
        
        # Get recurrence parameters
        recurrence_pattern = None if self.recurrence_pattern.value == "none" else self.recurrence_pattern.value
        recurrence_end = self.recurrence_end.value if self.recurrence_end.value and recurrence_pattern else None
        
        self.db.add_event(
            title=self.event_title.value,
            description=self.event_description.value or "",
            event_type=self.event_type.value,
            start_date=start_datetime,
            location=self.event_location.value or "",
            recurrence_pattern=recurrence_pattern,
            recurrence_end_date=recurrence_end
        )
        
        # Clear form
        self.event_title.value = ""
        self.event_description.value = ""
        self.event_date.value = datetime.now().strftime("%Y-%m-%d")
        self.event_time.value = "09:00"
        self.event_location.value = ""
        self.recurrence_pattern.value = "none"
        self.recurrence_end.value = ""
        self.recurrence_end.visible = False
        
        self.load_events()
        
        if hasattr(self.page, 'snack_bar'):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Event added successfully!", color="#FFFFFF"),
                bgcolor=ft.Colors.GREEN_700,
            )
            self.page.snack_bar.open = True
        self.update()
    
    def load_events(self):
        """Load and display events from database"""
        self.events_list.controls.clear()
        events = self.db.get_events()
        
        if not events:
            self.events_list.controls.append(
                ft.Text("No events scheduled yet", italic=True, color=ft.Colors.GREY_400)
            )
        else:
            for event_id, title, description, event_type, start_date, end_date, location, recurrence_pattern, parent_event_id in events:
                # Parse date
                try:
                    event_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
                    date_str = event_datetime.strftime("%b %d, %Y at %I:%M %p")
                    
                    # Check if event is upcoming or past
                    is_upcoming = event_datetime > datetime.now()
                    
                    # Color coding based on type
                    type_colors = {
                        "Exam": ft.Colors.RED_400,
                        "Deadline": ft.Colors.ORANGE_400,
                        "Class": ft.Colors.BLUE_400,
                        "Meeting": ft.Colors.PURPLE_400,
                        "Study Session": ft.Colors.GREEN_400,
                        "Other": ft.Colors.GREY_400,
                    }
                    color = type_colors.get(event_type, ft.Colors.GREY_400)
                    
                except:
                    date_str = start_date
                    is_upcoming = True
                    color = ft.Colors.GREY_400
                
                rem_count = len(self.db.get_reminders("event", event_id))
                event_card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.EVENT, color=color, size=20),
                                    ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
                                    ft.Container(
                                        content=ft.Text(event_type, size=12, color="#FFFFFF"),
                                        bgcolor=color,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=5,
                                    ),
                                    ft.Container(
                                        content=ft.Text(f"🔔 {rem_count}", size=11, color="#FFFFFF"),
                                        bgcolor=ft.Colors.INDIGO_600,
                                        padding=ft.padding.symmetric(horizontal=6, vertical=3),
                                        border_radius=10,
                                        visible=rem_count > 0,
                                    ),
                                ],
                                spacing=10,
                            ),
                            ft.Text(f"📅 {date_str}", size=14, color=ft.Colors.GREY_400),
                            ft.Text(description, size=13) if description else None,
                            ft.Text(f"📍 {location}", size=13, color=ft.Colors.BLUE_300) if location else None,
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.NOTIFICATIONS_ACTIVE,
                                        icon_color=ft.Colors.INDIGO_300,
                                        on_click=lambda _, eid=event_id, t=title: open_reminders_dialog(
                                            self.page, self.db, "event", eid, t, on_change=self.load_events
                                        ),
                                        tooltip="Manage event reminders"
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        icon_color=ft.Colors.RED_400,
                                        on_click=lambda _, eid=event_id: self.delete_event(eid),
                                        tooltip="Delete event"
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.END,
                            )
                        ],
                        spacing=5,
                    ),
                    bgcolor=ft.Colors.BLUE_GREY_800 if is_upcoming else ft.Colors.GREY_800,
                    padding=15,
                    border_radius=10,
                    border=ft.border.all(1, color if is_upcoming else ft.Colors.GREY_700),
                )
                
                self.events_list.controls.append(event_card)
        
        try:
            if self.page:
                self.update()
        except RuntimeError:
            pass
    
    def delete_event(self, event_id):
        """Delete event from database"""
        self.db.delete_event(event_id)
        self.load_events()
        
        if hasattr(self.page, 'snack_bar'):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("🗑️ Event deleted", color="#FFFFFF"),
                bgcolor=ft.Colors.ORANGE_700,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def load_categories(self):
        """Load event categories from database"""
        try:
            # Get event categories from database
            category_names = self.db.get_category_names("event")
            
            # Create dropdown options
            self.event_type.options = [
                ft.dropdown.Option(name) for name in category_names
            ]
            
            # Set default value if categories exist
            if category_names:
                self.event_type.value = category_names[0]
            
        except:
            # Fallback to default categories if database fails
            self.event_type.options = [
                ft.dropdown.Option("Class"),
                ft.dropdown.Option("Exam"),
                ft.dropdown.Option("Meeting"),
                ft.dropdown.Option("Study Session"),
            ]
            self.event_type.value = "Class"
