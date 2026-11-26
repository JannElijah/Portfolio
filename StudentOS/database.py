import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="student_os_fixed.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        cursor = conn.cursor()
        
        # Subjects
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT,
                room TEXT,
                schedule TEXT,
                credit_hours REAL DEFAULT 3.0
            )
        ''')

        # Tasks (Time Blocking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time_slot TEXT NOT NULL,
                task_name TEXT NOT NULL,
                status TEXT DEFAULT "pending",
                priority TEXT DEFAULT "Medium",
                date TEXT NOT NULL
            )
        ''')

        # Projects
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                stack TEXT,
                status TEXT
            )
        ''')

        # Finance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS finance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT,
                date TEXT NOT NULL
            )
        ''')

        # Focus Logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS focus_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                duration INTEGER,
                timestamp TEXT
            )
        ''')
        
        # Assignments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT NOT NULL,
                grade REAL,
                max_grade REAL,
                status TEXT DEFAULT "pending",
                submission_date TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Events/Calendar
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                event_type TEXT,
                start_date TEXT NOT NULL,
                end_date TEXT,
                location TEXT,
                reminder_minutes INTEGER,
                recurrence_pattern TEXT DEFAULT "none",
                recurrence_end_date TEXT,
                parent_event_id INTEGER,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Notes & Flashcards
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                note_type TEXT DEFAULT "note",
                flashcard_front TEXT,
                flashcard_back TEXT,
                tags TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        ''')
        
        # Settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        # Reminders
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                reminder_time TEXT NOT NULL,
                is_sent INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Goals
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_type TEXT NOT NULL,
                target_value REAL NOT NULL,
                current_value REAL DEFAULT 0,
                time_period TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TEXT NOT NULL
            )
        ''')
        
        # Time Tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                entity_name TEXT NOT NULL,
                duration INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Initialize default settings
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ("theme", "dark"))
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ("daily_budget", "50.0"))
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ("focus_duration", "25"))
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ("break_duration", "5"))
        
        # Migration: Add priority column to tasks if it doesn't exist
        try:
            cursor.execute("SELECT priority FROM tasks LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'Medium'")
        
        # Migration: Add credit_hours column to subjects if it doesn't exist
        try:
            cursor.execute("SELECT credit_hours FROM subjects LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE subjects ADD COLUMN credit_hours REAL DEFAULT 3.0")
        
        # Migration: Add recurrence fields to events if they don't exist
        try:
            cursor.execute("SELECT recurrence_pattern FROM events LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE events ADD COLUMN recurrence_pattern TEXT DEFAULT 'none'")
            cursor.execute("ALTER TABLE events ADD COLUMN recurrence_end_date TEXT")
            cursor.execute("ALTER TABLE events ADD COLUMN parent_event_id INTEGER")
        
        # Custom Categories Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                color TEXT DEFAULT '#607D8B',
                is_default INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Quick Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quick_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_text TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                category TEXT DEFAULT 'General',
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        ''')
        
        # Add default categories
        default_categories = [
            ('Food', 'expense', '#FF5722', 1),
            ('Transportation', 'expense', '#FF9800', 1),
            ('Books', 'expense', '#2196F3', 1),
            ('Entertainment', 'expense', '#9C27B0', 1),
            ('Class', 'event', '#2196F3', 1),
            ('Meeting', 'event', '#9C27B0', 1),
            ('Exam', 'event', '#F44336', 1),
            ('Study Session', 'event', '#4CAF50', 1),
        ]
        
        for name, cat_type, color, is_default in default_categories:
            cursor.execute(
                "INSERT OR IGNORE INTO categories (name, type, color, is_default, created_at) VALUES (?, ?, ?, ?, ?)",
                (name, cat_type, color, is_default, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
        
        # Migration: Add file_paths column to assignments, projects, notes if they don't exist
        try:
            cursor.execute("SELECT file_paths FROM assignments LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE assignments ADD COLUMN file_paths TEXT")
        
        try:
            cursor.execute("SELECT file_paths FROM projects LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE projects ADD COLUMN file_paths TEXT")
        
        try:
            cursor.execute("SELECT file_paths FROM notes LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE notes ADD COLUMN file_paths TEXT")
        
        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_name, check_same_thread=False)

    # --- Tasks ---
    def add_task(self, time_slot: str, task_name: str, status: str = "pending", priority: str = "Medium"):
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO tasks (time_slot, task_name, status, priority, date) VALUES (?, ?, ?, ?, ?)",
                       (time_slot, task_name, status, priority, today))
        conn.commit()
        conn.close()

    def get_tasks_for_today(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT id, time_slot, task_name, status, priority FROM tasks WHERE date = ?", (today,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def update_task_status(self, task_id: int, status: str):
         conn = self.get_connection()
         cursor = conn.cursor()
         cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
         conn.commit()
         conn.close()

    # --- Finance ---
    def add_expense(self, item: str, amount: float, category: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO finance (item, amount, category, date) VALUES (?, ?, ?, ?)",
                       (item, amount, category, today))
        conn.commit()
        conn.close()

    def get_expenses(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT item, amount, category, date FROM finance ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_expenses_filtered(self, category: str = None, start_date: str = None, end_date: str = None, limit: int = 100):
        """Get expenses with advanced filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT item, amount, category, date FROM finance WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if start_date:
            query += " AND date(date) >= date(?)"
            params.append(start_date)
        
        if end_date:
            query += " AND date(date) <= date(?)"
            params.append(end_date)
        
        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit if limit is not None else 100)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_daily_spending(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT SUM(amount) FROM finance WHERE date = ?", (today,))
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 0.0

    # --- Projects ---
    def add_project(self, name: str, stack: str, status: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO projects (name, stack, status) VALUES (?, ?, ?)",
                       (name, stack, status))
        conn.commit()
        conn.close()

    def get_projects(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, stack, status FROM projects")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def update_project_status(self, project_id: int, status: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET status = ? WHERE id = ?", (status, project_id))
        conn.commit()
        conn.close()
    
    def add_quick_task(self, task_name: str):
        """Add a quick capture task to today's schedule"""
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        # Add to next available time slot or a default one
        cursor.execute("INSERT INTO tasks (time_slot, task_name, status, date) VALUES (?, ?, ?, ?)",
                       ("Quick", task_name, "pending", today))
        conn.commit()
        conn.close()
    
    # --- Subjects ---
    def add_subject(self, name: str, code: str, room: str, schedule: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subjects (name, code, room, schedule) VALUES (?, ?, ?, ?)", (name, code, room, schedule))
        conn.commit()
        conn.close()
        
    def get_subjects(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, code, room, schedule FROM subjects")
        rows = cursor.fetchall()
        conn.close()
        return rows    
    # --- Focus Logs ---
    def add_focus_log(self, duration: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO focus_logs (duration, timestamp) VALUES (?, ?)", (duration, timestamp))
        conn.commit()
        conn.close()
    
    def get_focus_logs(self, limit: int = 30):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT duration, timestamp FROM focus_logs ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_focus_logs_with_dates(self, start_date: str = None, end_date: str = None):
        """Get focus logs filtered by date range"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute(
                "SELECT id, duration, timestamp FROM focus_logs WHERE date(timestamp) BETWEEN date(?) AND date(?) ORDER BY timestamp DESC",
                (start_date, end_date)
            )
        elif start_date:
            cursor.execute(
                "SELECT id, duration, timestamp FROM focus_logs WHERE date(timestamp) >= date(?) ORDER BY timestamp DESC",
                (start_date,)
            )
        else:
            cursor.execute("SELECT id, duration, timestamp FROM focus_logs ORDER BY timestamp DESC LIMIT 100")
        
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_focus_statistics(self):
        """Get comprehensive focus session statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total sessions
        cursor.execute("SELECT COUNT(*) FROM focus_logs")
        stats['total_sessions'] = cursor.fetchone()[0]
        
        # Total time (in minutes)
        cursor.execute("SELECT SUM(duration) FROM focus_logs")
        result = cursor.fetchone()[0]
        stats['total_minutes'] = result if result else 0
        
        # Average session duration
        cursor.execute("SELECT AVG(duration) FROM focus_logs")
        result = cursor.fetchone()[0]
        stats['average_duration'] = round(result, 1) if result else 0
        
        # Longest session
        cursor.execute("SELECT MAX(duration) FROM focus_logs")
        result = cursor.fetchone()[0]
        stats['longest_session'] = result if result else 0
        
        # Sessions this week
        cursor.execute("SELECT COUNT(*) FROM focus_logs WHERE date(timestamp) >= date('now', '-7 days')")
        stats['sessions_this_week'] = cursor.fetchone()[0]
        
        # Sessions this month
        cursor.execute("SELECT COUNT(*) FROM focus_logs WHERE date(timestamp) >= date('now', '-30 days')")
        stats['sessions_this_month'] = cursor.fetchone()[0]
        
        # Sessions today
        cursor.execute("SELECT COUNT(*) FROM focus_logs WHERE date(timestamp) = date('now')")
        stats['sessions_today'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    # --- Assignments ---
    def add_assignment(self, subject: str, title: str, description: str, due_date: str, max_grade: float = 100.0):
        conn = self.get_connection()
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO assignments (subject, title, description, due_date, max_grade, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (subject, title, description, due_date, max_grade, created_at)
        )
        assignment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return assignment_id
    
    def get_assignments(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, subject, title, description, due_date, grade, max_grade, status, submission_date FROM assignments ORDER BY due_date")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_assignments_filtered(self, subject: str = None, status: str = None, start_date: str = None, end_date: str = None):
        """Get assignments with advanced filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT id, subject, title, description, due_date, grade, max_grade, status, submission_date FROM assignments WHERE 1=1"
        params = []
        
        if subject:
            query += " AND subject = ?"
            params.append(subject)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if start_date:
            query += " AND date(due_date) >= date(?)"
            params.append(start_date)
        
        if end_date:
            query += " AND date(due_date) <= date(?)"
            params.append(end_date)
        
        query += " ORDER BY due_date"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def update_assignment_grade(self, assignment_id: int, grade: float, status: str = "graded"):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE assignments SET grade = ?, status = ? WHERE id = ?", (grade, status, assignment_id))
        conn.commit()
        conn.close()
    
    def submit_assignment(self, assignment_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        submission_date = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("UPDATE assignments SET status = 'submitted', submission_date = ? WHERE id = ?", (submission_date, assignment_id))
        conn.commit()
        conn.close()
    
    # --- Events ---
    def add_event(self, title: str, description: str, event_type: str, start_date: str, end_date: str = None, 
                  location: str = None, reminder_minutes: int = 60, recurrence_pattern: str = "none", 
                  recurrence_end_date: str = None):
        """Add an event with optional recurrence"""
        conn = self.get_connection()
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO events (title, description, event_type, start_date, end_date, location, reminder_minutes, recurrence_pattern, recurrence_end_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (title, description, event_type, start_date, end_date, location, reminder_minutes, recurrence_pattern, recurrence_end_date, created_at)
        )
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Generate recurring instances if needed
        if recurrence_pattern != "none" and recurrence_end_date:
            self.generate_recurring_events(event_id, title, description, event_type, start_date, 
                                          end_date, location, reminder_minutes, recurrence_pattern, 
                                          recurrence_end_date)
        
        return event_id
    
    def generate_recurring_events(self, parent_id: int, title: str, description: str, event_type: str,
                                  start_date: str, end_date: str, location: str, reminder_minutes: int,
                                  pattern: str, recurrence_end: str):
        """Generate all instances of a recurring event"""
        from datetime import datetime, timedelta
        
        # Parse start_date with time if present, otherwise just date
        if " " in start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
            time_str = start.strftime(" %H:%M")
        else:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            time_str = ""
        
        recur_end = datetime.strptime(recurrence_end, "%Y-%m-%d")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate duration if end_date exists
        duration_days = 0
        if end_date:
            if " " in end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
            else:
                end = datetime.strptime(end_date, "%Y-%m-%d")
            duration_days = (end - start).days
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        current = start
        if pattern == "daily":
            delta = timedelta(days=1)
        elif pattern == "weekly":
            delta = timedelta(weeks=1)
        elif pattern == "monthly":
            delta = timedelta(days=30)  # Approximate
        else:
            conn.close()
            return
        
        # Skip first instance (already created), generate the rest
        current += delta
        
        # Compare only dates, not times
        while current.date() <= recur_end.date():
            instance_start = current.strftime("%Y-%m-%d") + time_str
            instance_end = ((current + timedelta(days=duration_days)).strftime("%Y-%m-%d") + time_str) if end_date else None
            
            cursor.execute(
                "INSERT INTO events (title, description, event_type, start_date, end_date, location, reminder_minutes, recurrence_pattern, parent_event_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (title, description, event_type, instance_start, instance_end, location, reminder_minutes, pattern, parent_id, created_at)
            )
            
            current += delta
        
        conn.commit()
        conn.close()
    
    def get_events(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, event_type, start_date, end_date, location, recurrence_pattern, parent_event_id FROM events ORDER BY start_date")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_events_filtered(self, event_type: str = None, start_date: str = None, end_date: str = None):
        """Get events with advanced filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT id, title, description, event_type, start_date, end_date, location, recurrence_pattern, parent_event_id FROM events WHERE 1=1"
        params = []
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if start_date:
            query += " AND date(start_date) >= date(?)"
            params.append(start_date)
        
        if end_date:
            query += " AND date(start_date) <= date(?)"
            params.append(end_date)
        
        query += " ORDER BY start_date"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_events_for_week(self, start_date: str):
        """Get all events for a week starting from start_date"""
        from datetime import datetime, timedelta
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = start + timedelta(days=7)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, description, event_type, start_date, end_date, location FROM events WHERE start_date >= ? AND start_date < ? ORDER BY start_date",
            (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def delete_event(self, event_id: int, delete_all: bool = False):
        """Delete event(s). If delete_all=True, deletes all instances of recurring event"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if delete_all:
            # Get parent_id if this is a child event
            cursor.execute("SELECT parent_event_id FROM events WHERE id = ?", (event_id,))
            result = cursor.fetchone()
            parent_id = result[0] if result and result[0] else event_id
            
            # Delete parent and all children
            cursor.execute("DELETE FROM events WHERE id = ? OR parent_event_id = ?", (parent_id, parent_id))
        else:
            # Delete only this instance
            cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        
        conn.commit()
        conn.close()
    
    # --- Reminders ---
    def add_reminder(self, entity_type: str, entity_id: int, reminder_time: str):
        """Add a reminder for an event or assignment"""
        conn = self.get_connection()
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO reminders (entity_type, entity_id, reminder_time, created_at) VALUES (?, ?, ?, ?)",
            (entity_type, entity_id, reminder_time, created_at)
        )
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return reminder_id
    
    def get_reminders(self, entity_type: str, entity_id: int):
        """Get all reminders for an entity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, reminder_time, is_sent FROM reminders WHERE entity_type = ? AND entity_id = ? ORDER BY reminder_time",
            (entity_type, entity_id)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_pending_reminders(self):
        """Get all unsent reminders that are due"""
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, entity_type, entity_id, reminder_time FROM reminders WHERE is_sent = 0 AND reminder_time <= ?",
            (now,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def mark_reminder_sent(self, reminder_id: int):
        """Mark a reminder as sent"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE reminders SET is_sent = 1 WHERE id = ?", (reminder_id,))
        conn.commit()
        conn.close()
    
    def delete_reminder(self, reminder_id: int):
        """Delete a reminder"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
        conn.close()
    
    # --- Goals ---
    def add_goal(self, goal_type: str, target_value: float, time_period: str, start_date: str, end_date: str):
        """Add a new goal"""
        conn = self.get_connection()
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO goals (goal_type, target_value, current_value, time_period, start_date, end_date, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (goal_type, target_value, 0, time_period, start_date, end_date, 'active', created_at)
        )
        goal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return goal_id
    
    def get_goals(self, status: str = None):
        """Get all goals, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if status:
            cursor.execute(
                "SELECT id, goal_type, target_value, current_value, time_period, start_date, end_date, status FROM goals WHERE status = ? ORDER BY created_at DESC",
                (status,)
            )
        else:
            cursor.execute("SELECT id, goal_type, target_value, current_value, time_period, start_date, end_date, status FROM goals ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def update_goal_progress(self, goal_id: int, current_value: float):
        """Update the current progress of a goal"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE goals SET current_value = ? WHERE id = ?", (current_value, goal_id))
        
        # Check if goal is completed
        cursor.execute("SELECT target_value, current_value FROM goals WHERE id = ?", (goal_id,))
        target, current = cursor.fetchone()
        if current >= target:
            cursor.execute("UPDATE goals SET status = 'completed' WHERE id = ?", (goal_id,))
        
        conn.commit()
        conn.close()
    
    def delete_goal(self, goal_id: int):
        """Delete a goal"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        conn.commit()
        conn.close()
    
    # --- Time Tracking ---
    def add_time_entry(self, entity_type: str, entity_id: int, entity_name: str, duration: int, start_time: str, end_time: str, notes: str = None):
        """Add a time tracking entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO time_tracking (entity_type, entity_id, entity_name, duration, start_time, end_time, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (entity_type, entity_id, entity_name, duration, start_time, end_time, notes, created_at)
        )
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return entry_id
    
    def get_time_entries(self, entity_type: str = None, entity_id: int = None, limit: int = 100):
        """Get time tracking entries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if entity_type and entity_id:
            cursor.execute(
                "SELECT id, entity_type, entity_id, entity_name, duration, start_time, end_time, notes FROM time_tracking WHERE entity_type = ? AND entity_id = ? ORDER BY start_time DESC LIMIT ?",
                (entity_type, entity_id, limit)
            )
        elif entity_type:
            cursor.execute(
                "SELECT id, entity_type, entity_id, entity_name, duration, start_time, end_time, notes FROM time_tracking WHERE entity_type = ? ORDER BY start_time DESC LIMIT ?",
                (entity_type, limit)
            )
        else:
            cursor.execute(
                "SELECT id, entity_type, entity_id, entity_name, duration, start_time, end_time, notes FROM time_tracking ORDER BY start_time DESC LIMIT ?",
                (limit,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_time_summary_by_entity(self, entity_type: str = None):
        """Get total time spent per entity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if entity_type:
            cursor.execute(
                "SELECT entity_name, SUM(duration) as total FROM time_tracking WHERE entity_type = ? GROUP BY entity_name ORDER BY total DESC",
                (entity_type,)
            )
        else:
            cursor.execute(
                "SELECT entity_type, entity_name, SUM(duration) as total FROM time_tracking GROUP BY entity_type, entity_name ORDER BY total DESC"
            )
        
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def delete_time_entry(self, entry_id: int):
        """Delete a time tracking entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM time_tracking WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()
    
    # --- Notes ---
    def add_note(self, title: str, content: str, subject: str = None, tags: str = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO notes (subject, title, content, note_type, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (subject, title, content, "note", tags, created_at, created_at)
        )
        conn.commit()
        conn.close()
    
    def add_flashcard(self, title: str, front: str, back: str, subject: str = None, tags: str = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO notes (subject, title, content, note_type, flashcard_front, flashcard_back, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (subject, title, f"{front} | {back}", "flashcard", front, back, tags, created_at, created_at)
        )
        conn.commit()
        conn.close()
    
    def get_notes(self, note_type: str = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if note_type:
            cursor.execute("SELECT id, subject, title, content, note_type, flashcard_front, flashcard_back, tags, created_at FROM notes WHERE note_type = ? ORDER BY created_at DESC", (note_type,))
        else:
            cursor.execute("SELECT id, subject, title, content, note_type, flashcard_front, flashcard_back, tags, created_at FROM notes ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def delete_note(self, note_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        conn.close()
    
    def get_study_statistics(self):
        """Get comprehensive study statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Notes per subject
        cursor.execute("""
            SELECT subject, COUNT(*) as count 
            FROM notes 
            WHERE note_type = 'note' AND subject IS NOT NULL 
            GROUP BY subject 
            ORDER BY count DESC
        """)
        stats['notes_by_subject'] = cursor.fetchall()
        
        # Flashcards per subject
        cursor.execute("""
            SELECT subject, COUNT(*) as count 
            FROM notes 
            WHERE note_type = 'flashcard' AND subject IS NOT NULL 
            GROUP BY subject 
            ORDER BY count DESC
        """)
        stats['flashcards_by_subject'] = cursor.fetchall()
        
        # Total notes and flashcards
        cursor.execute("SELECT COUNT(*) FROM notes WHERE note_type = 'note'")
        stats['total_notes'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM notes WHERE note_type = 'flashcard'")
        stats['total_flashcards'] = cursor.fetchone()[0]
        
        # Assignments by subject
        cursor.execute("""
            SELECT subject, COUNT(*) as count, AVG(grade * 100.0 / max_grade) as avg_grade
            FROM assignments 
            WHERE grade IS NOT NULL 
            GROUP BY subject 
            ORDER BY count DESC
        """)
        stats['assignments_by_subject'] = cursor.fetchall()
        
        # Most productive day (most focus sessions)
        cursor.execute("""
            SELECT date(timestamp) as day, COUNT(*) as sessions, SUM(duration) as total_time
            FROM focus_logs 
            GROUP BY day 
            ORDER BY total_time DESC 
            LIMIT 1
        """)
        result = cursor.fetchone()
        stats['most_productive_day'] = result if result else (None, 0, 0)
        
        conn.close()
        return stats
    
    # --- Settings ---
    def get_setting(self, key: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def update_setting(self, key: str, value: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()
    
    # --- Analytics ---
    def get_spending_by_category(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT category, SUM(amount) FROM finance GROUP BY category")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_weekly_spending(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DATE(date) as day, SUM(amount) as total 
            FROM finance 
            WHERE date >= date('now', '-7 days')
            GROUP BY day 
            ORDER BY day
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_grade_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT subject, AVG(grade * 100.0 / max_grade) as avg_percentage 
            FROM assignments 
            WHERE grade IS NOT NULL AND max_grade > 0
            GROUP BY subject
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_total_focus_time(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(duration) FROM focus_logs WHERE date(timestamp) >= date('now', '-7 days')")
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 0
    
    # --- GPA Calculation ---
    def calculate_gpa(self):
        """Calculate GPA based on graded assignments and subject credit hours"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get average grade percentage per subject
        cursor.execute("""
            SELECT subject, AVG(grade * 100.0 / max_grade) as avg_percentage 
            FROM assignments 
            WHERE grade IS NOT NULL AND max_grade > 0
            GROUP BY subject
        """)
        subject_grades = cursor.fetchall()
        
        if not subject_grades:
            conn.close()
            return None
        
        total_grade_points = 0
        total_credits = 0
        
        for subject_name, avg_percentage in subject_grades:
            # Get credit hours for this subject (default 3.0 if not found)
            cursor.execute("SELECT credit_hours FROM subjects WHERE name = ?", (subject_name,))
            result = cursor.fetchone()
            credit_hours = result[0] if result else 3.0
            
            # Convert percentage to 4.0 scale
            if avg_percentage >= 93:
                grade_point = 4.0
            elif avg_percentage >= 90:
                grade_point = 3.7
            elif avg_percentage >= 87:
                grade_point = 3.3
            elif avg_percentage >= 83:
                grade_point = 3.0
            elif avg_percentage >= 80:
                grade_point = 2.7
            elif avg_percentage >= 77:
                grade_point = 2.3
            elif avg_percentage >= 73:
                grade_point = 2.0
            elif avg_percentage >= 70:
                grade_point = 1.7
            elif avg_percentage >= 67:
                grade_point = 1.3
            elif avg_percentage >= 65:
                grade_point = 1.0
            else:
                grade_point = 0.0
            
            total_grade_points += grade_point * credit_hours
            total_credits += credit_hours
        
        conn.close()
        
        if total_credits == 0:
            return None
        
        gpa = total_grade_points / total_credits
        return round(gpa, 2)
    
    def update_subject_credits(self, subject_name: str, credit_hours: float):
        """Update credit hours for a subject"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE subjects SET credit_hours = ? WHERE name = ?", (credit_hours, subject_name))
        conn.commit()
        conn.close()
    
    # --- Study Streak ---
    def get_study_streak(self):
        """Calculate current consecutive days with focus sessions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all dates with focus sessions, ordered by date descending
        cursor.execute("""
            SELECT DISTINCT DATE(timestamp) as study_date 
            FROM focus_logs 
            ORDER BY study_date DESC
        """)
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not dates:
            return 0, 0  # current_streak, longest_streak
        
        from datetime import datetime, timedelta
        
        # Calculate current streak
        current_streak = 0
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Check if there's a session today or yesterday
        if dates:
            latest_date = datetime.strptime(dates[0], "%Y-%m-%d").date()
            
            # Only count streak if last session was today or yesterday
            if latest_date == today or latest_date == yesterday:
                current_streak = 1
                expected_date = latest_date - timedelta(days=1)
                
                # Count consecutive days
                for date_str in dates[1:]:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if date_obj == expected_date:
                        current_streak += 1
                        expected_date = date_obj - timedelta(days=1)
                    else:
                        break
        
        # Calculate longest streak
        longest_streak = 0
        if dates:
            temp_streak = 1
            for i in range(len(dates) - 1):
                date1 = datetime.strptime(dates[i], "%Y-%m-%d").date()
                date2 = datetime.strptime(dates[i + 1], "%Y-%m-%d").date()
                
                if (date1 - date2).days == 1:
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    longest_streak = max(longest_streak, temp_streak)
                    temp_streak = 1
            longest_streak = max(longest_streak, temp_streak)
        
        return current_streak, longest_streak
    
    # --- Chart Data ---
    def get_spending_chart_data(self, days=7):
        """Get spending data for chart (last N days)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT DATE(date) as day, SUM(amount) as total 
            FROM finance 
            WHERE date >= date('now', '-{days} days')
            GROUP BY day 
            ORDER BY day
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_grades_chart_data(self):
        """Get grade data for bar chart by subject"""
        return self.get_grade_stats()
    
    def get_focus_chart_data(self, days=7):
        """Get focus session data for chart (last N days)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT DATE(timestamp) as day, SUM(duration) as total_minutes 
            FROM focus_logs 
            WHERE date(timestamp) >= date('now', '-{days} days')
            GROUP BY day 
            ORDER BY day
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    # --- Weekly Report ---
    def generate_weekly_report(self):
        """Generate comprehensive weekly report"""
        from datetime import datetime
        conn = self.get_connection()
        cursor = conn.cursor()
        
        report = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "period": "Last 7 Days"
        }
        
        # Tasks statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending
            FROM tasks 
            WHERE date >= date('now', '-7 days')
        """)
        task_stats = cursor.fetchone()
        report["tasks"] = {
            "total": task_stats[0] or 0,
            "completed": task_stats[1] or 0,
            "pending": task_stats[2] or 0,
            "completion_rate": round((task_stats[1] / task_stats[0] * 100) if task_stats[0] > 0 else 0, 1)
        }
        
        # Focus statistics
        cursor.execute("""
            SELECT COUNT(*), SUM(duration) 
            FROM focus_logs 
            WHERE date(timestamp) >= date('now', '-7 days')
        """)
        focus_stats = cursor.fetchone()
        total_minutes = focus_stats[1] or 0
        report["focus"] = {
            "sessions": focus_stats[0] or 0,
            "total_minutes": total_minutes,
            "hours": total_minutes // 60,
            "daily_average": round(total_minutes / 7, 1)
        }
        
        # Spending statistics
        cursor.execute("""
            SELECT SUM(amount), category 
            FROM finance 
            WHERE date >= date('now', '-7 days')
            GROUP BY category
        """)
        spending_by_category = cursor.fetchall()
        total_spending = sum(row[0] for row in spending_by_category)
        report["spending"] = {
            "total": round(total_spending, 2),
            "by_category": {cat: round(amt, 2) for amt, cat in spending_by_category},
            "daily_average": round(total_spending / 7, 2)
        }
        
        # Assignment statistics
        cursor.execute("""
            SELECT COUNT(*), 
                   SUM(CASE WHEN status = 'graded' THEN 1 ELSE 0 END),
                   AVG(CASE WHEN grade IS NOT NULL THEN grade * 100.0 / max_grade END)
            FROM assignments 
            WHERE created_at >= date('now', '-7 days')
        """)
        assign_stats = cursor.fetchone()
        report["assignments"] = {
            "total": assign_stats[0] or 0,
            "graded": assign_stats[1] or 0,
            "average_grade": round(assign_stats[2], 1) if assign_stats[2] else None
        }
        
        # Current GPA
        gpa = self.calculate_gpa()
        report["gpa"] = gpa
        
        # Study streak
        current_streak, longest_streak = self.get_study_streak()
        report["streak"] = {
            "current": current_streak,
            "longest": longest_streak
        }
        
        conn.close()
        return report

    # --- File Attachments ---
    def add_file_attachment(self, entity_type: str, entity_id: int, file_path: str):
        """Attach a file to an assignment, project, or note"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get existing file paths
        cursor.execute(f"SELECT file_paths FROM {entity_type}s WHERE id = ?", (entity_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            # Parse existing file paths (JSON-like string)
            import json
            try:
                file_paths = json.loads(result[0]) if result[0] else []
            except:
                file_paths = []
        else:
            file_paths = []
        
        # Add new file path
        file_paths.append(file_path)
        
        # Update database
        import json
        cursor.execute(f"UPDATE {entity_type}s SET file_paths = ? WHERE id = ?", 
                      (json.dumps(file_paths), entity_id))
        conn.commit()
        conn.close()
        
        return len(file_paths)
    
    def get_file_attachments(self, entity_type: str, entity_id: int):
        """Get all file attachments for an entity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT file_paths FROM {entity_type}s WHERE id = ?", (entity_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            import json
            try:
                return json.loads(result[0])
            except:
                return []
        return []
    
    def remove_file_attachment(self, entity_type: str, entity_id: int, file_path: str):
        """Remove a file attachment from an entity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get existing file paths
        cursor.execute(f"SELECT file_paths FROM {entity_type}s WHERE id = ?", (entity_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            import json
            try:
                file_paths = json.loads(result[0])
                if file_path in file_paths:
                    file_paths.remove(file_path)
                    cursor.execute(f"UPDATE {entity_type}s SET file_paths = ? WHERE id = ?", 
                                  (json.dumps(file_paths), entity_id))
                    conn.commit()
            except:
                pass
        
        conn.close()

    # --- Custom Categories ---
    def add_custom_category(self, name: str, category_type: str, color: str = "#607D8B"):
        """Add a custom category for expenses or events"""
        conn = self.get_connection()
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute(
            "INSERT INTO categories (name, type, color, is_default, created_at) VALUES (?, ?, ?, 0, ?)",
            (name, category_type, color, created_at)
        )
        category_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return category_id
    
    def get_categories(self, category_type: str = None):
        """Get all categories, optionally filtered by type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if category_type:
            cursor.execute("SELECT id, name, type, color, is_default FROM categories WHERE type = ? ORDER BY is_default DESC, name", (category_type,))
        else:
            cursor.execute("SELECT id, name, type, color, is_default FROM categories ORDER BY type, is_default DESC, name")
        
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def update_custom_category(self, category_id: int, name: str = None, color: str = None):
        """Update a custom category (only non-default categories can be updated)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if category is not default
        cursor.execute("SELECT is_default FROM categories WHERE id = ?", (category_id,))
        result = cursor.fetchone()
        
        if result and result[0] == 0:  # Not a default category
            updates = []
            params = []
            
            if name:
                updates.append("name = ?")
                params.append(name)
            if color:
                updates.append("color = ?")
                params.append(color)
            
            if updates:
                params.append(category_id)
                cursor.execute(f"UPDATE categories SET {', '.join(updates)} WHERE id = ?", params)
                conn.commit()
        
        conn.close()
    
    def delete_custom_category(self, category_id: int):
        """Delete a custom category (only non-default categories can be deleted)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if category is not default
        cursor.execute("SELECT is_default FROM categories WHERE id = ?", (category_id,))
        result = cursor.fetchone()
        
        if result and result[0] == 0:  # Not a default category
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()
        
        conn.close()
    
    def get_category_names(self, category_type: str):
        """Get just the category names for dropdown options"""
        categories = self.get_categories(category_type)
        return [cat[1] for cat in categories]  # Return just the names
    
    # --- Quick Tasks ---
    def add_quick_task(self, task_text: str, priority: str = "Medium", category: str = "General"):
        """Add a new quick task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO quick_tasks (task_text, priority, category, created_at) VALUES (?, ?, ?, ?)",
            (task_text, priority, category, created_at)
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
    
    def get_quick_tasks(self, status=None):
        """Get all quick tasks, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                """SELECT id, task_text, priority, category, status, created_at, completed_at 
                   FROM quick_tasks WHERE status = ? ORDER BY created_at DESC""",
                (status,)
            )
        else:
            cursor.execute(
                """SELECT id, task_text, priority, category, status, created_at, completed_at 
                   FROM quick_tasks ORDER BY status ASC, created_at DESC"""
            )
        
        tasks = cursor.fetchall()
        conn.close()
        return tasks
    
    def update_quick_task_status(self, task_id: int, status: str):
        """Update the status of a quick task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "completed" else None
        cursor.execute(
            "UPDATE quick_tasks SET status = ?, completed_at = ? WHERE id = ?",
            (status, completed_at, task_id)
        )
        conn.commit()
        conn.close()
    
    def delete_quick_task(self, task_id: int):
        """Delete a quick task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quick_tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
    
    def clear_completed_quick_tasks(self):
        """Clear all completed quick tasks and return count of cleared tasks"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get count first
        cursor.execute("SELECT COUNT(*) FROM quick_tasks WHERE status = 'completed'")
        count = cursor.fetchone()[0]
        
        # Delete completed tasks
        cursor.execute("DELETE FROM quick_tasks WHERE status = 'completed'")
        conn.commit()
        conn.close()
        return count
    
    def get_quick_tasks_stats(self):
        """Get quick task statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get counts by status
        cursor.execute("SELECT status, COUNT(*) FROM quick_tasks GROUP BY status")
        stats = dict(cursor.fetchall())
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM quick_tasks")
        total = cursor.fetchone()[0]
        
        conn.close()
        return {
            'pending': stats.get('pending', 0),
            'completed': stats.get('completed', 0),
            'total': total
        }

    def seed_demo_semester(self):
        """Idempotently populate sample BSIT semester records when tables are empty."""
        from datetime import timedelta
        conn = self.get_connection()
        cursor = conn.cursor()
        inserted = 0
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")

        if cursor.execute("SELECT COUNT(*) FROM subjects").fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO subjects (name, code, room, schedule) VALUES (?, ?, ?, ?)",
                [
                    ("Network Security & OSPF", "IT402", "Lab 304", "MWF 09:00-10:30"),
                    ("Software Engineering", "CS308", "Room 201", "TTh 10:00-11:30"),
                    ("Database Systems", "IT301", "Lab 102", "MWF 13:00-14:30"),
                ],
            )
            inserted += 3

        if cursor.execute("SELECT COUNT(*) FROM tasks WHERE date = ?", (today,)).fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO tasks (time_slot, task_name, status, priority, date) VALUES (?, ?, ?, ?, ?)",
                [
                    ("8:00 AM", "Review OSPF Area 0 Lab", "completed", "High", today),
                    ("10:00 AM", "API Contract Test Suite", "completed", "High", today),
                    ("2:00 PM", "SQL Indexing Benchmark", "pending", "Medium", today),
                ],
            )
            inserted += 3

        if cursor.execute("SELECT COUNT(*) FROM finance").fetchone()[0] == 0:
            for offset, amt in [(2, 18.0), (1, 24.5), (0, 21.0)]:
                d = (now - timedelta(days=offset)).strftime("%Y-%m-%d")
                cursor.execute("INSERT INTO finance (item, amount, category, date) VALUES (?, ?, ?, ?)", ("Lab Materials", amt, "Books", d))
            inserted += 3

        if cursor.execute("SELECT COUNT(*) FROM focus_logs WHERE date(timestamp) >= date('now', '-7 days')").fetchone()[0] == 0:
            for offset, mins in [(2, 50), (1, 75), (0, 60)]:
                ts = (now - timedelta(days=offset)).strftime("%Y-%m-%d 14:00:00")
                cursor.execute("INSERT INTO focus_logs (duration, timestamp) VALUES (?, ?)", (mins, ts))
            inserted += 3

        if cursor.execute("SELECT COUNT(*) FROM assignments WHERE status = 'graded'").fetchone()[0] == 0:
            for subj, title, grade in [("IT402", "OSPF & ACL Lab", 96.0), ("CS308", "Sprint 4 Review", 94.5), ("IT301", "SQLite Indexing", 92.0)]:
                cursor.execute(
                    "INSERT INTO assignments (subject, title, description, due_date, grade, max_grade, status, created_at) VALUES (?, ?, ?, ?, ?, 100.0, 'graded', ?)",
                    (subj, title, "Graded coursework", today, grade, today),
                )
            inserted += 3

        conn.commit()
        conn.close()
        return inserted
