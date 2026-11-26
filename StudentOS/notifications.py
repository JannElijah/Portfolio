"""Desktop notification system for StudentOS"""
from plyer import notification
from datetime import datetime, timedelta
import threading
import time

class NotificationManager:
    def __init__(self, db):
        self.db = db
        self.is_running = False
        self.check_thread = None
        
    def send_notification(self, title, message, timeout=10):
        """Send a desktop notification"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="StudentOS",
                timeout=timeout
            )
        except Exception as e:
            print(f"Notification error: {e}")
    
    def check_assignment_deadlines(self):
        """Check for assignments due in the next 24 hours"""
        try:
            assignments = self.db.get_assignments()
            now = datetime.now()
            
            for assignment in assignments:
                if assignment[7] == "pending":  # Only pending assignments
                    due_date_str = assignment[4]
                    if due_date_str:
                        try:
                            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                            time_diff = due_date - now
                            
                            # Notify if due within 24 hours
                            if timedelta(0) < time_diff <= timedelta(hours=24):
                                hours_left = int(time_diff.total_seconds() / 3600)
                                self.send_notification(
                                    "📚 Assignment Deadline!",
                                    f"{assignment[2]} ({assignment[1]}) is due in {hours_left} hours!"
                                )
                            # Notify if overdue
                            elif time_diff < timedelta(0):
                                days_overdue = abs(time_diff.days)
                                self.send_notification(
                                    "⚠️ Overdue Assignment!",
                                    f"{assignment[2]} is {days_overdue} day(s) overdue!"
                                )
                        except:
                            pass
        except Exception as e:
            print(f"Assignment check error: {e}")
    
    def check_upcoming_events(self):
        """Check for events happening in the next hour"""
        try:
            events = self.db.get_events()
            now = datetime.now()
            
            for event in events:
                event_date_str = event[3]
                event_time_str = event[4]
                
                if event_date_str and event_time_str:
                    try:
                        event_datetime = datetime.strptime(
                            f"{event_date_str} {event_time_str}",
                            "%Y-%m-%d %H:%M"
                        )
                        time_diff = event_datetime - now
                        
                        # Notify if event is in 1 hour (with 5-minute tolerance)
                        if timedelta(minutes=55) <= time_diff <= timedelta(minutes=65):
                            self.send_notification(
                                f"📅 {event[2]} Event",
                                f"{event[1]} starts in 1 hour at {event_time_str}"
                            )
                    except:
                        pass
        except Exception as e:
            print(f"Event check error: {e}")
    
    def notify_focus_complete(self, duration_minutes):
        """Notify when a focus session completes"""
        self.send_notification(
            "✅ Focus Session Complete!",
            f"Great job! You focused for {duration_minutes} minutes. Time for a break! 🎉"
        )
    
    def notify_break_complete(self, break_minutes):
        """Notify when break time is over"""
        self.send_notification(
            "⏰ Break Time Over!",
            f"Your {break_minutes}-minute break is done. Ready for another focus session?"
        )
    
    def check_custom_reminders(self):
        """Check for custom reminders that are due"""
        try:
            pending_reminders = self.db.get_pending_reminders()
            
            for reminder in pending_reminders:
                reminder_id, entity_type, entity_id, reminder_time = reminder
                
                # Get entity details and send notification
                if entity_type == "event":
                    events = self.db.get_events()
                    event = next((e for e in events if e[0] == entity_id), None)
                    if event:
                        self.send_notification(
                            f"📅 {event[3]} Reminder",
                            f"{event[1]} - {event[4] if len(event) > 4 else ''}",
                            timeout=30
                        )
                elif entity_type == "assignment":
                    assignments = self.db.get_assignments()
                    assignment = next((a for a in assignments if a[0] == entity_id), None)
                    if assignment:
                        self.send_notification(
                            "📚 Assignment Reminder",
                            f"{assignment[2]} ({assignment[1]}) - Due: {assignment[4]}",
                            timeout=30
                        )
                
                # Mark as sent
                self.db.mark_reminder_sent(reminder_id)
                
        except Exception as e:
            print(f"Custom reminder check error: {e}")
    
    def background_check_loop(self):
        """Background thread to periodically check for notifications"""
        while self.is_running:
            try:
                # Check custom reminders every minute
                self.check_custom_reminders()
                
                # Check assignments every 30 minutes
                self.check_assignment_deadlines()
                
                # Check events every 10 minutes
                self.check_upcoming_events()
                
                # Wait 1 minute before next check (for custom reminders)
                time.sleep(60)
            except Exception as e:
                print(f"Background check error: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def start_background_checks(self):
        """Start background notification checking"""
        if not self.is_running:
            self.is_running = True
            self.check_thread = threading.Thread(target=self.background_check_loop, daemon=True)
            self.check_thread.start()
            print("📬 Notification system started")
    
    def stop_background_checks(self):
        """Stop background notification checking"""
        self.is_running = False
        if self.check_thread:
            self.check_thread = None
        print("📭 Notification system stopped")
