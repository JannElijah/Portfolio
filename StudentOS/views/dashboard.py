import base64
import flet as ft
from datetime import datetime
import sys
import os

_EMPTY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from charts import create_spending_chart, create_grades_chart, create_focus_chart
from utils import UIHelpers, ErrorHandler, show_success, show_error, with_error_handling


class TimeBlockRow(ft.Container):
    def __init__(self, time_slot: str, task_name: str = "", status: str = "pending", priority: str = "Medium", on_change=None):
        super().__init__()
        self.time_slot = time_slot
        self.task_name = task_name
        self.status = status
        self.priority = priority
        self.on_change = on_change
        
        # Priority colors
        self.priority_colors = {
            "High": ft.Colors.RED_400,
            "Medium": ft.Colors.YELLOW_400,
            "Low": ft.Colors.GREEN_400,
        }
        
        # Style props
        self.padding = 12
        self.border_radius = 8
        self.border = ft.border.all(1, ft.Colors.GREY_700)
        self.bgcolor = ft.Colors.GREEN_900 if self.status == "completed" else ft.Colors.GREY_900
        self.animate = 300
        
        self.checkbox = ft.Checkbox(
            value=self.status == "completed",
            on_change=self.handle_change,
            fill_color=ft.Colors.GREEN_700,
        )
        self.task_field = ft.TextField(
            value=self.task_name,
            expand=True,
            border="none",
            hint_text="What needs to be done?",
            text_style=ft.TextStyle(
                decoration=ft.TextDecoration.LINE_THROUGH if self.status == "completed" else ft.TextDecoration.NONE,
                color=ft.Colors.GREY_500 if self.status == "completed" else None,
            ),
            on_submit=self.handle_change,
            on_blur=self.handle_change,
        )
        
        self.priority_button = ft.IconButton(
            icon=ft.Icons.FLAG,
            icon_color=self.priority_colors.get(self.priority, ft.Colors.GREY_400),
            tooltip=f"Priority: {self.priority}",
            on_click=self.cycle_priority,
        )
        
        time_icon = ft.Icon(
            ft.Icons.ACCESS_TIME,
            size=18,
            color=ft.Colors.BLUE_400,
        )
        
        self.content = ft.Row(
            controls=[
                time_icon,
                ft.Text(
                    self.time_slot,
                    width=90,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_300,
                ),
                self.task_field,
                self.priority_button,
                self.checkbox,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )
    
    def cycle_priority(self, e):
        """Cycle through priority levels"""
        priorities = ["Low", "Medium", "High"]
        current_index = priorities.index(self.priority)
        self.priority = priorities[(current_index + 1) % 3]
        
        # Update button color and tooltip
        self.priority_button.icon_color = self.priority_colors.get(self.priority, ft.Colors.GREY_400)
        self.priority_button.tooltip = f"Priority: {self.priority}"
        self.update()
        
        # Save changes
        if self.on_change:
            self.on_change(self.time_slot, self.task_field.value, self.status, self.priority)

    def handle_change(self, e):
        # Update state
        is_complete = self.checkbox.value
        self.status = "completed" if is_complete else "pending"
        
        # Visual updates
        self.bgcolor = ft.Colors.GREEN_900 if is_complete else ft.Colors.GREY_900
        self.task_field.text_style = ft.TextStyle(
            decoration=ft.TextDecoration.LINE_THROUGH if is_complete else ft.TextDecoration.NONE,
            color=ft.Colors.GREY_500 if is_complete else None,
        )
        self.update()
        
        if self.on_change:
            self.on_change(self.time_slot, self.task_field.value, self.status, self.priority)


class DashboardView(ft.Container):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20
        self.rows_col = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)
        self.completed_count = ft.Text("0", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
        self.pending_count = ft.Text("0", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400)
        self.productivity_text = ft.Text("0%", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
        self.streak_count = ft.Text("0", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_400)
        
        # Chart containers (hidden cleanly until populated with valid PNG bytes)
        self.spending_chart = ft.Image(src=_EMPTY_PNG, width=800, height=400, visible=False)
        self.grades_chart = ft.Image(src=_EMPTY_PNG, width=800, height=400, visible=False)
        self.focus_chart = ft.Image(src=_EMPTY_PNG, width=800, height=400, visible=False)
        self.spending_row = ft.Row(
            [
                ft.Container(
                    content=self.spending_chart,
                    padding=10,
                    bgcolor=ft.Colors.BLUE_GREY_900,
                    border_radius=10,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            visible=False,
        )
        self.grades_row = ft.Row(
            [
                ft.Container(
                    content=self.grades_chart,
                    padding=10,
                    bgcolor=ft.Colors.BLUE_GREY_900,
                    border_radius=10,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            visible=False,
        )
        self.focus_row = ft.Row(
            [
                ft.Container(
                    content=self.focus_chart,
                    padding=10,
                    bgcolor=ft.Colors.BLUE_GREY_900,
                    border_radius=10,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            visible=False,
        )
        self.no_charts_notice = ft.Text(
            "Add graded assignments, expenses, or focus logs to view analytics charts.",
            size=13,
            color=ft.Colors.GREY_400,
            visible=False,
        )
        
        self.build_ui()
    
    def build_ui(self):
        """Build the main UI"""
        # Stats cards
        stats_row = ft.Row([
            self.create_stat_card("Completed", self.completed_count, ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN_700),
            self.create_stat_card("Pending", self.pending_count, ft.Icons.PENDING, ft.Colors.ORANGE_700),
            self.create_stat_card("Productivity", self.productivity_text, ft.Icons.TRENDING_UP, ft.Colors.BLUE_700),
            self.create_stat_card("Streak", self.streak_count, ft.Icons.LOCAL_FIRE_DEPARTMENT, ft.Colors.PURPLE_700),
        ], spacing=15, alignment=ft.MainAxisAlignment.CENTER, wrap=True)
        
        # Analytics row
        analytics_row = ft.Row([
            self.create_analytics_card("Spending", self.get_spending_analytics()),
            self.create_analytics_card("GPA", self.get_gpa_analytics()),
            self.create_analytics_card("Grade Average", self.get_grade_analytics()),
            self.create_analytics_card("Focus Time", self.get_focus_analytics()),
        ], spacing=15, wrap=True)
        
        # Charts section
        charts_section = ft.Column([
            ft.Row([
                ft.Text("Analytics Charts", size=20, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton(
                    "Weekly Report",
                    icon=ft.Icons.SUMMARIZE,
                    on_click=self.show_weekly_report,
                    bgcolor=ft.Colors.INDIGO_700,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            self.no_charts_notice,
            self.spending_row,
            self.grades_row,
            self.focus_row,
        ], spacing=15)

        # Time blocks container
        self.priority_filter = ft.Dropdown(
            value="All",
            width=150,
            dense=True,
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
                ft.dropdown.Option("Pending Only"),
            ],
            on_change=lambda e: self.refresh_data(update_ui=False),
        )
        time_blocks_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_TODAY, color=ft.Colors.BLUE_400),
                            ft.Text(
                                f"Today's Schedule - {datetime.now().strftime('%B %d, %Y')}",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ], spacing=10),
                        self.priority_filter,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    self.rows_col,
                ]),
                padding=20,
            ),
            elevation=3,
        )

        self.refresh_data(update_ui=False)
        
        self.content = ft.Column([
                ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD),
                stats_row,
                analytics_row,
                charts_section,
                ft.Container(content=time_blocks_card, expand=True),
            ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)

    def create_stat_card(self, label, value_control, icon, color):
        """Create a statistics card"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=40, color=color),
                    value_control,
                    ft.Text(label, size=14, color=ft.Colors.GREY_400),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=20,
                width=180,
            ),
            elevation=2,
        )

    @with_error_handling
    def refresh_data(self, update_ui=True):
        """Refresh time blocks and statistics with error handling"""
        # Show loading state if updating UI
        if update_ui and hasattr(self, 'page') and self.page:
            self.rows_col.controls.clear()
            self.rows_col.controls.append(UIHelpers.create_loading_indicator("Loading dashboard..."))
            self.update()
        
        self.rows_col.controls.clear()
        # Get existing tasks for today
        tasks = self.db.get_tasks_for_today()
        task_map = {row[1]: (row[2], row[3], row[4]) for row in tasks}  # time_slot -> (name, status, priority)
        active_filter = self.priority_filter.value if hasattr(self, "priority_filter") else "All"

        # Generate rows from 8:00 AM to 10:00 PM
        start_hour = 8
        end_hour = 22
        
        completed = 0
        pending = 0
        
        for hour in range(start_hour, end_hour + 1):
            time_slot = f"{hour % 12 or 12}:00 {'AM' if hour < 12 else 'PM'}"
            task_name = ""
            status = "pending"
            priority = "Medium"
            
            if time_slot in task_map:
                task_name, status, priority = task_map[time_slot]
                if task_name:  # Only count if there's actually a task
                    if status == "completed":
                        completed += 1
                    else:
                        pending += 1

            if active_filter in {"High", "Medium", "Low"} and (not task_name or priority != active_filter):
                continue
            if active_filter == "Pending Only" and (not task_name or status == "completed"):
                continue

            row = TimeBlockRow(
                time_slot=time_slot,
                task_name=task_name,
                status=status,
                priority=priority,
                on_change=self.save_task
            )
            self.rows_col.controls.append(row)
        
        # Update stats
        self._apply_task_counts(completed, pending)
        total_tasks = completed + pending
        
        # Update streak
        current_streak, longest_streak = self.db.get_study_streak()
        self.streak_count.value = str(current_streak)
        
        # Update charts
        self.update_charts()
        
        if update_ui:
            # Show success message for dashboard refresh
            if hasattr(self, 'page') and self.page:
                show_success(self.page, f"Dashboard updated - {total_tasks} tasks loaded")
        if hasattr(self, 'page') and self.page:
            self.update()

    def _apply_task_counts(self, completed: int, pending: int) -> None:
        self.completed_count.value = str(completed)
        self.pending_count.value = str(pending)
        total_tasks = completed + pending
        self.productivity_text.value = f"{int((completed / total_tasks) * 100)}%" if total_tasks > 0 else "0%"

    def _recompute_task_counters(self) -> None:
        tasks = self.db.get_tasks_for_today()
        completed = sum(1 for row in tasks if row[2] and row[3] == "completed")
        pending = sum(1 for row in tasks if row[2] and row[3] != "completed")
        self._apply_task_counts(completed, pending)
        if hasattr(self, "page") and self.page:
            self.completed_count.update()
            self.pending_count.update()
            self.productivity_text.update()

    def save_task(self, time_slot, task_name, status, priority="Medium"):
        """Save task changes to database"""
        self.db.add_task(time_slot, task_name, status, priority)
        self._recompute_task_counters()
    
    def create_analytics_card(self, title, content):
        """Create an analytics card"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    content,
                ], spacing=10),
                padding=15,
                width=250,
            ),
            elevation=2,
        )
    
    def get_spending_analytics(self):
        """Get spending analytics widget"""
        try:
            daily_spending = self.db.get_daily_spending()
            budget = float(self.db.get_setting("daily_budget") or 50.0)
            percentage = (daily_spending / budget * 100) if budget > 0 else 0
            
            color = ft.Colors.GREEN_400 if percentage < 70 else (ft.Colors.ORANGE_400 if percentage < 100 else ft.Colors.RED_400)
            
            return ft.Column([
                ft.Text(f"${daily_spending:.2f} / ${budget:.2f}", size=20, weight=ft.FontWeight.BOLD, color=color),
                ft.ProgressBar(value=min(percentage / 100, 1.0), color=color, bgcolor=ft.Colors.GREY_700, height=8),
                ft.Text(f"{percentage:.0f}% of daily budget", size=12, color=ft.Colors.GREY_400),
            ], spacing=5)
        except:
            return ft.Text("No data", color=ft.Colors.GREY_400)
    
    def get_gpa_analytics(self):
        """Get GPA analytics widget"""
        try:
            gpa = self.db.calculate_gpa()
            
            if gpa is None:
                return ft.Text("No grades yet", color=ft.Colors.GREY_400)
            
            # Color based on GPA
            if gpa >= 3.7:
                color = ft.Colors.GREEN_400
                status = "Excellent!"
            elif gpa >= 3.0:
                color = ft.Colors.BLUE_400
                status = "Good"
            elif gpa >= 2.5:
                color = ft.Colors.ORANGE_400
                status = "Fair"
            else:
                color = ft.Colors.RED_400
                status = "Needs Work"
            
            return ft.Column([
                ft.Text(f"{gpa:.2f}", size=32, weight=ft.FontWeight.BOLD, color=color),
                ft.Text("/ 4.0", size=14, color=ft.Colors.GREY_500),
                ft.Divider(),
                ft.Text(status, size=13, color=color, weight=ft.FontWeight.BOLD),
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        except:
            return ft.Text("No data", color=ft.Colors.GREY_400)
    
    def get_grade_analytics(self):
        """Get grade analytics widget"""
        try:
            grade_stats = self.db.get_grade_stats()
            
            if not grade_stats:
                return ft.Text("No grades yet", color=ft.Colors.GREY_400)
            
            total_avg = sum(avg for _, avg in grade_stats) / len(grade_stats)
            color = ft.Colors.GREEN_400 if total_avg >= 85 else (ft.Colors.BLUE_400 if total_avg >= 70 else ft.Colors.ORANGE_400)
            
            return ft.Column([
                ft.Text(f"{total_avg:.1f}%", size=24, weight=ft.FontWeight.BOLD, color=color),
                ft.Text("Overall Average", size=12, color=ft.Colors.GREY_400),
                ft.Divider(),
                ft.Column([
                    ft.Row([
                        ft.Text(subject[:15], size=11),
                        ft.Text(f"{avg:.0f}%", size=11, weight=ft.FontWeight.BOLD),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    for subject, avg in grade_stats[:3]
                ], spacing=3),
            ], spacing=5)
        except:
            return ft.Text("No data", color=ft.Colors.GREY_400)
    
    def get_focus_analytics(self):
        """Get focus time analytics widget"""
        try:
            total_minutes = self.db.get_total_focus_time()
            hours = total_minutes // 60
            minutes = total_minutes % 60
            
            # Calculate daily average
            daily_avg = total_minutes / 7 if total_minutes > 0 else 0
            
            return ft.Column([
                ft.Text(f"{hours}h {minutes}m", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_400),
                ft.Text("Total (7 days)", size=12, color=ft.Colors.GREY_400),
                ft.Divider(),
                ft.Text(f"{daily_avg:.0f} min/day average", size=11, color=ft.Colors.PURPLE_300),
            ], spacing=5)
        except:
            return ft.Text("No data", color=ft.Colors.GREY_400)
    
    def _set_chart_image(self, image_control, row_control, b64_payload):
        if b64_payload:
            image_control.src = base64.b64decode(b64_payload)
            image_control.visible = True
            row_control.visible = True
            return True
        image_control.src = _EMPTY_PNG
        image_control.visible = False
        row_control.visible = False
        return False

    def update_charts(self):
        """Update all chart images"""
        try:
            any_visible = False

            budget = float(self.db.get_setting("daily_budget") or 50.0)
            spending_data = self.db.get_spending_chart_data(days=7)
            spending_img = create_spending_chart(spending_data, budget)
            any_visible = self._set_chart_image(self.spending_chart, self.spending_row, spending_img) or any_visible

            grades_data = self.db.get_grades_chart_data()
            grades_img = create_grades_chart(grades_data)
            any_visible = self._set_chart_image(self.grades_chart, self.grades_row, grades_img) or any_visible

            focus_data = self.db.get_focus_chart_data(days=7)
            focus_img = create_focus_chart(focus_data)
            any_visible = self._set_chart_image(self.focus_chart, self.focus_row, focus_img) or any_visible

            self.no_charts_notice.visible = not any_visible
        except Exception as e:
            print(f"Chart update error: {e}")
    
    def show_weekly_report(self, e):
        """Generate and display weekly report"""
        try:
            report = self.db.generate_weekly_report()
            
            # Create report dialog
            report_content = ft.Column([
                ft.Text("📊 Weekly Report", size=24, weight=ft.FontWeight.BOLD),
                ft.Text(f"Generated: {report['generated_at']}", size=12, color=ft.Colors.GREY_400),
                ft.Divider(),
                
                # Tasks
                ft.Text("📋 Tasks", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
                ft.Text(f"Total: {report['tasks']['total']} | Completed: {report['tasks']['completed']} | Pending: {report['tasks']['pending']}"),
                ft.Text(f"Completion Rate: {report['tasks']['completion_rate']}%", color=ft.Colors.GREEN_400),
                ft.Divider(),
                
                # Focus
                ft.Text("⏱️ Focus Sessions", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_400),
                ft.Text(f"Sessions: {report['focus']['sessions']} | Total: {report['focus']['hours']}h {report['focus']['total_minutes'] % 60}m"),
                ft.Text(f"Daily Average: {report['focus']['daily_average']:.1f} minutes", color=ft.Colors.PURPLE_300),
                ft.Divider(),
                
                # Spending
                ft.Text("💰 Spending", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400),
                ft.Text(f"Total: ${report['spending']['total']:.2f} | Daily Avg: ${report['spending']['daily_average']:.2f}"),
                ft.Column([
                    ft.Text(f"  • {cat}: ${amt:.2f}", size=12)
                    for cat, amt in report['spending']['by_category'].items()
                ], spacing=3) if report['spending']['by_category'] else ft.Text("No spending data"),
                ft.Divider(),
                
                # Assignments
                ft.Text("📚 Assignments", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400),
                ft.Text(f"New: {report['assignments']['total']} | Graded: {report['assignments']['graded']}"),
                ft.Text(f"Average Grade: {report['assignments']['average_grade']:.1f}%" if report['assignments']['average_grade'] else "No grades yet",
                       color=ft.Colors.CYAN_300),
                ft.Divider(),
                
                # GPA & Streak
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🎓 Current GPA", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{report['gpa']:.2f} / 4.0" if report['gpa'] else "N/A", 
                                   size=24, color=ft.Colors.GREEN_400),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=15,
                        bgcolor=ft.Colors.BLUE_GREY_900,
                        border_radius=10,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🔥 Study Streak", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{report['streak']['current']} days", size=24, color=ft.Colors.ORANGE_400),
                            ft.Text(f"Best: {report['streak']['longest']} days", size=12, color=ft.Colors.GREY_400),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=15,
                        bgcolor=ft.Colors.BLUE_GREY_900,
                        border_radius=10,
                        expand=True,
                    ),
                ], spacing=10),
            ], spacing=10, scroll=ft.ScrollMode.AUTO, height=600)
            
            dialog = ft.AlertDialog(
                title=ft.Text("Weekly Summary Report"),
                content=report_content,
                actions=[
                    ft.TextButton("Close", on_click=lambda e: self.close_dialog()),
                ],
            )
            
            if hasattr(self, 'page') and self.page:
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
        except Exception as e:
            print(f"Report generation error: {e}")
            if hasattr(self, 'page') and self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error generating report: {str(e)}"),
                    bgcolor=ft.Colors.RED_700,
                )
                self.page.snack_bar.open = True
                self.page.update()
    
    def close_dialog(self):
        """Close the current dialog"""
        if hasattr(self, 'page') and self.page and self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
