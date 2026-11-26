"""
Quick Tasks View - Simple task management separate from time blocking
"""
import flet as ft
from datetime import datetime
from utils import UIHelpers, ValidationHelpers, ErrorHandler, show_success, show_error, with_error_handling


class QuickTasksView(ft.Container):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20
        
        # UI Elements
        self.task_input = ft.TextField(
            label="New Task",
            hint_text="Enter a quick task and press Enter...",
            expand=True,
            autofocus=True,
            on_submit=self.add_task,
            prefix_icon=ft.Icons.ADD_TASK,
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
        )
        
        self.priority_dropdown = ft.Dropdown(
            label="Priority",
            value="Medium",
            width=120,
            options=[
                ft.dropdown.Option("High", "🔴 High"),
                ft.dropdown.Option("Medium", "🟡 Medium"),
                ft.dropdown.Option("Low", "🟢 Low"),
            ],
        )
        
        self.category_dropdown = ft.Dropdown(
            label="Category",
            value="General",
            width=150,
            options=[
                ft.dropdown.Option("General", "📋 General"),
                ft.dropdown.Option("Study", "📚 Study"),
                ft.dropdown.Option("Personal", "👤 Personal"),
                ft.dropdown.Option("Work", "💼 Work"),
                ft.dropdown.Option("Health", "💪 Health"),
                ft.dropdown.Option("Finance", "💰 Finance"),
            ],
        )
        
        # Task lists
        self.pending_tasks = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        self.completed_tasks = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        
        # Stats
        self.stats_pending = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400)
        self.stats_completed = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
        self.stats_total = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
        
        self.build_ui()
        
    def build_ui(self):
        """Build the main UI"""
        # Add task section
        add_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("➕ Add Quick Task", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        self.task_input,
                        self.priority_dropdown,
                        self.category_dropdown,
                        ft.ElevatedButton(
                            "Add",
                            icon=ft.Icons.ADD,
                            on_click=self.add_task,
                            bgcolor=ft.Colors.BLUE_700,
                            color="#FFFFFF",
                        ),
                    ], spacing=10),
                    ft.Row([
                        ft.TextButton(
                            "Add from template",
                            icon=ft.Icons.CONTENT_COPY,
                            on_click=self.show_templates,
                        ),
                        ft.TextButton(
                            "Bulk add",
                            icon=ft.Icons.LIST_ALT,
                            on_click=self.show_bulk_add,
                        ),
                        ft.TextButton(
                            "Clear all completed",
                            icon=ft.Icons.CLEAR_ALL,
                            on_click=self.clear_completed_tasks,
                        ),
                    ], spacing=10),
                ], spacing=15),
                padding=20,
                bgcolor=ft.Colors.BLUE_GREY_900,
                border_radius=10,
            ),
        )
        
        # Stats section
        stats_section = ft.Card(
            content=ft.Container(
                content=ft.Row([
                    self.create_stat_card("Pending", self.stats_pending, ft.Icons.PENDING, ft.Colors.ORANGE_700),
                    self.create_stat_card("Completed", self.stats_completed, ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN_700),
                    self.create_stat_card("Total", self.stats_total, ft.Icons.ASSIGNMENT, ft.Colors.BLUE_700),
                ], spacing=20, alignment=ft.MainAxisAlignment.SPACE_AROUND),
                padding=20,
            ),
            elevation=2,
        )
        
        # Tasks section
        tasks_section = ft.Row([
            # Pending tasks
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("⏳ Pending Tasks", size=20, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip="Refresh tasks",
                            on_click=lambda _: self.load_tasks(),
                        ),
                    ]),
                    ft.Container(
                        content=self.pending_tasks,
                        expand=True,
                        height=400,
                    ),
                ], spacing=10),
                bgcolor=ft.Colors.BLUE_GREY_900,
                padding=20,
                border_radius=10,
                expand=True,
            ),
            
            # Completed tasks  
            ft.Container(
                content=ft.Column([
                    ft.Text("✅ Completed Tasks", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=self.completed_tasks,
                        expand=True,
                        height=400,
                    ),
                ], spacing=10),
                bgcolor=ft.Colors.BLUE_GREY_900,
                padding=20,
                border_radius=10,
                expand=True,
            ),
        ], spacing=20, expand=True)
        
        # Main content
        main_content = ft.Column([
            ft.Text("⚡ Quick Tasks", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Simple task management for quick capture and tracking", size=14, color=ft.Colors.GREY_400),
            ft.Divider(),
            add_section,
            stats_section,
            tasks_section,
        ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)
        
        self.content = main_content
        
        # Load initial data
        self.load_tasks()
    
    def create_stat_card(self, title, value_text, icon, color):
        """Create a statistics card"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=30, color=color),
                    ft.Container(expand=True),
                ]),
                value_text,
                ft.Text(title, size=12, color=ft.Colors.GREY_400),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            bgcolor=color.value + "20",  # Add transparency
            border=ft.border.all(2, color),
            border_radius=10,
            padding=15,
            width=120,
            height=90,
        )
    
    @with_error_handling
    def add_task(self, e=None):
        """Add a new quick task"""
        # Validate input
        if not ValidationHelpers.validate_required_field(self.task_input, "Task"):
            self.task_input.focus()
            self.update()
            return
        
        task_text = self.task_input.value.strip()
        priority = self.priority_dropdown.value
        category = self.category_dropdown.value
        
        # Add to database
        task_id = self.db.add_quick_task(task_text, priority, category)
        
        # Clear input
        self.task_input.value = ""
        self.task_input.error_text = None
        
        # Reload and show success
        self.load_tasks()
        show_success(self.page, f"Task '{task_text}' added successfully!")
        
        # Focus back to input for quick entry
        self.task_input.focus()
        self.update()
    
    @with_error_handling
    def load_tasks(self):
        """Load all quick tasks from database"""
        # Show loading states
        self.pending_tasks.controls.clear()
        self.completed_tasks.controls.clear()
        
        self.pending_tasks.controls.append(UIHelpers.create_loading_indicator("Loading pending tasks..."))
        self.completed_tasks.controls.append(UIHelpers.create_loading_indicator("Loading completed tasks..."))
        self.update()
        
        # Get tasks from database
        all_tasks = self.db.get_quick_tasks()
        
        # Clear loading states
        self.pending_tasks.controls.clear()
        self.completed_tasks.controls.clear()
        
        pending_count = 0
        completed_count = 0
        
        if not all_tasks:
            self.pending_tasks.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.TASK_ALT, size=60, color=ft.Colors.GREY_400),
                        ft.Text("No tasks yet", size=16, color=ft.Colors.GREY_400),
                        ft.Text("Add your first quick task above!", size=12, color=ft.Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    height=200,
                )
            )
        else:
            for task in all_tasks:
                task_id, task_text, priority, category, status, created_at, completed_at = task
                
                task_card = self.create_task_card(task_id, task_text, priority, category, status, created_at)
                
                if status == "completed":
                    self.completed_tasks.controls.append(task_card)
                    completed_count += 1
                else:
                    self.pending_tasks.controls.append(task_card)
                    pending_count += 1
        
        # Update stats
        self.stats_pending.value = str(pending_count)
        self.stats_completed.value = str(completed_count)
        self.stats_total.value = str(pending_count + completed_count)
        
        self.update()
    
    @with_error_handling
    def create_task_card(self, task_id, task_text, priority, category, status, created_at):
        """Create a task card"""
        priority_colors = {
            "High": ft.Colors.RED_400,
            "Medium": ft.Colors.YELLOW_400,
            "Low": ft.Colors.GREEN_400,
        }
        
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Checkbox(
                        value=status == "completed",
                        on_change=lambda e: self.toggle_task_status(task_id, e.control.value),
                        fill_color=ft.Colors.GREEN_700,
                    ),
                    ft.Expanded(
                        child=ft.Column([
                            ft.Text(
                                task_text,
                                size=14,
                                weight=ft.FontWeight.W500,
                                color=ft.Colors.GREY_400 if status == "completed" else None,
                            ),
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(priority, size=10, color="#FFFFFF"),
                                    bgcolor=priority_colors.get(priority, ft.Colors.GREY),
                                    padding=ft.Padding(4, 2, 4, 2),
                                    border_radius=4,
                                ),
                                ft.Text(f"• {category}", size=10, color=ft.Colors.GREY_500),
                                ft.Container(expand=True),
                                ft.Text(created_at.split()[0], size=10, color=ft.Colors.GREY_500),
                            ], spacing=8),
                        ], spacing=4)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_400,
                        tooltip="Delete task",
                        on_click=lambda e: self.delete_task(task_id),
                        icon_size=16,
                    ),
                ], alignment=ft.MainAxisAlignment.START),
                padding=12,
                bgcolor=ft.Colors.GREEN_900 if status == "completed" else ft.Colors.GREY_900,
            ),
            elevation=1,
        )
    
    @with_error_handling
    def toggle_task_status(self, task_id, is_completed):
        """Toggle task completion status"""
        status = "completed" if is_completed else "pending"
        self.db.update_quick_task_status(task_id, status)
        
        self.load_tasks()
        
        action = "completed" if is_completed else "reopened"
        show_success(self.page, f"Task {action} successfully!")
    
    @with_error_handling
    def delete_task(self, task_id):
        """Delete a task"""
        def confirm_delete(e):
            self.db.delete_quick_task(task_id)
            self.load_tasks()
            show_success(self.page, "Task deleted successfully!")
            dialog.open = False
            self.page.update()
        
        def cancel_delete(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Delete Task"),
            content=ft.Text("Are you sure you want to delete this task? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.ElevatedButton(
                    "Delete",
                    on_click=confirm_delete,
                    bgcolor=ft.Colors.RED_700,
                    color="#FFFFFF",
                ),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def show_templates(self, e):
        """Show task templates"""
        templates = [
            "Review lecture notes",
            "Complete assignment", 
            "Study for exam",
            "Read chapter",
            "Practice problems",
            "Group study session",
            "Research project topic",
            "Prepare presentation", 
            "Submit application",
            "Exercise/workout",
        ]
        
        template_buttons = []
        for template in templates:
            btn = ft.ElevatedButton(
                template,
                on_click=lambda e, text=template: self.add_template_task(text, e),
                width=200,
            )
            template_buttons.append(btn)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Task Templates"),
            content=ft.Container(
                content=ft.Column(template_buttons, scroll=ft.ScrollMode.AUTO),
                width=400,
                height=300,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog()),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def add_template_task(self, template_text, e):
        """Add a task from template"""
        self.task_input.value = template_text
        self.close_dialog()
        self.add_task()
    
    def show_bulk_add(self, e):
        """Show bulk add dialog"""
        bulk_input = ft.TextField(
            label="Bulk Tasks",
            hint_text="Enter tasks, one per line...",
            multiline=True,
            min_lines=10,
            expand=True,
        )
        
        def add_bulk_tasks(e):
            if bulk_input.value:
                lines = bulk_input.value.strip().split('\n')
                added_count = 0
                for line in lines:
                    task = line.strip()
                    if task:
                        self.db.add_quick_task(task, self.priority_dropdown.value, self.category_dropdown.value)
                        added_count += 1
                
                self.load_tasks()
                show_success(self.page, f"Added {added_count} tasks successfully!")
                self.close_dialog()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Bulk Add Tasks"),
            content=ft.Container(
                content=bulk_input,
                width=500,
                height=300,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog()),
                ft.ElevatedButton(
                    "Add All",
                    on_click=add_bulk_tasks,
                    bgcolor=ft.Colors.BLUE_700,
                    color="#FFFFFF",
                ),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    @with_error_handling
    def clear_completed_tasks(self, e):
        """Clear all completed tasks"""
        def confirm_clear(e):
            cleared_count = self.db.clear_completed_quick_tasks()
            self.load_tasks()
            show_success(self.page, f"Cleared {cleared_count} completed tasks!")
            dialog.open = False
            self.page.update()
        
        def cancel_clear(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Clear Completed Tasks"),
            content=ft.Text("Are you sure you want to clear all completed tasks? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_clear),
                ft.ElevatedButton(
                    "Clear All",
                    on_click=confirm_clear,
                    bgcolor=ft.Colors.ORANGE_700,
                    color="#FFFFFF",
                ),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def close_dialog(self):
        """Close any open dialog"""
        if hasattr(self.page, 'dialog') and self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def did_mount(self):
        """Called when view is mounted"""
        self.load_tasks()