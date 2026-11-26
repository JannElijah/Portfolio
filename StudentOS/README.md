# StudentOS - Complete Student Command Center

A comprehensive productivity app for students built with Python and Flet.

## 🚀 Features

### Core Modules
- **📊 Dashboard** - Daily time blocking with productivity analytics
- **📚 Academics** - Subject management and class scheduling
- **📝 Assignments** - Track assignments with grades and deadlines
- **📅 Calendar** - Events and deadline tracking with reminders
- **💼 Projects** - Kanban board for project management
- **💰 Finance** - Expense tracking with budget analytics
- **⏱️ Focus** - Pomodoro timer with game blocker
- **📖 Library** - AI-powered PDF reader with Gemini integration
- **📓 Notes** - Notes and flashcards with study mode
- **⚙️ Settings** - Theme toggle, budget limits, and data export

### Advanced Features
- **🔍 Global Search** - Search across all tasks, projects, assignments, events, and notes (Ctrl+F)
- **⚡ Quick Capture** - Instantly add tasks with Ctrl+Space
- **📊 Analytics** - Spending trends, grade tracking, and focus time statistics
- **🎨 Theme Toggle** - Dark/Light mode support
- **📤 Data Export** - Export all data to JSON for backup
- **🤖 AI Integration** - Real Gemini API support for PDF summarization

## 📦 Installation

1. **Clone or download this repository**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up Gemini API (Optional):**
   - Copy `.env.example` to `.env`
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Add your key to `.env`:
     ```
     GEMINI_API_KEY=your_actual_api_key
     ```

## 🎯 Usage

Run the application:
```bash
python main.py
```

### Keyboard Shortcuts
- **Ctrl+Space** - Quick Capture (add tasks instantly)
- **Ctrl+F** - Global Search

## 📁 Project Structure

```
StudentOS/
├── main.py              # Application entry point
├── database.py          # SQLite database manager
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── views/
│   ├── dashboard.py     # Time blocking & analytics
│   ├── academics.py     # Subject management
│   ├── assignments.py   # Assignment tracker
│   ├── calendar_view.py # Events & calendar
│   ├── projects.py      # Kanban board
│   ├── finance.py       # Expense tracking
│   ├── focus.py         # Pomodoro timer & game blocker
│   ├── library.py       # AI PDF reader
│   ├── notes.py         # Notes & flashcards
│   └── settings.py      # App settings & data export
└── student_os_fixed.db  # SQLite database (auto-created)
```

## 🗄️ Database Schema

The app uses SQLite with the following tables:
- `subjects` - Academic subjects and schedules
- `tasks` - Daily time-blocked tasks
- `projects` - Projects with Kanban status
- `finance` - Expense records
- `focus_logs` - Pomodoro session history
- `assignments` - Assignment tracking with grades
- `events` - Calendar events and deadlines
- `notes` - Notes and flashcards
- `settings` - App configuration

## 🎨 Features Breakdown

### Dashboard Analytics
- Task completion tracking
- Daily productivity percentage
- Spending vs budget visualization
- Grade average by subject
- Weekly focus time statistics

### Assignment Tracker
- Submission status tracking
- Grade management
- Overdue highlighting
- Due date reminders

### Calendar & Events
- Event categorization (Exam, Deadline, Class, Meeting, etc.)
- Color-coded event types
- Upcoming/past event filtering
- Location and time tracking

### Notes & Flashcards
- Rich text notes with subjects and tags
- Flashcard creation and management
- Interactive study mode with flip cards
- Randomized card order for effective learning

### AI PDF Reader
- PDF text extraction with PyMuPDF
- Real Gemini API integration for summarization
- Fallback to mock summary if API unavailable
- Word count and reading time estimation

### Settings & Data Management
- Dark/Light theme toggle
- Budget limit configuration
- Pomodoro duration settings
- Full data export to JSON
- Database statistics

## 🛠️ Technologies

- **Frontend:** Flet (Flutter for Python)
- **Database:** SQLite
- **PDF Processing:** PyMuPDF (fitz)
- **Process Management:** psutil
- **AI:** Google Generative AI (Gemini)

## 📝 License

Free to use for educational purposes.

## 🤝 Contributing

Feel free to fork, modify, and enhance! Suggestions and improvements are welcome.

## 🙏 Credits

Built with Python and Flet for students who want to stay organized and productive.

---

**Happy Studying! 🎓**
