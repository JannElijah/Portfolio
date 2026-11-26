import flet as ft
from datetime import datetime, timedelta

class FocusHistoryView(ft.Column):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.spacing = 20
        
        # Date filter controls
        self.start_date = ft.TextField(
            label="From Date (YYYY-MM-DD)",
            width=200,
            value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        )
        self.end_date = ft.TextField(
            label="To Date (YYYY-MM-DD)",
            width=200,
            value=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Statistics cards
        self.total_sessions_text = ft.Text("0", size=30, weight=ft.FontWeight.BOLD)
        self.total_time_text = ft.Text("0h 0m", size=30, weight=ft.FontWeight.BOLD)
        self.avg_duration_text = ft.Text("0 min", size=30, weight=ft.FontWeight.BOLD)
        self.longest_session_text = ft.Text("0 min", size=30, weight=ft.FontWeight.BOLD)
        
        # Session list
        self.sessions_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)
        
        self.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text("Focus Session History", size=24, weight=ft.FontWeight.BOLD),
                    
                    # Statistics cards
                    ft.Row(
                        [
                            self.create_stat_card("Total Sessions", self.total_sessions_text, ft.Colors.BLUE_700),
                            self.create_stat_card("Total Time", self.total_time_text, ft.Colors.GREEN_700),
                            self.create_stat_card("Avg Duration", self.avg_duration_text, ft.Colors.ORANGE_700),
                            self.create_stat_card("Longest Session", self.longest_session_text, ft.Colors.PURPLE_700),
                        ],
                        spacing=15,
                        wrap=True,
                    ),
                    
                    ft.Divider(),
                    
                    # Filter controls
                    ft.Row(
                        [
                            self.start_date,
                            self.end_date,
                            ft.ElevatedButton(
                                "Apply Filter",
                                icon=ft.Icons.FILTER_LIST,
                                on_click=lambda _: self.load_sessions(),
                                bgcolor=ft.Colors.BLUE_700,
                                color="#FFFFFF"
                            ),
                            ft.ElevatedButton(
                                "Reset",
                                icon=ft.Icons.REFRESH,
                                on_click=self.reset_filters,
                                bgcolor=ft.Colors.GREY_700,
                                color="#FFFFFF"
                            ),
                        ],
                        spacing=10,
                    ),
                    
                    ft.Divider(),
                    
                    # Sessions list header
                    ft.Text("Session History", size=20, weight=ft.FontWeight.BOLD),
                    self.sessions_list,
                ]),
                padding=20,
            )
        ]
    
    def create_stat_card(self, title: str, value_control: ft.Text, color):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=14, color=ft.Colors.GREY_400),
                    value_control,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=color,
            padding=15,
            border_radius=10,
            width=200,
        )
    
    def load_sessions(self):
        """Load focus sessions with filters"""
        self.sessions_list.controls.clear()
        
        # Get filtered sessions
        start = self.start_date.value if self.start_date.value else None
        end = self.end_date.value if self.end_date.value else None
        
        sessions = self.db.get_focus_logs_with_dates(start, end)
        
        # Calculate statistics
        if sessions:
            total_sessions = len(sessions)
            total_minutes = sum(s[1] for s in sessions)
            avg_duration = total_minutes / total_sessions if total_sessions > 0 else 0
            longest = max(s[1] for s in sessions) if sessions else 0
            
            # Update stats
            self.total_sessions_text.value = str(total_sessions)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            self.total_time_text.value = f"{hours}h {minutes}m"
            self.avg_duration_text.value = f"{round(avg_duration)} min"
            self.longest_session_text.value = f"{longest} min"
            
            # Add session cards
            for session_id, duration, timestamp in sessions:
                self.sessions_list.controls.append(
                    self.create_session_card(session_id, duration, timestamp)
                )
        else:
            self.total_sessions_text.value = "0"
            self.total_time_text.value = "0h 0m"
            self.avg_duration_text.value = "0 min"
            self.longest_session_text.value = "0 min"
            
            self.sessions_list.controls.append(
                ft.Container(
                    content=ft.Text("No sessions found for this period", italic=True, color=ft.Colors.GREY_400),
                    padding=20,
                )
            )
        
        self.update()
    
    def create_session_card(self, session_id: int, duration: int, timestamp: str):
        """Create a card for a single session"""
        try:
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            date_str = dt.strftime("%b %d, %Y")
            time_str = dt.strftime("%I:%M %p")
        except:
            date_str = timestamp
            time_str = ""
        
        # Duration formatting
        hours = duration // 60
        minutes = duration % 60
        duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes} min"
        
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.TIMER, color=ft.Colors.BLUE_400),
                    ft.Column(
                        [
                            ft.Text(date_str, weight=ft.FontWeight.BOLD),
                            ft.Text(time_str, size=12, color=ft.Colors.GREY_400),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Text(duration_str, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                        bgcolor=ft.Colors.GREEN_700,
                        padding=ft.padding.symmetric(horizontal=15, vertical=8),
                        border_radius=15,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=ft.Colors.BLUE_GREY_900,
            padding=15,
            border_radius=10,
        )
    
    def reset_filters(self, e):
        """Reset date filters to default"""
        self.start_date.value = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.end_date.value = datetime.now().strftime("%Y-%m-%d")
        self.load_sessions()
    
    def did_mount(self):
        """Called when view is added to the page"""
        self.load_sessions()
