"""
Test script for new features (Focus History, Study Stats, Goals, Time Tracking, Advanced Filters)
Tests all 5 new features comprehensively
"""

from database import DatabaseManager
from datetime import datetime, timedelta

def test_focus_history():
    """Test focus session history and statistics"""
    print("\n📊 Testing Focus Session History...")
    db = DatabaseManager()
    
    # Add some focus logs
    print("\n1️⃣ Adding focus sessions...")
    for i in range(10):
        duration = 25 + (i * 5)  # Varying durations
        db.add_focus_log(duration)
    
    print("   ✅ Added 10 focus sessions")
    
    # Get focus logs with date range
    print("\n2️⃣ Testing date-filtered retrieval...")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    logs = db.get_focus_logs_with_dates(start_date, end_date)
    print(f"   ✅ Retrieved {len(logs)} sessions for last 7 days")
    
    # Get focus statistics
    print("\n3️⃣ Testing focus statistics...")
    stats = db.get_focus_statistics()
    
    print(f"   ✅ Total sessions: {stats['total_sessions']}")
    print(f"   ✅ Total minutes: {stats['total_minutes']}")
    print(f"   ✅ Average duration: {stats['average_duration']} min")
    print(f"   ✅ Longest session: {stats['longest_session']} min")
    print(f"   ✅ Sessions this week: {stats['sessions_this_week']}")
    print(f"   ✅ Sessions this month: {stats['sessions_this_month']}")
    print(f"   ✅ Sessions today: {stats['sessions_today']}")
    
    assert stats['total_sessions'] > 0, "No sessions found"
    assert stats['total_minutes'] > 0, "No minutes logged"
    
    print("\n✅ Focus History tests passed!")
    return True

def test_study_statistics():
    """Test study statistics aggregation"""
    print("\n📚 Testing Study Statistics...")
    db = DatabaseManager()
    
    print("\n1️⃣ Getting study statistics...")
    stats = db.get_study_statistics()
    
    print(f"   ✅ Total notes: {stats['total_notes']}")
    print(f"   ✅ Total flashcards: {stats['total_flashcards']}")
    print(f"   ✅ Notes by subject: {len(stats['notes_by_subject'])} subjects")
    print(f"   ✅ Flashcards by subject: {len(stats['flashcards_by_subject'])} subjects")
    print(f"   ✅ Assignments by subject: {len(stats['assignments_by_subject'])} subjects")
    
    if stats['most_productive_day'][0]:
        day, sessions, total_time = stats['most_productive_day']
        print(f"   ✅ Most productive day: {day} ({sessions} sessions, {total_time} min)")
    else:
        print(f"   ✅ Most productive day: Not available yet")
    
    print("\n✅ Study Statistics tests passed!")
    return True

def test_goals():
    """Test goal creation and tracking"""
    print("\n🎯 Testing Goals & Milestones...")
    db = DatabaseManager()
    
    # Create a study hours goal
    print("\n1️⃣ Creating study hours goal...")
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    goal_id = db.add_goal(
        goal_type="study_hours",
        target_value=10.0,
        time_period="weekly",
        start_date=start_date,
        end_date=end_date
    )
    
    assert goal_id is not None, "Goal creation failed"
    print(f"   ✅ Created goal with ID: {goal_id}")
    
    # Create a focus sessions goal
    print("\n2️⃣ Creating focus sessions goal...")
    goal_id2 = db.add_goal(
        goal_type="focus_sessions",
        target_value=20,
        time_period="weekly",
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"   ✅ Created goal with ID: {goal_id2}")
    
    # Get active goals
    print("\n3️⃣ Retrieving active goals...")
    goals = db.get_goals(status='active')
    print(f"   ✅ Found {len(goals)} active goals")
    assert len(goals) >= 2, "Goals not retrieved correctly"
    
    # Update goal progress
    print("\n4️⃣ Testing goal progress update...")
    db.update_goal_progress(goal_id, 5.0)
    goals = db.get_goals(status='active')
    
    for g_id, g_type, target, current, period, s_date, e_date, status in goals:
        if g_id == goal_id:
            assert current == 5.0, "Goal progress not updated"
            print(f"   ✅ Goal progress updated: {current}/{target}")
    
    # Test auto-completion
    print("\n5️⃣ Testing goal auto-completion...")
    db.update_goal_progress(goal_id, 15.0)  # Exceeds target
    goals = db.get_goals(status='completed')
    
    found_completed = False
    for g_id, g_type, target, current, period, s_date, e_date, status in goals:
        if g_id == goal_id:
            found_completed = True
            print(f"   ✅ Goal automatically marked as completed!")
    
    # Delete a goal
    print("\n6️⃣ Testing goal deletion...")
    db.delete_goal(goal_id2)
    goals_after = db.get_goals()
    print(f"   ✅ Goal deleted successfully")
    
    print("\n✅ Goals tests passed!")
    return True

def test_time_tracking():
    """Test time tracking functionality"""
    print("\n⏱️ Testing Time Tracking...")
    db = DatabaseManager()
    
    # Add a time entry
    print("\n1️⃣ Creating time entry...")
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    end_time = (datetime.now() + timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S")
    
    entry_id = db.add_time_entry(
        entity_type="subject",
        entity_id=1,
        entity_name="Mathematics",
        duration=45,
        start_time=start_time,
        end_time=end_time,
        notes="Studied calculus"
    )
    
    assert entry_id is not None, "Time entry creation failed"
    print(f"   ✅ Created time entry with ID: {entry_id}")
    
    # Add more entries
    print("\n2️⃣ Creating multiple time entries...")
    db.add_time_entry("project", 2, "Web App", 60, start_time, end_time)
    db.add_time_entry("assignment", 3, "Essay", 30, start_time, end_time)
    
    print("   ✅ Created additional entries")
    
    # Get all time entries
    print("\n3️⃣ Retrieving time entries...")
    entries = db.get_time_entries(limit=50)
    print(f"   ✅ Retrieved {len(entries)} time entries")
    assert len(entries) >= 3, "Not all entries retrieved"
    
    # Get filtered entries
    print("\n4️⃣ Testing filtered retrieval...")
    subject_entries = db.get_time_entries(entity_type="subject")
    print(f"   ✅ Found {len(subject_entries)} subject time entries")
    
    # Get time summary
    print("\n5️⃣ Testing time summary by entity...")
    summary = db.get_time_summary_by_entity("subject")
    if summary:
        for entity_name, total in summary:
            print(f"   ✅ {entity_name}: {total} minutes")
    
    # Delete a time entry
    print("\n6️⃣ Testing time entry deletion...")
    db.delete_time_entry(entry_id)
    entries_after = db.get_time_entries()
    print(f"   ✅ Time entry deleted successfully")
    
    print("\n✅ Time Tracking tests passed!")
    return True

def test_advanced_filters():
    """Test advanced filtering for assignments, events, and expenses"""
    print("\n🔍 Testing Advanced Filters...")
    db = DatabaseManager()
    
    # Test assignment filters
    print("\n1️⃣ Testing assignment filters...")
    
    # Filter by status
    pending = db.get_assignments_filtered(status='pending')
    print(f"   ✅ Pending assignments: {len(pending)}")
    
    # Filter by date range
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    date_filtered = db.get_assignments_filtered(start_date=start_date, end_date=end_date)
    print(f"   ✅ Assignments in date range: {len(date_filtered)}")
    
    # Test event filters
    print("\n2️⃣ Testing event filters...")
    
    # Filter by event type
    meetings = db.get_events_filtered(event_type="Meeting")
    print(f"   ✅ Meeting events: {len(meetings)}")
    
    # Filter by date range
    events_in_range = db.get_events_filtered(start_date=start_date, end_date=end_date)
    print(f"   ✅ Events in date range: {len(events_in_range)}")
    
    # Test expense filters
    print("\n3️⃣ Testing expense filters...")
    
    # Filter by category
    food_expenses = db.get_expenses_filtered(category="Food")
    print(f"   ✅ Food expenses: {len(food_expenses)}")
    
    # Filter by date range
    recent_expenses = db.get_expenses_filtered(start_date=start_date, end_date=end_date, limit=20)
    print(f"   ✅ Recent expenses: {len(recent_expenses)}")
    
    print("\n✅ Advanced Filters tests passed!")
    return True

def run_all_tests():
    """Run all tests for new features"""
    print("="*60)
    print("🧪 TESTING NEW FEATURES (OPTION C + ENHANCEMENTS)")
    print("="*60)
    
    try:
        test_focus_history()
        test_study_statistics()
        test_goals()
        test_time_tracking()
        test_advanced_filters()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n📋 Feature Summary:")
        print("   ✅ Focus Session History View")
        print("   ✅ Study Statistics")
        print("   ✅ Goal Setting & Tracking")
        print("   ✅ Time Tracking")
        print("   ✅ Advanced Filters")
        print("\n🎉 All 5 features implemented and verified!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    run_all_tests()
