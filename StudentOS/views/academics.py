import flet as ft
from utils import UIHelpers, ValidationHelpers, ErrorHandler, show_success, show_error, with_error_handling
from utils import UIHelpers, ValidationHelpers, ErrorHandler, show_success, show_error, with_error_handling
from utils import UIHelpers, ValidationHelpers, ErrorHandler, show_success, show_error, with_error_handling


class AcademicsView(ft.Container):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20
        
        # Dialog form fields
        self.sub_name = ft.TextField(
            label="Subject Name",
            hint_text="e.g., Introduction to Computer Science",
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
        )
        self.sub_code = ft.TextField(
            label="Subject Code",
            hint_text="e.g., CS101",
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
        )
        self.sub_room = ft.TextField(
            label="Room",
            hint_text="e.g., Room 301",
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
        )
        self.sub_sched = ft.TextField(
            label="Schedule",
            hint_text="e.g., Mon/Wed 10:00-11:30",
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
        )
        
        # Subject grid
        self.subject_grid = ft.GridView(
            runs_count=5,
            max_extent=260,
            child_aspect_ratio=1.3,
            spacing=15,
            run_spacing=15,
            expand=True,
        )
        
        # Add subject dialog
        self.add_dialog = ft.AlertDialog(
            title=ft.Text("Add New Subject", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                self.sub_name,
                self.sub_code,
                self.sub_room,
                self.sub_sched,
            ], tight=True, width=400, spacing=15),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=self.close_dialog,
                ),
                ft.ElevatedButton(
                    "Add Subject",
                    icon=ft.Icons.ADD,
                    on_click=self.save_subject,
                    bgcolor=ft.Colors.BLUE_700,
                    color="#FFFFFF",
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # GWA Calculator components
        self.grade_rows = ft.Column(spacing=10)
        self.gwa_result = ft.Text(
            "GWA: 0.00",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.CYAN_400,
        )
        
        # Add initial 4 rows for calculator
        for _ in range(4):
            self.add_grade_row()

        self.build_ui()
    
    def build_ui(self):
        """Build the main UI"""
        # GWA Calculator container
        gwa_container = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("GWA Calculator", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self.grade_rows,
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton(
                            "Add Row",
                            icon=ft.Icons.ADD,
                            on_click=lambda e: self.add_grade_row(update=True),
                            bgcolor=ft.Colors.BLUE_700,
                            color="#FFFFFF",
                        ),
                        ft.ElevatedButton(
                            "Calculate GWA",
                            icon=ft.Icons.CALCULATE,
                            on_click=self.calculate_gwa,
                            bgcolor=ft.Colors.GREEN_700,
                            color="#FFFFFF",
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                    ft.Container(height=10),
                    ft.Container(
                        content=self.gwa_result,
                        alignment=ft.alignment.Alignment(0,0),
                    ),
                ]),
                padding=20,
            ),
            elevation=3,
        )

        self.refresh_subjects(update_ui=False)
        
        # Create main content with scroll
        main_content = ft.Column([
            # Header
            ft.Row([
                ft.Text("📚 Academics", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Add Subject",
                    icon=ft.Icons.ADD,
                    on_click=self.open_dialog,
                    bgcolor=ft.Colors.BLUE_700,
                    color="#FFFFFF",
                ),
            ]),
            ft.Divider(),
            
            # Subjects section
            ft.Row([
                ft.Text("My Subjects", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.Text(f"Total: {len(self.db.get_subjects()) if hasattr(self.db, 'get_subjects') else 0} subjects", 
                        size=14, color=ft.Colors.GREY_400),
            ]),
            ft.Container(
                content=self.subject_grid,
                expand=True,
            ),
            
            ft.Divider(),
            
            # GWA Calculator section
            gwa_container,
        ], spacing=15, expand=True)
        
        self.content = UIHelpers.create_scrollable_container(
            main_content, 
            expand=True
        )

    @with_error_handling
    def refresh_subjects(self, update_ui=True):
        """Load and display all subjects from the database"""
        # Show loading state
        if hasattr(self, 'page') and self.page:
            self.subject_grid.controls.clear()
            self.subject_grid.controls.append(UIHelpers.create_loading_indicator("Loading subjects..."))
            if update_ui:
                self.update()
        
        subjects = self.db.get_subjects()
        
        if not subjects:
            # Show empty state
            self.subject_grid.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            ft.Icons.SCHOOL_OUTLINED,
                            size=80,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Text(
                            "No subjects yet",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_500,
                        ),
                        ft.Text(
                            "Click 'Add Subject' to get started!",
                            size=14,
                            color=ft.Colors.GREY_500,
                            italic=True,
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    alignment=ft.alignment.Alignment(0,0),
                    padding=40,
                )
            )
        else:
            for sub in subjects:
                name, code, room, schedule = sub
                self.subject_grid.controls.append(
                    self.create_subject_card(name, code, room, schedule)
                )
        
        # Update subject count in header
        if hasattr(self, 'page') and self.page and update_ui:
            show_success(self.page, f"Loaded {len(subjects)} subjects")
            
        if update_ui:
            self.update()

    def create_subject_card(self, name, code, room, schedule):
        """Create an enhanced card for displaying a subject"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Header with icon and code
                    ft.Row([
                        ft.Icon(
                            ft.Icons.SCHOOL,
                            color=ft.Colors.BLUE_400,
                            size=32,
                        ),
                        ft.Text(
                            code if code else "N/A",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.CYAN_400,
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    # Subject name
                    ft.Text(
                        name,
                        size=15,
                        weight=ft.FontWeight.W_500,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    
                    ft.Divider(height=8, thickness=1),
                    
                    # Room info
                    ft.Row([
                        ft.Icon(ft.Icons.ROOM, size=16, color=ft.Colors.GREY_400),
                        ft.Text(
                            room if room else "No room",
                            size=13,
                            color=ft.Colors.GREY_300,
                        ),
                    ], spacing=5),
                    
                    # Schedule info
                    ft.Row([
                        ft.Icon(ft.Icons.SCHEDULE, size=16, color=ft.Colors.GREY_400),
                        ft.Text(
                            schedule if schedule else "No schedule",
                            size=13,
                            color=ft.Colors.GREY_300,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ], spacing=5),
                ], spacing=8),
                padding=15,
                bgcolor=ft.Colors.GREY_900,
                border_radius=10,
            ),
            elevation=2,
        )

    def open_dialog(self, e):
        """Open the add subject dialog with proper form reset"""
        # Clear all fields and errors
        self.sub_name.value = ""
        self.sub_code.value = ""
        self.sub_room.value = ""
        self.sub_sched.value = ""
        self.sub_name.error_text = None
        self.sub_code.error_text = None
        self.sub_room.error_text = None
        self.sub_sched.error_text = None
        
        self.page.dialog = self.add_dialog
        self.add_dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        """Close the add subject dialog"""
        self.add_dialog.open = False
        self.page.update()

    @with_error_handling
    def save_subject(self, e):
        """Save a new subject to the database with enhanced validation"""
        # Clear previous errors
        self.sub_name.error_text = None
        self.sub_code.error_text = None
        self.sub_room.error_text = None
        self.sub_sched.error_text = None
        
        # Comprehensive validation
        is_valid = True
        
        # Required field validation
        if not ValidationHelpers.validate_required_field(self.sub_name, "Subject name"):
            is_valid = False
            
        # Subject code validation (optional but if provided, should be reasonable length)
        if self.sub_code.value and len(self.sub_code.value.strip()) > 20:
            self.sub_code.error_text = "Subject code too long (max 20 characters)"
            is_valid = False
            
        if not is_valid:
            self.page.update()
            show_error(self.page, "Please fix the validation errors")
            return
        
        name = self.sub_name.value.strip()
        code = self.sub_code.value.strip() if self.sub_code.value else ""
        room = self.sub_room.value.strip() if self.sub_room.value else ""
        schedule = self.sub_sched.value.strip() if self.sub_sched.value else ""
        
        # Check for duplicate subject name
        existing_subjects = self.db.get_subjects()
        if any(sub[0].lower() == name.lower() for sub in existing_subjects):
            self.sub_name.error_text = "Subject with this name already exists"
            self.page.update()
            show_error(self.page, "Subject with this name already exists")
            return
        
        # Add to database
        self.db.add_subject(name, code, room, schedule)
        
        # Refresh and close
        self.refresh_subjects()
        self.close_dialog(None)
        show_success(self.page, f"Subject '{name}' added successfully!")

    def show_snackbar(self, message, success=False, error=False):
        """Show a snackbar notification"""
        if self.page:
            bgcolor = ft.Colors.GREEN_700 if success else (ft.Colors.RED_700 if error else ft.Colors.BLUE_700)
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message, color="#FFFFFF"),
                bgcolor=bgcolor,
            )
            self.page.snack_bar.open = True
            self.page.update()

    # --- GWA Calculator Logic ---
    def add_grade_row(self, update=False):
        """Add a new grade input row"""
        row = ft.Row(
            controls=[
                ft.TextField(
                    label="Grade",
                    width=120,
                    hint_text="1.0-5.0",
                    border_color=ft.Colors.BLUE_400,
                    keyboard_type=ft.KeyboardType.NUMBER,
                ),
                ft.TextField(
                    label="Units",
                    width=120,
                    hint_text="e.g., 3",
                    border_color=ft.Colors.BLUE_400,
                    keyboard_type=ft.KeyboardType.NUMBER,
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED_400,
                    tooltip="Delete row",
                    on_click=lambda e: self.delete_row(e.control.parent),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )
        self.grade_rows.controls.append(row)
        if update:
            self.update()

    def delete_row(self, row_control):
        """Delete a grade input row"""
        if len(self.grade_rows.controls) > 1:  # Keep at least one row
            self.grade_rows.controls.remove(row_control)
            self.update()
        else:
            self.show_snackbar("At least one row is required", error=True)

    def calculate_gwa(self, e):
        """Calculate the GWA from entered grades and units"""
        total_points = 0.0
        total_units = 0.0
        valid_entries = 0
        
        for row in self.grade_rows.controls:
            try:
                grade_field = row.controls[0]
                units_field = row.controls[1]
                
                if grade_field.value and units_field.value:
                    grade = float(grade_field.value)
                    units = float(units_field.value)
                    
                    # Validate grade range (typical Philippine grading: 1.0-5.0)
                    if grade < 1.0 or grade > 5.0:
                        grade_field.error_text = "Grade must be 1.0-5.0"
                        self.update()
                        continue
                    
                    if units <= 0:
                        units_field.error_text = "Units must be positive"
                        self.update()
                        continue
                    
                    # Clear any previous errors
                    grade_field.error_text = None
                    units_field.error_text = None
                    
                    total_points += grade * units
                    total_units += units
                    valid_entries += 1
                    
            except ValueError:
                continue
        
        if total_units > 0 and valid_entries > 0:
            gwa = total_points / total_units
            self.gwa_result.value = f"GWA: {gwa:.2f}"
            self.gwa_result.color = ft.Colors.CYAN_400
            self.show_snackbar(f"GWA calculated: {gwa:.2f} from {valid_entries} subjects", success=True)
        else:
            self.gwa_result.value = "Enter valid grades and units"
            self.gwa_result.color = ft.Colors.RED_400
            self.show_snackbar("Please enter valid grades (1.0-5.0) and units", error=True)
        
        self.update()





