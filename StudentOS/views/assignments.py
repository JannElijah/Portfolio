import flet as ft
from datetime import datetime
from .file_attachment import FileAttachmentWidget
from .reminder_dialog import open_reminders_dialog

class AssignmentsView(ft.Container):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20
        self.current_assignment_id = None
        
        # Form fields
        self.assignment_subject = ft.TextField(label="Subject", width=300)
        self.assignment_title = ft.TextField(label="Assignment Title", width=300)
        self.assignment_description = ft.TextField(label="Description", multiline=True, width=300, height=80)
        self.assignment_due_date = ft.TextField(
            label="Due Date (YYYY-MM-DD)",
            width=300,
            value=datetime.now().strftime("%Y-%m-%d")
        )
        self.assignment_max_grade = ft.TextField(label="Max Grade", width=300, value="100")
        
        # File attachment widget
        self.file_widget = FileAttachmentWidget(
            db=self.db, 
            entity_type="assignment",
            on_file_change=self.on_file_change
        )
        
        self.assignments_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)
        
        self.content = ft.Column(
            [
                ft.Text("📝 Assignment Tracker", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                ft.Row(
                    [
                        # Left panel - Add Assignment
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Add New Assignment", size=20, weight=ft.FontWeight.BOLD),
                                    self.assignment_subject,
                                    self.assignment_title,
                                    self.assignment_description,
                                    self.assignment_due_date,
                                    self.assignment_max_grade,
                                    ft.ElevatedButton(
                                        "Add Assignment",
                                        icon=ft.Icons.ADD_CIRCLE,
                                        on_click=self.add_assignment,
                                        bgcolor=ft.Colors.GREEN_700,
                                        color="#FFFFFF"
                                    ),
                                    ft.Divider(),
                                    self.file_widget,
                                ],
                                spacing=15,
                                scroll=ft.ScrollMode.AUTO,
                            ),
                            bgcolor=ft.Colors.BLUE_GREY_900,
                            padding=20,
                            border_radius=10,
                            width=420,
                        ),
                        
                        # Right panel - Assignments List
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text("My Assignments", size=20, weight=ft.FontWeight.BOLD),
                                            ft.IconButton(
                                                icon=ft.Icons.REFRESH,
                                                on_click=lambda _: self.load_assignments(),
                                                tooltip="Refresh assignments"
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    self.assignments_list,
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
        
        # Don't load assignments in constructor - will be loaded when view is displayed
        # self.load_assignments()
    
    def add_assignment(self, e):
        """Add new assignment to database"""
        if not self.assignment_subject.value or not self.assignment_title.value:
            if hasattr(self.page, 'snack_bar'):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ Please fill in subject and title", color="#FFFFFF"),
                    bgcolor=ft.Colors.RED_700,
                )
                self.page.snack_bar.open = True
                self.page.update()
            return
        
        try:
            max_grade = float(self.assignment_max_grade.value)
        except:
            max_grade = 100.0
        
        assignment_id = self.db.add_assignment(
            subject=self.assignment_subject.value,
            title=self.assignment_title.value,
            description=self.assignment_description.value or "",
            due_date=self.assignment_due_date.value,
            max_grade=max_grade
        )
        
        # Set the assignment ID for file attachments
        self.current_assignment_id = assignment_id
        self.file_widget.set_entity_id(assignment_id)
        
        # Clear form
        self.assignment_subject.value = ""
        self.assignment_title.value = ""
        self.assignment_description.value = ""
        self.assignment_due_date.value = datetime.now().strftime("%Y-%m-%d")
        self.assignment_max_grade.value = "100"
        
        self.load_assignments()
        
        if hasattr(self.page, 'snack_bar'):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Assignment added successfully! You can now attach files.", color="#FFFFFF"),
                bgcolor=ft.Colors.GREEN_700,
            )
            self.page.snack_bar.open = True
        self.update()
    
    def on_file_change(self):
        """Called when files are added/removed"""
        # Refresh assignments list to show file indicators
        self.load_assignments()
    
    def load_assignments(self):
        """Load and display assignments from database"""
        self.assignments_list.controls.clear()
        assignments = self.db.get_assignments()
        
        if not assignments:
            self.assignments_list.controls.append(
                ft.Text("No assignments yet", italic=True, color=ft.Colors.GREY_400)
            )
        else:
            for assignment_id, subject, title, description, due_date, grade, max_grade, status, submission_date in assignments:
                # Parse due date
                try:
                    due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
                    date_str = due_datetime.strftime("%b %d, %Y")
                    
                    # Check if overdue
                    is_overdue = due_datetime < datetime.now() and status == "pending"
                    
                except:
                    date_str = due_date
                    is_overdue = False
                
                # Status color
                status_colors = {
                    "pending": ft.Colors.ORANGE_400,
                    "submitted": ft.Colors.BLUE_400,
                    "graded": ft.Colors.GREEN_400,
                }
                status_color = status_colors.get(status, ft.Colors.GREY_400)
                
                # Grade display
                grade_display = ""
                if grade is not None and max_grade:
                    percentage = (grade / max_grade) * 100
                    grade_display = f"Grade: {grade}/{max_grade} ({percentage:.1f}%)"
                
                # File attachments & reminders count
                file_attachments = self.db.get_file_attachments("assignment", assignment_id)
                file_count = len(file_attachments)
                rem_count = len(self.db.get_reminders("assignment", assignment_id))
                
                assignment_card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(subject, weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLUE_300),
                                    ft.Row([
                                        ft.Container(
                                            content=ft.Text(f"🔔 {rem_count}", size=11, color="#FFFFFF"),
                                            bgcolor=ft.Colors.INDIGO_600,
                                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                            border_radius=10,
                                            visible=rem_count > 0,
                                        ),
                                        # File attachment indicator
                                        ft.Container(
                                            content=ft.Row([
                                                ft.Icon(ft.Icons.ATTACH_FILE, size=14, color="#FFFFFF"),
                                                ft.Text(str(file_count), size=12, color="#FFFFFF"),
                                            ], spacing=4),
                                            bgcolor=ft.Colors.BLUE_600,
                                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                            border_radius=10,
                                            visible=file_count > 0,
                                        ),
                                        ft.Container(
                                            content=ft.Text(status.upper(), size=12, color="#FFFFFF"),
                                            bgcolor=status_color,
                                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                            border_radius=5,
                                        ),
                                    ], spacing=8),
                                ],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(description, size=13, color=ft.Colors.GREY_300) if description else None,
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=ft.Colors.RED_400 if is_overdue else ft.Colors.GREY_400),
                                    ft.Text(
                                        f"Due: {date_str}",
                                        size=14,
                                        color=ft.Colors.RED_400 if is_overdue else ft.Colors.GREY_400,
                                        weight=ft.FontWeight.BOLD if is_overdue else ft.FontWeight.NORMAL
                                    ),
                                ],
                                spacing=5,
                            ),
                            ft.Text(grade_display, size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_300) if grade_display else None,
                            
                            # Action buttons
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "Submit",
                                        icon=ft.Icons.UPLOAD,
                                        on_click=lambda _, aid=assignment_id: self.submit_assignment(aid),
                                        bgcolor=ft.Colors.BLUE_700,
                                        color="#FFFFFF",
                                        disabled=(status != "pending")
                                    ) if status == "pending" else None,
                                    ft.ElevatedButton(
                                        "Reminders",
                                        icon=ft.Icons.NOTIFICATIONS_ACTIVE,
                                        on_click=lambda _, aid=assignment_id, t=title: open_reminders_dialog(
                                            self.page, self.db, "assignment", aid, t, on_change=self.load_assignments
                                        ),
                                        bgcolor=ft.Colors.INDIGO_700,
                                        color="#FFFFFF",
                                    ),
                                    ft.ElevatedButton(
                                        "Add Grade",
                                        icon=ft.Icons.GRADE,
                                        on_click=lambda _, aid=assignment_id, mg=max_grade: self.show_grade_dialog(aid, mg),
                                        bgcolor=ft.Colors.GREEN_700,
                                        color="#FFFFFF",
                                        disabled=(status == "pending")
                                    ) if status != "pending" else None,
                                ],
                                spacing=10,
                            )
                        ],
                        spacing=8,
                    ),
                    bgcolor=ft.Colors.RED_900 if is_overdue else ft.Colors.BLUE_GREY_800,
                    padding=15,
                    border_radius=10,
                    border=ft.border.all(2, ft.Colors.RED_400 if is_overdue else status_color),
                )
                
                self.assignments_list.controls.append(assignment_card)
        
        try:
            if self.page:
                self.update()
        except RuntimeError:
            pass
    
    def submit_assignment(self, assignment_id):
        """Mark assignment as submitted"""
        self.db.submit_assignment(assignment_id)
        self.load_assignments()
        
        if hasattr(self.page, 'snack_bar'):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Assignment submitted!", color="#FFFFFF"),
                bgcolor=ft.Colors.BLUE_700,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def show_grade_dialog(self, assignment_id, max_grade):
        """Show dialog to add grade"""
        grade_field = ft.TextField(label=f"Grade (out of {max_grade})", width=200, keyboard_type=ft.KeyboardType.NUMBER)
        
        def save_grade(e):
            try:
                grade = float(grade_field.value)
                self.db.update_assignment_grade(assignment_id, grade)
                self.page.dialog.open = False
                self.load_assignments()
                
                if hasattr(self.page, 'snack_bar'):
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("✅ Grade added!", color="#FFFFFF"),
                        bgcolor=ft.Colors.GREEN_700,
                    )
                    self.page.snack_bar.open = True
                self.page.update()
            except:
                if hasattr(self.page, 'snack_bar'):
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("⚠️ Invalid grade", color="#FFFFFF"),
                        bgcolor=ft.Colors.RED_700,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Add Grade"),
            content=grade_field,
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(self.page.dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Save", on_click=save_grade, bgcolor=ft.Colors.GREEN_700, color="#FFFFFF"),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
