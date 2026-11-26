import flet as ft
from utils import UIHelpers, ValidationHelpers, ErrorHandler, show_success, show_error, with_error_handling

class ProjectTask(ft.Container):
    """A draggable project task card"""
    def __init__(self, project_id, name, stack, status, on_drop_callback):
        super().__init__()
        self.project_id = project_id
        self.name = name
        self.stack = stack
        self.status = status
        self.on_drop_callback = on_drop_callback
        
        # Status colors
        status_colors = {
            "To Do": ft.Colors.BLUE_700,
            "In Progress": ft.Colors.ORANGE_700,
            "Done": ft.Colors.GREEN_700,
        }
        
        self.content = ft.Draggable(
            group="projects",
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Colors.CODE, color=ft.Colors.BLUE_400, size=24),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text(
                                    status,
                                    size=10,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF",
                                ),
                                bgcolor=status_colors.get(status, ft.Colors.GREY_700),
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                border_radius=10,
                            ),
                        ]),
                        ft.Text(
                            name,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Row([
                            ft.Icon(ft.Icons.BUILD, size=12, color=ft.Colors.GREY_400),
                            ft.Text(
                                stack if stack else "No stack",
                                size=11,
                                color=ft.Colors.GREY_300,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                expand=True,
                            ),
                        ], spacing=5),
                    ], spacing=8),
                    padding=12,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=8,
                ),
                elevation=2,
            ),
            content_feedback=ft.Container(
                content=ft.Text(name, color=ft.Colors.CYAN_400),
                bgcolor=ft.Colors.GREY_800,
                padding=10,
                border_radius=8,
                opacity=0.7,
            ),
            data={"id": project_id, "name": name, "stack": stack, "old_status": status},
        )


class KanbanColumn(ft.Container):
    """A Kanban column with drag target"""
    def __init__(self, title, status, on_drop, color):
        super().__init__()
        self.title = title
        self.status = status
        self.on_drop = on_drop
        self.color = color
        
        self.tasks_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        
        self.content = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DRAG_INDICATOR, size=18, color=color),
                        ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=color),
                    ], spacing=5),
                    padding=10,
                ),
                ft.Divider(height=1, color=color),
                ft.Container(
                    content=ft.DragTarget(
                        group="projects",
                        content=self.tasks_column,
                        on_accept=self.handle_drop,
                    ),
                    expand=True,
                    padding=10,
                ),
            ], spacing=0),
            bgcolor=ft.Colors.GREY_900,
            border_radius=10,
            border=ft.border.all(2, color),
            expand=True,
        )
    
    def handle_drop(self, e):
        """Handle task drop in this column"""
        if e.data:
            self.on_drop(e.data, self.status)


class ProjectsView(ft.Container):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20
        
        # Form fields for dialog
        self.project_name = ft.TextField(
            label="Project Name",
            hint_text="e.g., E-Commerce Website",
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
        )
        self.project_stack = ft.TextField(
            label="Tech Stack",
            hint_text="e.g., React, Node.js, MongoDB",
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
        )
        
        # Kanban columns
        self.todo_column = KanbanColumn(
            "To Do", 
            "To Do", 
            self.on_task_drop, 
            ft.Colors.BLUE_400
        )
        self.inprogress_column = KanbanColumn(
            "In Progress", 
            "In Progress", 
            self.on_task_drop, 
            ft.Colors.ORANGE_400
        )
        self.done_column = KanbanColumn(
            "Done", 
            "Done", 
            self.on_task_drop, 
            ft.Colors.GREEN_400
        )
        
        # Add project dialog
        self.add_dialog = ft.AlertDialog(
            title=ft.Text("Add New Project", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                self.project_name,
                self.project_stack,
            ], tight=True, width=400, spacing=15),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.ElevatedButton(
                    "Add Project",
                    icon=ft.Icons.ADD,
                    on_click=self.save_project,
                    bgcolor=ft.Colors.BLUE_700,
                    color="#FFFFFF",
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.build_ui()
    
    def build_ui(self):
        """Build the main UI"""
        self.refresh_projects(update_ui=False)
        
        self.content = ft.Column([
            # Header
            ft.Row([
                ft.Text("Projects - Kanban Board", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Add Project",
                    icon=ft.Icons.ADD,
                    on_click=self.open_dialog,
                    bgcolor=ft.Colors.BLUE_700,
                    color="#FFFFFF",
                ),
            ]),
            ft.Divider(),
            
            # Kanban board
            ft.Container(
                content=ft.Row([
                    self.todo_column,
                    self.inprogress_column,
                    self.done_column,
                ], spacing=15, expand=True),
                expand=True,
            ),
        ], spacing=15, expand=True)
    
    def on_task_drop(self, data_str, new_status):
        """Handle task drop - update database and UI"""
        import json
        try:
            data = json.loads(data_str)
            project_id = data.get("id")
            old_status = data.get("old_status")
            
            if old_status != new_status:
                # Update in database
                self.db.update_project_status(project_id, new_status)
                # Refresh UI
                self.refresh_projects()
                self.show_snackbar(f"Moved to {new_status}", success=True)
        except Exception as e:
            print(f"Drop error: {e}")
    
    def refresh_projects(self, update_ui=True):
        """Load and display all projects in Kanban columns"""
        # Clear all columns
        self.todo_column.tasks_column.controls.clear()
        self.inprogress_column.tasks_column.controls.clear()
        self.done_column.tasks_column.controls.clear()
        
        projects = self.db.get_projects()
        
        if not projects:
            # Show empty state in To Do column
            self.todo_column.tasks_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            ft.Icons.CODE_OFF,
                            size=60,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Text(
                            "No projects yet",
                            size=14,
                            color=ft.Colors.GREY_500,
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    alignment=ft.alignment.Alignment(0, 0),
                    padding=20,
                )
            )
        else:
            for proj in projects:
                project_id, name, stack, status = proj
                
                task_card = ProjectTask(
                    project_id=project_id,
                    name=name,
                    stack=stack,
                    status=status,
                    on_drop_callback=self.on_task_drop
                )
                
                # Add to appropriate column
                if status == "To Do":
                    self.todo_column.tasks_column.controls.append(task_card)
                elif status == "In Progress":
                    self.inprogress_column.tasks_column.controls.append(task_card)
                elif status == "Done":
                    self.done_column.tasks_column.controls.append(task_card)
        
        if update_ui:
            self.update()
    
    def open_dialog(self, e):
        """Open the add project dialog"""
        self.project_name.value = ""
        self.project_stack.value = ""
        self.project_name.error_text = None
        self.page.dialog = self.add_dialog
        self.add_dialog.open = True
        self.page.update()
    
    def close_dialog(self, e):
        """Close the add project dialog"""
        self.add_dialog.open = False
        self.page.update()
    
    def save_project(self, e):
        """Save a new project to the database"""
        # Validation
        if not self.project_name.value or not self.project_name.value.strip():
            self.project_name.error_text = "Project name is required"
            self.page.update()
            self.show_snackbar("Please enter a project name", error=True)
            return
        
        name = self.project_name.value.strip()
        stack = self.project_stack.value.strip() if self.project_stack.value else ""
        status = "To Do"  # New projects start in To Do
        
        # Add to database
        self.db.add_project(name, stack, status)
        
        # Refresh and close
        self.refresh_projects()
        self.close_dialog(None)
        self.show_snackbar(f"Project '{name}' added to To Do!", success=True)
    
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

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20
        
        # Form fields for dialog
        self.project_name = ft.TextField(
            label="Project Name",
            hint_text="e.g., E-Commerce Website",
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
        )
        self.project_stack = ft.TextField(
            label="Tech Stack",
            hint_text="e.g., React, Node.js, MongoDB",
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
        )
        self.project_status = ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option("Planning"),
                ft.dropdown.Option("In Progress"),
                ft.dropdown.Option("Completed"),
                ft.dropdown.Option("On Hold"),
            ],
            value="In Progress",
            border_color=ft.Colors.BLUE_400,
        )
        
        # Projects grid
        self.projects_grid = ft.GridView(
            runs_count=4,
            max_extent=280,
            child_aspect_ratio=1.2,
            spacing=15,
            run_spacing=15,
            expand=True,
        )
        
        # Add project dialog
        self.add_dialog = ft.AlertDialog(
            title=ft.Text("Add New Project", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                self.project_name,
                self.project_stack,
                self.project_status,
            ], tight=True, width=400, spacing=15),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.ElevatedButton(
                    "Add Project",
                    icon=ft.Icons.ADD,
                    on_click=self.save_project,
                    bgcolor=ft.Colors.BLUE_700,
                    color="#FFFFFF",
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.build_ui()
    
    def build_ui(self):
        """Build the main UI"""
        self.refresh_projects(update_ui=False)
        
        self.content = ft.Column([
                # Header
                ft.Row([
                    ft.Text("Projects", size=28, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Add Project",
                        icon=ft.Icons.ADD,
                        on_click=self.open_dialog,
                        bgcolor=ft.Colors.BLUE_700,
                        color="#FFFFFF",
                    ),
                ]),
                ft.Divider(),
                
                # Projects grid
                ft.Text("My Portfolio", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.projects_grid,
                    expand=True,
                ),
            ], spacing=15, expand=True)

    def refresh_projects(self, update_ui=True):
        """Load and display all projects from the database"""
        self.projects_grid.controls.clear()
        projects = self.db.get_projects()
        
        if not projects:
            # Show empty state
            self.projects_grid.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            ft.Icons.CODE_OFF,
                            size=80,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Text(
                            "No projects yet",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_500,
                        ),
                        ft.Text(
                            "Click 'Add Project' to start building!",
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
            for proj in projects:
                name, stack, status = proj
                self.projects_grid.controls.append(
                    self.create_project_card(name, stack, status)
                )
        
        if update_ui:
            self.update()

    def create_project_card(self, name, stack, status):
        """Create an enhanced project card"""
        # Determine status color
        status_colors = {
            "Completed": ft.Colors.GREEN_700,
            "In Progress": ft.Colors.BLUE_700,
            "Planning": ft.Colors.PURPLE_700,
            "On Hold": ft.Colors.ORANGE_700,
        }
        status_color = status_colors.get(status, ft.Colors.GREY_700)
        
        # Determine icon based on status
        status_icons = {
            "Completed": ft.Icons.CHECK_CIRCLE,
            "In Progress": ft.Icons.TRENDING_UP,
            "Planning": ft.Icons.LIGHTBULB,
            "On Hold": ft.Icons.PAUSE_CIRCLE,
        }
        status_icon = status_icons.get(status, ft.Icons.CODE)
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Header with icon
                    ft.Row([
                        ft.Icon(
                            ft.Icons.CODE,
                            color=ft.Colors.BLUE_400,
                            size=32,
                        ),
                        ft.Container(expand=True),
                        ft.Icon(
                            status_icon,
                            color=status_color,
                            size=24,
                        ),
                    ]),
                    
                    # Project name
                    ft.Text(
                        name,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    
                    # Tech stack
                    ft.Row([
                        ft.Icon(ft.Icons.BUILD, size=14, color=ft.Colors.GREY_400),
                        ft.Text(
                            stack if stack else "No stack specified",
                            size=12,
                            color=ft.Colors.GREY_300,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            expand=True,
                        ),
                    ], spacing=5),
                    
                    ft.Divider(height=8, thickness=1),
                    
                    # Status badge
                    ft.Container(
                        content=ft.Text(
                            status,
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF",
                        ),
                        bgcolor=status_color,
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        border_radius=15,
                        alignment=ft.alignment.Alignment(0,0),
                    ),
                ], spacing=8),
                padding=15,
                bgcolor=ft.Colors.GREY_900,
                border_radius=10,
            ),
            elevation=2,
        )

    def open_dialog(self, e):
        """Open the add project dialog"""
        self.project_name.value = ""
        self.project_stack.value = ""
        self.project_status.value = "In Progress"
        self.project_name.error_text = None
        self.page.dialog = self.add_dialog
        self.add_dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        """Close the add project dialog"""
        self.add_dialog.open = False
        self.page.update()

    def save_project(self, e):
        """Save a new project to the database"""
        # Validation
        if not self.project_name.value or not self.project_name.value.strip():
            self.project_name.error_text = "Project name is required"
            self.page.update()
            self.show_snackbar("Please enter a project name", error=True)
            return
        
        name = self.project_name.value.strip()
        stack = self.project_stack.value.strip() if self.project_stack.value else ""
        status = self.project_status.value
        
        # Add to database
        self.db.add_project(name, stack, status)
        
        # Refresh and close
        self.refresh_projects()
        self.close_dialog(None)
        self.show_snackbar(f"Project '{name}' added successfully!", success=True)

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






