import flet as ft
import json
from datetime import datetime
from utils import UIHelpers, ValidationHelpers, ErrorHandler, show_success, show_error, with_error_handling

class SettingsView(ft.Container):
    def __init__(self, db, page):
        super().__init__()
        self.db = db
        self.app_page = page
        self.expand = True
        self.padding = 20
        
        # File picker for import
        self.file_picker = ft.FilePicker()
        
        # Settings fields
        self.daily_budget_field = ft.TextField(
            label="Daily Budget ($)",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
            value=self.db.get_setting("daily_budget") or "50.0"
        )
        
        self.focus_duration_field = ft.TextField(
            label="Focus Duration (minutes)",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
            value=self.db.get_setting("focus_duration") or "25"
        )
        
        self.break_duration_field = ft.TextField(
            label="Break Duration (minutes)",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
            value=self.db.get_setting("break_duration") or "5"
        )
        
        self.theme_toggle = ft.Switch(
            label="Dark Mode",
            value=(self.db.get_setting("theme") or "dark") == "dark",
            on_change=self.toggle_theme
        )
        
        self.content = ft.Column(
            [
                # Hidden file picker
                self.file_picker,
                
                ft.Text("Settings", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                ft.Row(
                    [
                        # Left panel - General Settings
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("General Settings", size=22, weight=ft.FontWeight.BOLD),
                                    ft.Divider(),
                                    
                                    ft.Text("Appearance", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300),
                                    self.theme_toggle,
                                    
                                    ft.Divider(),
                                    ft.Text("Finance", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_300),
                                    self.daily_budget_field,
                                    
                                    ft.Divider(),
                                    ft.Text("Focus Timer", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_300),
                                    self.focus_duration_field,
                                    self.break_duration_field,
                                    
                                    ft.Divider(),
                                    ft.ElevatedButton(
                                        "Save Settings",
                                        icon=ft.Icons.SAVE,
                                        on_click=self.save_settings,
                                        bgcolor=ft.Colors.GREEN_700,
                                        color="#FFFFFF"
                                    ),
                                ],
                                spacing=15,
                            ),
                            bgcolor=ft.Colors.BLUE_GREY_900,
                            padding=30,
                            border_radius=10,
                            width=400,
                        ),
                        
                        # Right panel - Data Management
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Data Management", size=22, weight=ft.FontWeight.BOLD),
                                    ft.Divider(),
                                    
                                    ft.Text("Backup & Restore", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_300),
                                    ft.Text("Export and import your data for backup", size=14, color=ft.Colors.GREY_400),
                                    ft.Row(
                                        [
                                            ft.ElevatedButton(
                                                "Export Data",
                                                icon=ft.Icons.DOWNLOAD,
                                                on_click=self.export_data,
                                                bgcolor=ft.Colors.PURPLE_700,
                                                color="#FFFFFF"
                                            ),
                                            ft.ElevatedButton(
                                                "Import Data",
                                                icon=ft.Icons.UPLOAD,
                                                on_click=self.pick_import_file,
                                                bgcolor=ft.Colors.ORANGE_700,
                                                color="#FFFFFF"
                                            ),
                                            ft.ElevatedButton(
                                                "Load Sample Semester",
                                                icon=ft.Icons.AUTO_AWESOME,
                                                on_click=self.load_sample_semester,
                                                bgcolor=ft.Colors.INDIGO_700,
                                                color="#FFFFFF"
                                            ),
                                        ],
                                        spacing=10,
                                        wrap=True,
                                    ),
                                    
                                    ft.Divider(),
                                    ft.Text("Statistics", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
                                    self.get_statistics_widget(),
                                ],
                                spacing=15,
                            ),
                            bgcolor=ft.Colors.BLUE_GREY_900,
                            padding=30,
                            border_radius=10,
                            expand=True,
                        ),
                    ],
                    spacing=20,
                    expand=True,
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                )
            ],
            spacing=20,
            expand=True,
        )
    
    def save_settings(self, e):
        """Save settings to database"""
        try:
            # Validate and save budget
            budget = float(self.daily_budget_field.value)
            self.db.update_setting("daily_budget", str(budget))
            
            # Validate and save focus duration
            focus = int(self.focus_duration_field.value)
            self.db.update_setting("focus_duration", str(focus))
            
            # Validate and save break duration
            break_time = int(self.break_duration_field.value)
            self.db.update_setting("break_duration", str(break_time))
            
            # Theme is handled by toggle
            
            if hasattr(self.page, 'snack_bar'):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Settings saved successfully!", color="#FFFFFF"),
                    bgcolor=ft.Colors.GREEN_700,
                )
                self.page.snack_bar.open = True
                self.page.update()
        except:
            if hasattr(self.page, 'snack_bar'):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Invalid input values", color="#FFFFFF"),
                    bgcolor=ft.Colors.RED_700,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def load_sample_semester(self, e):
        """Populate starter sample academic data when tables are empty."""
        count = self.db.seed_demo_semester()
        if hasattr(self.page, 'snack_bar'):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Loaded {count} sample semester records!", color="#FFFFFF"),
                bgcolor=ft.Colors.INDIGO_700,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def toggle_theme(self, e):
        """Toggle between dark and light theme"""
        new_theme = "dark" if e.control.value else "light"
        self.db.update_setting("theme", new_theme)
        
        # Apply theme to page
        if self.app_page:
            self.app_page.theme_mode = new_theme
            self.app_page.update()
        
        if hasattr(self.page, 'snack_bar'):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✅ Theme changed to {new_theme} mode", color="#FFFFFF"),
                bgcolor=ft.Colors.BLUE_700,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def get_statistics_widget(self):
        """Get statistics widget"""
        try:
            # Count items in database
            tasks = len(self.db.get_tasks_for_today())
            projects = len(self.db.get_projects())
            expenses = len(self.db.get_expenses())
            subjects = len(self.db.get_subjects())
            assignments = len(self.db.get_assignments())
            events = len(self.db.get_events())
            notes = len(self.db.get_notes())
            
            return ft.Column(
                [
                    self.stat_row("📝 Tasks Today", tasks),
                    self.stat_row("💼 Projects", projects),
                    self.stat_row("💰 Expenses", expenses),
                    self.stat_row("📚 Subjects", subjects),
                    self.stat_row("📋 Assignments", assignments),
                    self.stat_row("📅 Events", events),
                    self.stat_row("📓 Notes & Flashcards", notes),
                ],
                spacing=10,
            )
        except:
            return ft.Text("Unable to load statistics", color=ft.Colors.RED_400)
    
    def stat_row(self, label, value):
        """Create a stat row"""
        return ft.Row(
            [
                ft.Text(label, size=14),
                ft.Text(str(value), size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
    
    def export_data(self, e):
        """Export all data to JSON"""
        try:
            export_data = {
                "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tasks": self.db.get_tasks_for_today(),
                "projects": self.db.get_projects(),
                "expenses": self.db.get_expenses(),
                "subjects": self.db.get_subjects(),
                "assignments": self.db.get_assignments(),
                "events": self.db.get_events(),
                "notes": self.db.get_notes(),
                "focus_logs": self.db.get_focus_logs(),
            }
            
            # Save to file
            filename = f"student_os_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            if hasattr(self.page, 'snack_bar'):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ Data exported to {filename}", color="#FFFFFF"),
                    bgcolor=ft.Colors.GREEN_700,
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as ex:
            if hasattr(self.page, 'snack_bar'):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Export failed: {str(ex)}", color="#FFFFFF"),
                    bgcolor=ft.Colors.RED_700,
                )
                self.page.snack_bar.open = True
                self.page.update()    
    def pick_import_file(self, e):
        """Open file picker to select import JSON"""
        def on_result(result: ft.FilePickerResultEvent):
            if result.files:
                file_path = result.files[0].path
                self.import_data(file_path)
        
        self.file_picker.on_result = on_result
        self.file_picker.pick_files(
            allowed_extensions=["json"],
            dialog_title="Select StudentOS export file",
        )
    
    def import_data(self, file_path):
        """Import data from JSON file"""
        try:
            # Read JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            imported_count = 0
            
            # Import subjects
            if "subjects" in data:
                for subject in data["subjects"]:
                    try:
                        self.db.add_subject(subject[0], subject[1], subject[2], subject[3])
                        imported_count += 1
                    except:
                        pass
            
            # Import projects
            if "projects" in data:
                for project in data["projects"]:
                    try:
                        self.db.add_project(project[1], project[2], project[3])
                        imported_count += 1
                    except:
                        pass
            
            # Import expenses
            if "expenses" in data:
                for expense in data["expenses"]:
                    try:
                        conn = self.db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO finance (item, amount, category, date) VALUES (?, ?, ?, ?)",
                            (expense[0], expense[1], expense[2], expense[3])
                        )
                        conn.commit()
                        conn.close()
                        imported_count += 1
                    except:
                        pass
            
            # Import assignments
            if "assignments" in data:
                for assignment in data["assignments"]:
                    try:
                        conn = self.db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO assignments (subject, title, description, due_date, grade, max_grade, status, submission_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (assignment[1], assignment[2], assignment[3], assignment[4], assignment[5], assignment[6], assignment[7], assignment[8], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        )
                        conn.commit()
                        conn.close()
                        imported_count += 1
                    except:
                        pass
            
            # Import events
            if "events" in data:
                for event in data["events"]:
                    try:
                        self.db.add_event(event[1], event[2], event[3], event[4], event[5], event[6])
                        imported_count += 1
                    except:
                        pass
            
            # Import notes
            if "notes" in data:
                for note in data["notes"]:
                    try:
                        if note[4] == "flashcard" and note[5] and note[6]:
                            self.db.add_flashcard(note[2], note[5], note[6], note[1], note[7])
                        else:
                            self.db.add_note(note[2], note[3], note[1], note[7])
                        imported_count += 1
                    except:
                        pass
            
            if hasattr(self.page, 'snack_bar'):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ Successfully imported {imported_count} items!", color="#FFFFFF"),
                    bgcolor=ft.Colors.GREEN_700,
                )
                self.page.snack_bar.open = True
                self.page.update()
                
        except Exception as ex:
            if hasattr(self.page, 'snack_bar'):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Import failed: {str(ex)}", color="#FFFFFF"),
                    bgcolor=ft.Colors.RED_700,
                )
                self.page.snack_bar.open = True
                self.page.update()