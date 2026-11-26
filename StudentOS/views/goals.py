import flet as ft
from datetime import datetime, timedelta

class GoalsView(ft.Column):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.spacing = 20
        
        # Form fields
        self.goal_type = ft.Dropdown(
            label="Goal Type",
            width=300,
            options=[
                ft.dropdown.Option("study_hours", "Study Hours"),
                ft.dropdown.Option("focus_sessions", "Focus Sessions"),
                ft.dropdown.Option("gpa", "GPA Target"),
                ft.dropdown.Option("assignments_completed", "Assignments Completed"),
                ft.dropdown.Option("notes_created", "Notes Created"),
            ]
        )
        
        self.target_value = ft.TextField(
            label="Target Value",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.time_period = ft.Dropdown(
            label="Time Period",
            width=300,
            options=[
                ft.dropdown.Option("daily", "Daily"),
                ft.dropdown.Option("weekly", "Weekly"),
                ft.dropdown.Option("monthly", "Monthly"),
                ft.dropdown.Option("semester", "Semester"),
            ]
        )
        
        self.start_date = ft.TextField(
            label="Start Date (YYYY-MM-DD)",
            width=300,
            value=datetime.now().strftime("%Y-%m-%d")
        )
        
        self.end_date = ft.TextField(
            label="End Date (YYYY-MM-DD)",
            width=300,
            value=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        )
        
        # Goals list
        self.active_goals = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)
        self.completed_goals = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)
        
        self.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text("🎯 Goals & Milestones", size=24, weight=ft.FontWeight.BOLD),
                    
                    ft.Row(
                        [
                            # Left panel - Create Goal
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Create New Goal", size=18, weight=ft.FontWeight.BOLD),
                                    self.goal_type,
                                    self.target_value,
                                    self.time_period,
                                    self.start_date,
                                    self.end_date,
                                    ft.ElevatedButton(
                                        "Create Goal",
                                        icon=ft.Icons.ADD_TASK,
                                        on_click=self.create_goal,
                                        bgcolor=ft.Colors.GREEN_700,
                                        color="#FFFFFF"
                                    ),
                                ], spacing=15),
                                bgcolor=ft.Colors.BLUE_GREY_900,
                                padding=20,
                                border_radius=10,
                                width=380,
                            ),
                            
                            # Right panel - Goals List
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Active Goals", size=18, weight=ft.FontWeight.BOLD),
                                    self.active_goals,
                                    
                                    ft.Divider(height=20),
                                    
                                    ft.Text("Completed Goals", size=18, weight=ft.FontWeight.BOLD),
                                    self.completed_goals,
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
    
    def create_goal(self, e):
        """Create a new goal"""
        if not self.goal_type.value or not self.target_value.value or not self.time_period.value:
            if hasattr(self.page, 'snack_bar'):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ Please fill in all fields", color="#FFFFFF"),
                    bgcolor=ft.Colors.RED_700,
                )
                self.page.snack_bar.open = True
                self.page.update()
            return
        
        try:
            target = float(self.target_value.value)
        except ValueError:
            if hasattr(self.page, 'snack_bar'):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ Target value must be a number", color="#FFFFFF"),
                    bgcolor=ft.Colors.RED_700,
                )
                self.page.snack_bar.open = True
                self.page.update()
            return
        
        # Create the goal
        self.db.add_goal(
            goal_type=self.goal_type.value,
            target_value=target,
            time_period=self.time_period.value,
            start_date=self.start_date.value,
            end_date=self.end_date.value
        )
        
        # Clear form
        self.goal_type.value = None
        self.target_value.value = ""
        self.time_period.value = None
        
        # Reload goals
        self.load_goals()
        
        if hasattr(self.page, 'snack_bar'):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Goal created successfully!", color="#FFFFFF"),
                bgcolor=ft.Colors.GREEN_700,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def load_goals(self):
        """Load all goals"""
        self.active_goals.controls.clear()
        self.completed_goals.controls.clear()
        
        # Get goals
        active = self.db.get_goals(status='active')
        completed = self.db.get_goals(status='completed')
        
        # Active goals
        if active:
            for goal_id, goal_type, target, current, period, start, end, status in active:
                # Update progress based on goal type
                current_value = self.calculate_current_value(goal_type, start, end)
                self.db.update_goal_progress(goal_id, current_value)
                
                self.active_goals.controls.append(
                    self.create_goal_card(goal_id, goal_type, target, current_value, period, start, end, status)
                )
        else:
            self.active_goals.controls.append(
                ft.Text("No active goals yet. Create one!", italic=True, color=ft.Colors.GREY_400)
            )
        
        # Completed goals
        if completed:
            for goal_id, goal_type, target, current, period, start, end, status in completed:
                self.completed_goals.controls.append(
                    self.create_goal_card(goal_id, goal_type, target, current, period, start, end, status)
                )
        else:
            self.completed_goals.controls.append(
                ft.Text("No completed goals yet", italic=True, color=ft.Colors.GREY_400)
            )
        
        self.update()
    
    def calculate_current_value(self, goal_type: str, start_date: str, end_date: str):
        """Calculate current progress for a goal"""
        # This is a simplified calculation - you can make it more sophisticated
        if goal_type == "study_hours":
            # Get total focus time in the date range
            logs = self.db.get_focus_logs_with_dates(start_date, end_date)
            total_minutes = sum(log[1] for log in logs)
            return total_minutes / 60  # Convert to hours
        
        elif goal_type == "focus_sessions":
            # Get number of focus sessions in the date range
            logs = self.db.get_focus_logs_with_dates(start_date, end_date)
            return len(logs)
        
        elif goal_type == "assignments_completed":
            # Count completed assignments in the date range
            assignments = self.db.get_assignments_filtered(status='completed', start_date=start_date, end_date=end_date)
            return len(assignments)
        
        elif goal_type == "notes_created":
            # This would require date filtering in notes - simplified for now
            notes = self.db.get_notes()
            return len(notes)
        
        elif goal_type == "gpa":
            # Get current GPA
            gpa = self.db.calculate_gpa()
            return gpa
        
        return 0
    
    def create_goal_card(self, goal_id: int, goal_type: str, target: float, current: float, period: str, start: str, end: str, status: str):
        """Create a goal card"""
        # Format goal type for display
        type_labels = {
            "study_hours": "📚 Study Hours",
            "focus_sessions": "🎯 Focus Sessions",
            "gpa": "🎓 GPA Target",
            "assignments_completed": "✅ Assignments Completed",
            "notes_created": "📝 Notes Created",
        }
        type_label = type_labels.get(goal_type, goal_type)
        
        # Calculate progress percentage
        progress = (current / target * 100) if target > 0 else 0
        progress = min(progress, 100)  # Cap at 100%
        
        # Progress color
        if progress >= 100:
            progress_color = ft.Colors.GREEN_700
        elif progress >= 75:
            progress_color = ft.Colors.BLUE_700
        elif progress >= 50:
            progress_color = ft.Colors.ORANGE_700
        else:
            progress_color = ft.Colors.RED_700
        
        return ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Text(type_label, weight=ft.FontWeight.BOLD, size=16),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda _: self.delete_goal(goal_id),
                            tooltip="Delete goal"
                        ),
                    ]
                ),
                ft.Text(f"Period: {period.capitalize()}", size=12, color=ft.Colors.GREY_400),
                ft.Text(f"{start} to {end}", size=12, color=ft.Colors.GREY_400),
                
                ft.Row(
                    [
                        ft.Text(f"Progress: {round(current, 1)} / {target}", size=14),
                        ft.Container(expand=True),
                        ft.Text(f"{round(progress)}%", weight=ft.FontWeight.BOLD, color=progress_color),
                    ]
                ),
                
                # Progress bar
                ft.Container(
                    content=ft.Container(
                        width=progress * 3,  # Scale for visibility
                        height=8,
                        bgcolor=progress_color,
                        border_radius=5,
                    ),
                    width=300,
                    height=8,
                    bgcolor=ft.Colors.GREY_700,
                    border_radius=5,
                ),
            ], spacing=8),
            bgcolor=ft.Colors.BLUE_GREY_900,
            padding=15,
            border_radius=10,
        )
    
    def delete_goal(self, goal_id: int):
        """Delete a goal"""
        self.db.delete_goal(goal_id)
        self.load_goals()
        
        if hasattr(self.page, 'snack_bar'):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("🗑️ Goal deleted", color="#FFFFFF"),
                bgcolor=ft.Colors.ORANGE_700,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def did_mount(self):
        """Called when view is added to the page"""
        self.load_goals()
