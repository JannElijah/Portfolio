import flet as ft

class StudyStatsView(ft.Column):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.spacing = 20
        
        # Content areas
        self.notes_by_subject = ft.Column(spacing=10)
        self.flashcards_by_subject = ft.Column(spacing=10)
        self.assignments_by_subject = ft.Column(spacing=10)
        self.focus_stats = ft.Column(spacing=10)
        
        self.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Text("Study Statistics", size=24, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.Icons.REFRESH,
                                on_click=lambda _: self.load_statistics(),
                                tooltip="Refresh statistics"
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    
                    ft.Divider(),
                    
                    # Two column layout
                    ft.Row(
                        [
                            # Left column
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Notes by Subject", size=18, weight=ft.FontWeight.BOLD),
                                    self.notes_by_subject,
                                    
                                    ft.Divider(height=20),
                                    
                                    ft.Text("Flashcards by Subject", size=18, weight=ft.FontWeight.BOLD),
                                    self.flashcards_by_subject,
                                ]),
                                expand=True,
                                padding=10,
                            ),
                            
                            # Right column
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("📊 Assignments by Subject", size=18, weight=ft.FontWeight.BOLD),
                                    self.assignments_by_subject,
                                    
                                    ft.Divider(height=20),
                                    
                                    ft.Text("⚡ Focus Statistics", size=18, weight=ft.FontWeight.BOLD),
                                    self.focus_stats,
                                ]),
                                expand=True,
                                padding=10,
                            ),
                        ],
                        expand=True,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                ]),
                padding=20,
            )
        ]
    
    def load_statistics(self):
        """Load all study statistics"""
        self.notes_by_subject.controls.clear()
        self.flashcards_by_subject.controls.clear()
        self.assignments_by_subject.controls.clear()
        self.focus_stats.controls.clear()
        
        # Get statistics from database
        stats = self.db.get_study_statistics()
        focus_stats = self.db.get_focus_statistics()
        
        # Notes by subject
        if stats['notes_by_subject']:
            for subject, count in stats['notes_by_subject']:
                self.notes_by_subject.controls.append(
                    self.create_subject_bar(subject or "No Subject", count, ft.Colors.BLUE_700)
                )
        else:
            self.notes_by_subject.controls.append(
                ft.Text("No notes yet", italic=True, color=ft.Colors.GREY_400)
            )
        
        # Add total
        self.notes_by_subject.controls.append(
            ft.Container(
                content=ft.Text(f"Total: {stats['total_notes']} notes", weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.BLUE_900,
                padding=10,
                border_radius=5,
                margin=ft.margin.only(top=10)
            )
        )
        
        # Flashcards by subject
        if stats['flashcards_by_subject']:
            for subject, count in stats['flashcards_by_subject']:
                self.flashcards_by_subject.controls.append(
                    self.create_subject_bar(subject or "No Subject", count, ft.Colors.GREEN_700)
                )
        else:
            self.flashcards_by_subject.controls.append(
                ft.Text("No flashcards yet", italic=True, color=ft.Colors.GREY_400)
            )
        
        # Add total
        self.flashcards_by_subject.controls.append(
            ft.Container(
                content=ft.Text(f"Total: {stats['total_flashcards']} flashcards", weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.GREEN_900,
                padding=10,
                border_radius=5,
                margin=ft.margin.only(top=10)
            )
        )
        
        # Assignments by subject
        if stats['assignments_by_subject']:
            for subject, count, avg_grade in stats['assignments_by_subject']:
                grade_text = f"{round(avg_grade, 1)}%" if avg_grade else "N/A"
                self.assignments_by_subject.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(subject, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Text(f"{count} assignments", size=12, color=ft.Colors.GREY_400),
                                ft.Container(
                                    content=ft.Text(grade_text, color="#FFFFFF"),
                                    bgcolor=ft.Colors.PURPLE_700,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                    border_radius=10,
                                ),
                            ]
                        ),
                        bgcolor=ft.Colors.BLUE_GREY_900,
                        padding=10,
                        border_radius=8,
                    )
                )
        else:
            self.assignments_by_subject.controls.append(
                ft.Text("No graded assignments yet", italic=True, color=ft.Colors.GREY_400)
            )
        
        # Focus statistics
        self.focus_stats.controls.extend([
            self.create_stat_row("Total Sessions", str(focus_stats['total_sessions']), ft.Icons.TIMER),
            self.create_stat_row("Total Time", f"{focus_stats['total_minutes']} min ({focus_stats['total_minutes']//60}h {focus_stats['total_minutes']%60}m)", ft.Icons.ACCESS_TIME),
            self.create_stat_row("Average Duration", f"{focus_stats['average_duration']} min", ft.Icons.TRENDING_UP),
            self.create_stat_row("Longest Session", f"{focus_stats['longest_session']} min", ft.Icons.MILITARY_TECH),
            self.create_stat_row("This Week", f"{focus_stats['sessions_this_week']} sessions", ft.Icons.DATE_RANGE),
            self.create_stat_row("This Month", f"{focus_stats['sessions_this_month']} sessions", ft.Icons.CALENDAR_MONTH),
            self.create_stat_row("Today", f"{focus_stats['sessions_today']} sessions", ft.Icons.TODAY),
        ])
        
        # Most productive day
        day, sessions, total_time = stats['most_productive_day']
        if day:
            self.focus_stats.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("🏆 Most Productive Day", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{day}: {sessions} sessions, {total_time} min", size=12),
                    ]),
                    bgcolor=ft.Colors.AMBER_900,
                    padding=10,
                    border_radius=8,
                    margin=ft.margin.only(top=10)
                )
            )
        
        self.update()
    
    def create_subject_bar(self, subject: str, count: int, color):
        """Create a horizontal bar for subject statistics"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(subject, weight=ft.FontWeight.BOLD, size=14),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Text(str(count), color="#FFFFFF"),
                        bgcolor=color,
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=10,
                    ),
                ]
            ),
            bgcolor=ft.Colors.BLUE_GREY_900,
            padding=10,
            border_radius=8,
        )
    
    def create_stat_row(self, label: str, value: str, icon):
        """Create a statistics row"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=20, color=ft.Colors.BLUE_400),
                    ft.Text(label, size=14),
                    ft.Container(expand=True),
                    ft.Text(value, weight=ft.FontWeight.BOLD),
                ]
            ),
            bgcolor=ft.Colors.BLUE_GREY_900,
            padding=10,
            border_radius=8,
        )
    
    def did_mount(self):
        """Called when view is added to the page"""
        self.load_statistics()
