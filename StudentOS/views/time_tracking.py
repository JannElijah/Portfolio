import flet as ft
from datetime import datetime

class TimeTrackingView(ft.Column):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.spacing = 20
        
        # Timer state
        self.is_tracking = False
        self.start_time = None
        self.current_entity_type = None
        self.current_entity_id = None
        self.current_entity_name = None
        
        # Form fields
        self.entity_type = ft.Dropdown(
            label="Track Time For",
            width=300,
            options=[
                ft.dropdown.Option("subject", "Subject"),
                ft.dropdown.Option("project", "Project"),
                ft.dropdown.Option("assignment", "Assignment"),
            ],
        )
        self.entity_type.on_change = self.on_type_change
        
        self.entity_selector = ft.Dropdown(
            label="Select Item",
            width=300,
            options=[],
        )
        
        self.notes_field = ft.TextField(
            label="Notes (optional)",
            width=300,
            multiline=True,
            min_lines=2,
            max_lines=3,
        )
        
        # Timer display
        self.timer_display = ft.Text("00:00:00", size=48, weight=ft.FontWeight.BOLD)
        self.timer_button = ft.ElevatedButton(
            "Start Tracking",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self.toggle_timer,
            bgcolor=ft.Colors.GREEN_700,
            color="#FFFFFF",
            width=200,
        )
        
        # Time entries list  
        self.time_entries_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)
        
        # Summary stats
        self.total_time_text = ft.Text("0h 0m", size=24, weight=ft.FontWeight.BOLD)
        self.entries_count_text = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
        
        self.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text("⏱️ Time Tracking", size=24, weight=ft.FontWeight.BOLD),
                    
                    ft.Row(
                        [
                            # Left panel - Timer
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Time Tracker", size=18, weight=ft.FontWeight.BOLD),
                                    
                                    self.timer_display,
                                    
                                    self.entity_type,
                                    self.entity_selector,
                                    self.notes_field,
                                    
                                    self.timer_button,
                                    
                                    ft.Divider(),
                                    
                                    # Quick stats
                                    ft.Row(
                                        [
                                            ft.Column([
                                                ft.Text("Total Time", size=12, color=ft.Colors.GREY_400),
                                                self.total_time_text,
                                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                            
                                            ft.VerticalDivider(),
                                            
                                            ft.Column([
                                                ft.Text("Entries", size=12, color=ft.Colors.GREY_400),
                                                self.entries_count_text,
                                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                    ),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                                bgcolor=ft.Colors.BLUE_GREY_900,
                                padding=20,
                                border_radius=10,
                                width=380,
                            ),
                            
                            # Right panel - Time Entries
                            ft.Container(
                                content=ft.Column([
                                    ft.Row(
                                        [
                                            ft.Text("Recent Time Entries", size=18, weight=ft.FontWeight.BOLD),
                                            ft.IconButton(
                                                icon=ft.Icons.REFRESH,
                                                on_click=lambda _: self.load_time_entries(),
                                                tooltip="Refresh"
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    self.time_entries_list,
                                ], scroll=ft.ScrollMode.AUTO),
                                bgcolor=ft.Colors.BLUE_GREY_900,
                                padding=20,
                                border_radius=10,
                                expand=True,
                            ),
                        ],
                        spacing=20,
                        expand=True,
                    ),
                ]),
                padding=20,
            )
        ]
    
    def on_type_change(self, e):
        """Load items based on selected type"""
        self.entity_selector.options.clear()
        
        if self.entity_type.value == "subject":
            subjects = self.db.get_subjects()
            for subj_id, name, code, room, schedule, credits in subjects:
                self.entity_selector.options.append(
                    ft.dropdown.Option(f"subj_{subj_id}", f"{name} ({code})")
                )
        
        elif self.entity_type.value == "project":
            projects = self.db.get_projects()
            for proj_id, name, stack, status in projects:
                self.entity_selector.options.append(
                    ft.dropdown.Option(f"proj_{proj_id}", name)
                )
        
        elif self.entity_type.value == "assignment":
            assignments = self.db.get_assignments()
            for assign_id, subject, title, desc, due, grade, max_grade, status, submission in assignments:
                self.entity_selector.options.append(
                    ft.dropdown.Option(f"assign_{assign_id}", f"{subject}: {title}")
                )
        
        self.entity_selector.update()
    
    def toggle_timer(self, e):
        """Start or stop the timer"""
        if not self.is_tracking:
            # Start timer
            if not self.entity_type.value or not self.entity_selector.value:
                if hasattr(self.page, 'snack_bar'):
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("⚠️ Please select what to track", color="#FFFFFF"),
                        bgcolor=ft.Colors.RED_700,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                return
            
            self.is_tracking = True
            self.start_time = datetime.now()
            self.current_entity_type = self.entity_type.value
            
            # Parse entity ID from selector value
            entity_value = self.entity_selector.value
            self.current_entity_id = int(entity_value.split('_')[1])
            self.current_entity_name = self.entity_selector.options[[opt.key for opt in self.entity_selector.options].index(entity_value)].text
            
            self.timer_button.text = "Stop Tracking"
            self.timer_button.icon = ft.Icons.STOP
            self.timer_button.bgcolor = ft.Colors.RED_700
            
            # Disable form fields
            self.entity_type.disabled = True
            self.entity_selector.disabled = True
            
        else:
            # Stop timer
            self.is_tracking = False
            end_time = datetime.now()
            duration_seconds = int((end_time - self.start_time).total_seconds())
            duration_minutes = duration_seconds // 60
            
            # Save time entry
            self.db.add_time_entry(
                entity_type=self.current_entity_type,
                entity_id=self.current_entity_id,
                entity_name=self.current_entity_name,
                duration=duration_minutes,
                start_time=self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
                notes=self.notes_field.value or None
            )
            
            self.timer_button.text = "Start Tracking"
            self.timer_button.icon = ft.Icons.PLAY_ARROW
            self.timer_button.bgcolor = ft.Colors.GREEN_700
            
            # Enable form fields
            self.entity_type.disabled = False
            self.entity_selector.disabled = False
            
            # Reset display
            self.timer_display.value = "00:00:00"
            self.notes_field.value = ""
            
            # Reload entries
            self.load_time_entries()
            
            if hasattr(self.page, 'snack_bar'):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ Tracked {duration_minutes} minutes!", color="#FFFFFF"),
                    bgcolor=ft.Colors.GREEN_700,
                )
                self.page.snack_bar.open = True
        
        self.update()
        if hasattr(self.page, 'update'):
            self.page.update()
    
    def load_time_entries(self):
        """Load recent time entries"""
        self.time_entries_list.controls.clear()
        
        entries = self.db.get_time_entries(limit=20)
        
        if entries:
            total_time = 0
            
            for entry_id, entity_type, entity_id, entity_name, duration, start, end, notes in entries:
                total_time += duration
                
                self.time_entries_list.controls.append(
                    self.create_entry_card(entry_id, entity_type, entity_name, duration, start, end, notes)
                )
            
            # Update summary
            hours = total_time // 60
            minutes = total_time % 60
            self.total_time_text.value = f"{hours}h {minutes}m"
            self.entries_count_text.value = str(len(entries))
        else:
            self.time_entries_list.controls.append(
                ft.Text("No time entries yet. Start tracking!", italic=True, color=ft.Colors.GREY_400)
            )
            self.total_time_text.value = "0h 0m"
            self.entries_count_text.value = "0"
        
        self.update()
    
    def create_entry_card(self, entry_id: int, entity_type: str, entity_name: str, duration: int, start: str, end: str, notes: str):
        """Create a time entry card"""
        # Format times
        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
            date_str = start_dt.strftime("%b %d, %Y")
            time_str = f"{start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
        except:
            date_str = start
            time_str = ""
        
        # Duration formatting
        hours = duration // 60
        minutes = duration % 60
        duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes} min"
        
        # Entity type icon
        icons = {
            "subject": ft.Icons.SCHOOL,
            "project": ft.Icons.CODE,
            "assignment": ft.Icons.ASSIGNMENT,
        }
        icon = icons.get(entity_type, ft.Icons.ACCESS_TIME)
        
        return ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Icon(icon, color=ft.Colors.BLUE_400),
                        ft.Column(
                            [
                                ft.Text(entity_name, weight=ft.FontWeight.BOLD),
                                ft.Text(entity_type.capitalize(), size=12, color=ft.Colors.GREY_400),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda _: self.delete_entry(entry_id),
                            tooltip="Delete entry"
                        ),
                    ]
                ),
                ft.Text(date_str, size=12, color=ft.Colors.GREY_400),
                ft.Text(time_str, size=12, color=ft.Colors.GREY_400),
                ft.Container(
                    content=ft.Text(duration_str, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    bgcolor=ft.Colors.GREEN_700,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border_radius=10,
                ),
                ft.Text(notes, size=12, italic=True) if notes else ft.Container(),
            ], spacing=5),
            bgcolor=ft.Colors.BLUE_GREY_900,
            padding=15,
            border_radius=10,
        )
    
    def delete_entry(self, entry_id: int):
        """Delete a time entry"""
        self.db.delete_time_entry(entry_id)
        self.load_time_entries()
        
        if hasattr(self.page, 'snack_bar'):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("🗑️ Entry deleted", color="#FFFFFF"),
                bgcolor=ft.Colors.ORANGE_700,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def did_mount(self):
        """Called when view is added to the page"""
        self.load_time_entries()
