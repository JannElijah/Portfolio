import flet as ft
import time
import threading
import psutil
from datetime import datetime
from utils import UIHelpers, ValidationHelpers, ErrorHandler, show_success, show_error, with_error_handling


class FocusView(ft.Container):
    def __init__(self, db, notification_manager=None):
        super().__init__()
        self.db = db
        self.notification_manager = notification_manager
        self.expand = True
        self.padding = 20
        
        # Timer state
        self.total_seconds = 25 * 60  # 25 minutes
        self.current_seconds = self.total_seconds
        self.is_running = False
        self.timer_thread = None
        
        # Break timer state
        self.break_seconds = 5 * 60  # 5 minutes
        self.current_break_seconds = self.break_seconds
        self.is_on_break = False
        self.break_thread = None
        
        # Game blocker state
        self.blocker_active = False
        self.blocker_thread = None
        self.blacklisted_processes = []
        
        # Game blocker UI
        self.process_input = ft.TextField(
            label="Add Process to Block",
            hint_text="e.g., steam.exe, chrome.exe, discord.exe",
            border_color=ft.Colors.RED_400,
            focused_border_color=ft.Colors.RED_700,
            suffix_icon=ft.Icons.BLOCK,
        )
        
        self.blacklist_display = ft.Column(spacing=8)
        
        self.blocker_status = ft.Text(
            "🟢 Blocker Inactive",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREEN_400,
        )
        
        # UI components
        self.timer_text = ft.Text(
            value=self.format_time(self.current_seconds),
            size=120,
            color=ft.Colors.CYAN_400,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )
        
        self.status_text = ft.Text(
            "Ready to focus?",
            size=22,
            color=ft.Colors.GREY_400,
            text_align=ft.TextAlign.CENTER,
        )
        
        self.progress_ring = ft.ProgressRing(
            value=1.0,
            width=280,
            height=280,
            stroke_width=8,
            color=ft.Colors.CYAN_700,
        )
        
        # Buttons
        self.start_btn = ft.ElevatedButton(
            "Start Focus",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self.start_timer,
            bgcolor=ft.Colors.GREEN_700,
            color="#FFFFFF",
            height=50,
            width=160,
        )
        self.pause_btn = ft.ElevatedButton(
            "Pause",
            icon=ft.Icons.PAUSE,
            on_click=self.pause_timer,
            disabled=True,
            bgcolor=ft.Colors.ORANGE_700,
            color="#FFFFFF",
            height=50,
            width=160,
        )
        self.reset_btn = ft.OutlinedButton(
            "Reset",
            icon=ft.Icons.REFRESH,
            on_click=self.reset_timer,
            height=50,
            width=160,
        )
        
        # History list
        self.history_list = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        # Stats
        self.total_sessions = ft.Text("0", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400)
        self.total_minutes = ft.Text("0", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)

        self.build_ui()
    
    def build_ui(self):
        """Build the main UI"""
        # Game Blocker card
        blocker_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.BLOCK, color=ft.Colors.RED_400, size=32),
                        ft.Text("Game Blocker", size=22, weight=ft.FontWeight.BOLD),
                    ], spacing=10),
                    ft.Divider(),
                    
                    # Status
                    ft.Container(
                        content=self.blocker_status,
                        padding=10,
                        bgcolor=ft.Colors.GREY_900,
                        border_radius=8,
                    ),
                    
                    # Add process input
                    ft.Row([
                        self.process_input,
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE,
                            icon_color=ft.Colors.RED_400,
                            tooltip="Add to blacklist",
                            on_click=self.add_to_blacklist,
                        ),
                    ], spacing=10),
                    
                    # Blacklist display
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Blacklisted Processes:", size=14, weight=ft.FontWeight.BOLD),
                            self.blacklist_display,
                        ], spacing=10),
                        padding=10,
                        bgcolor=ft.Colors.GREY_900,
                        border_radius=8,
                    ),
                    
                    # Start blocker button
                    ft.ElevatedButton(
                        "Start Focus Session (with Blocker)",
                        icon=ft.Icons.SECURITY,
                        on_click=self.toggle_blocker,
                        bgcolor=ft.Colors.RED_700,
                        color="#FFFFFF",
                        width=300,
                    ),
                ], spacing=15),
                padding=20,
            ),
            elevation=3,
        )
        
        # Timer card with circular progress
        timer_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Pomodoro Timer", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(height=20),
                    ft.Stack([
                        ft.Container(
                            content=self.progress_ring,
                            alignment=ft.alignment.Alignment(0,0),
                        ),
                        ft.Container(
                            content=ft.Column([
                                self.timer_text,
                                self.status_text,
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            alignment=ft.alignment.Alignment(0,0),
                        ),
                    ], height=280),
                    ft.Container(height=20),
                    ft.Row([
                        self.start_btn,
                        self.pause_btn,
                        self.reset_btn,
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30,
            ),
            elevation=3,
        )
        
        # Stats row
        stats_row = ft.Row([
            self.create_stat_card("Sessions Today", self.total_sessions, ft.Icons.TIMER, ft.Colors.CYAN_700),
            self.create_stat_card("Minutes Focused", self.total_minutes, ft.Icons.TRENDING_UP, ft.Colors.GREEN_700),
        ], spacing=15, alignment=ft.MainAxisAlignment.CENTER)
        
        # History card
        history_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Session History", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self.history_list,
                ]),
                padding=20,
            ),
            elevation=3,
        )
        
        # Load initial data
        self.refresh_history(update_ui=False)
        self.update_blacklist_display()
        
        self.content = ft.Column([
            ft.Text("Focus Mode", size=28, weight=ft.FontWeight.BOLD),
            stats_row,
            ft.Row([
                ft.Container(content=timer_card, expand=2),
                ft.Container(content=blocker_card, expand=1),
            ], spacing=15, expand=True),
            ft.Container(content=history_card, expand=True),
        ], spacing=20, expand=True)

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
                width=220,
            ),
            elevation=2,
        )

    def format_time(self, seconds):
        """Format seconds to MM:SS"""
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    @with_error_handling
    def start_timer(self, e):
        """Start the focus timer"""
        if not self.is_running:
            self.is_running = True
            self.start_btn.disabled = True
            self.pause_btn.disabled = False
            self.status_text.value = "🎯 Focus Mode ON"
            self.status_text.color = ft.Colors.GREEN_400
            self.update()
            
            # Start timer thread
            self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
            self.timer_thread.start()

    def run_timer(self):
        """Run the timer countdown"""
        while self.is_running and self.current_seconds > 0:
            time.sleep(1)
            self.current_seconds -= 1
            self.timer_text.value = self.format_time(self.current_seconds)
            
            # Update progress ring
            progress = self.current_seconds / self.total_seconds
            self.progress_ring.value = progress
            
            # Change color based on time remaining
            if progress < 0.25:
                self.progress_ring.color = ft.Colors.RED_700
            elif progress < 0.5:
                self.progress_ring.color = ft.Colors.ORANGE_700
            else:
                self.progress_ring.color = ft.Colors.CYAN_700
            
            try:
                self.update()
            except Exception:
                break
        
        if self.current_seconds == 0 and self.is_running:
            self.complete_session()

    def pause_timer(self, e):
        """Pause the timer"""
        self.is_running = False
        self.start_btn.disabled = False
        self.pause_btn.disabled = True
        self.status_text.value = "⏸️ Paused"
        self.status_text.color = ft.Colors.ORANGE_400
        self.update()

    def reset_timer(self, e):
        """Reset the timer"""
        self.is_running = False
        self.current_seconds = self.total_seconds
        self.timer_text.value = self.format_time(self.current_seconds)
        self.progress_ring.value = 1.0
        self.progress_ring.color = ft.Colors.CYAN_700
        self.start_btn.disabled = False
        self.pause_btn.disabled = True
        self.status_text.value = "Ready to focus?"
        self.status_text.color = ft.Colors.GREY_400
        self.update()

    def complete_session(self):
        """Complete a focus session and save to database"""
        self.is_running = False
        
        # Save to database
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            duration = 25  # 25 minutes
            cursor.execute(
                "INSERT INTO focus_logs (duration, timestamp) VALUES (?, ?)",
                (duration, now)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving session: {e}")
        
        # Reset timer
        self.current_seconds = self.total_seconds
        self.timer_text.value = self.format_time(self.current_seconds)
        self.progress_ring.value = 1.0
        self.progress_ring.color = ft.Colors.CYAN_700
        self.start_btn.disabled = False
        self.pause_btn.disabled = True
        self.status_text.value = "🎉 Session Complete! Well done!"
        self.status_text.color = ft.Colors.GREEN_400
        
        # Refresh history
        self.refresh_history()
        self.update()
        
        # Send desktop notification
        if self.notification_manager:
            self.notification_manager.notify_focus_complete(duration)
        
        # Show snackbar
        self.show_snackbar("Focus session completed! Great work! 🎉", success=True)
        
        # Auto-start break timer
        self.start_break_timer()

    def start_break_timer(self):
        """Start the break timer"""
        self.is_on_break = True
        self.current_break_seconds = self.break_seconds
        self.timer_text.value = f"☕ {self.format_time(self.current_break_seconds)}"
        self.timer_text.color = ft.Colors.ORANGE_400
        self.status_text.value = "⏸️ Break Time! Relax and recharge"
        self.status_text.color = ft.Colors.ORANGE_300
        self.progress_ring.color = ft.Colors.ORANGE_700
        self.start_btn.disabled = True
        self.pause_btn.disabled = True
        self.update()
        
        # Start break countdown
        self.break_thread = threading.Thread(target=self.run_break_timer, daemon=True)
        self.break_thread.start()
    
    def run_break_timer(self):
        """Run the break countdown"""
        while self.is_on_break and self.current_break_seconds > 0:
            time.sleep(1)
            self.current_break_seconds -= 1
            
            if hasattr(self, 'page') and self.page:
                self.timer_text.value = f"☕ {self.format_time(self.current_break_seconds)}"
                self.progress_ring.value = self.current_break_seconds / self.break_seconds
                self.update()
        
        if self.is_on_break:
            self.complete_break()
    
    def complete_break(self):
        """Complete the break and notify user"""
        self.is_on_break = False
        
        # Reset to focus timer
        self.current_seconds = self.total_seconds
        self.timer_text.value = self.format_time(self.current_seconds)
        self.timer_text.color = ft.Colors.CYAN_400
        self.progress_ring.value = 1.0
        self.progress_ring.color = ft.Colors.CYAN_700
        self.start_btn.disabled = False
        self.pause_btn.disabled = True
        self.status_text.value = "✅ Break Over! Ready for another session?"
        self.status_text.color = ft.Colors.GREEN_400
        self.update()
        
        # Send notification
        if self.notification_manager:
            self.notification_manager.notify_break_complete(int(self.break_seconds / 60))
        
        # Show snackbar
        self.show_snackbar("Break time is over! Ready to focus again? 💪", success=True)
    
    def refresh_history(self, update_ui=True):
        """Load and display focus session history"""
        self.history_list.controls.clear()
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get all sessions
            cursor.execute(
                "SELECT duration, timestamp FROM focus_logs ORDER BY id DESC LIMIT 20"
            )
            rows = cursor.fetchall()
            
            # Get today's stats
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT COUNT(*), SUM(duration) FROM focus_logs WHERE DATE(timestamp) = ?",
                (today,)
            )
            stats = cursor.fetchone()
            sessions_today = stats[0] if stats[0] else 0
            minutes_today = stats[1] if stats[1] else 0
            
            conn.close()
            
            # Update stats
            self.total_sessions.value = str(sessions_today)
            self.total_minutes.value = str(minutes_today)
            
            # Display history
            if not rows:
                self.history_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(
                                ft.Icons.TIMER_OFF,
                                size=80,
                                color=ft.Colors.GREY_600,
                            ),
                            ft.Text(
                                "No sessions yet",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_500,
                            ),
                            ft.Text(
                                "Start your first focus session!",
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
                for row in rows:
                    duration, timestamp = row
                    self.history_list.controls.append(
                        self.create_history_card(duration, timestamp)
                    )
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history_list.controls.append(
                ft.Text("Error loading history", color=ft.Colors.RED_400)
            )
        
        if update_ui:
            self.update()

    def create_history_card(self, duration, timestamp):
        """Create a card for a history entry"""
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE,
                        color=ft.Colors.GREEN_400,
                        size=32,
                    ),
                    ft.Column([
                        ft.Text(
                            f"{duration} minutes focused",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            timestamp,
                            size=12,
                            color=ft.Colors.GREY_400,
                        ),
                    ], spacing=2, expand=True),
                    ft.Icon(
                        ft.Icons.PSYCHOLOGY,
                        color=ft.Colors.CYAN_400,
                        size=24,
                    ),
                ]),
                padding=15,
                bgcolor=ft.Colors.GREY_900,
                border_radius=10,
            ),
            elevation=1,
        )

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
    
    # --- Game Blocker Methods ---
    def add_to_blacklist(self, e):
        """Add a process to the blacklist"""
        process_name = self.process_input.value
        if process_name and process_name.strip():
            process_name = process_name.strip().lower()
            if process_name not in self.blacklisted_processes:
                self.blacklisted_processes.append(process_name)
                self.process_input.value = ""
                self.update_blacklist_display()
                self.show_snackbar(f"Added '{process_name}' to blacklist", success=True)
                self.update()
            else:
                self.show_snackbar("Process already in blacklist", error=True)
    
    def update_blacklist_display(self):
        """Update the blacklist display"""
        self.blacklist_display.controls.clear()
        
        if not self.blacklisted_processes:
            self.blacklist_display.controls.append(
                ft.Text("No processes blacklisted", size=12, color=ft.Colors.GREY_500, italic=True)
            )
        else:
            for proc in self.blacklisted_processes:
                self.blacklist_display.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.DANGEROUS, color=ft.Colors.RED_400, size=16),
                            ft.Text(proc, size=13, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_size=16,
                                icon_color=ft.Colors.RED_400,
                                tooltip="Remove",
                                on_click=lambda e, p=proc: self.remove_from_blacklist(p),
                            ),
                        ], spacing=5),
                        padding=8,
                        bgcolor=ft.Colors.RED_900,
                        border_radius=5,
                    )
                )
    
    def remove_from_blacklist(self, process_name):
        """Remove a process from the blacklist"""
        if process_name in self.blacklisted_processes:
            self.blacklisted_processes.remove(process_name)
            self.update_blacklist_display()
            self.show_snackbar(f"Removed '{process_name}' from blacklist", success=True)
            self.update()
    
    def toggle_blocker(self, e):
        """Toggle the game blocker on/off"""
        if not self.blocker_active:
            if not self.blacklisted_processes:
                self.show_snackbar("Add at least one process to blacklist first!", error=True)
                return
            
            # Start blocker
            self.blocker_active = True
            self.blocker_status.value = "🔴 Blocker Active - Monitoring..."
            self.blocker_status.color = ft.Colors.RED_400
            e.control.text = "Stop Focus Session"
            e.control.bgcolor = ft.Colors.GREEN_700
            
            # Start monitoring thread
            self.blocker_thread = threading.Thread(target=self.monitor_processes, daemon=True)
            self.blocker_thread.start()
            
            self.show_snackbar("Focus session started! Distractions will be blocked.", success=True)
        else:
            # Stop blocker
            self.blocker_active = False
            self.blocker_status.value = "🟢 Blocker Inactive"
            self.blocker_status.color = ft.Colors.GREEN_400
            e.control.text = "Start Focus Session (with Blocker)"
            e.control.bgcolor = ft.Colors.RED_700
            
            self.show_snackbar("Focus session ended.", success=True)
        
        self.update()
    
    def monitor_processes(self):
        """Background thread to monitor and kill blacklisted processes"""
        while self.blocker_active:
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc_name = proc.info['name'].lower()
                        if proc_name in self.blacklisted_processes:
                            # Kill the process
                            proc.kill()
                            # Show warning
                            self.show_snackbar(
                                f"⚠️ Blocked and terminated: {proc_name}",
                                error=True
                            )
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                # Check every 5 seconds
                time.sleep(5)
                
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(5)






