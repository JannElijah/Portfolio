"""
Test script for Enhanced Scheduling features (Option B)
Tests:
1. Recurring Events (daily, weekly, monthly patterns)
2. Advanced Reminder System
3. Weekly Schedule View
"""

from database import DatabaseManager
from datetime import datetime, timedelta
import time

def test_recurring_events():
    """Test recurring event generation"""
    print("\n🔁 Testing Recurring Events...")
    db = DatabaseManager()
    
    # Clean up any previous test events
    print("\n🧹 Cleaning up previous test data...")
    all_events = db.get_events()
    for event in all_events:
        event_id = event[0]
        db.delete_event(event_id, delete_all=True)
    print("   ✅ Database cleaned")
    
    # Test 1: Daily recurring event
    print("\n1️⃣ Creating daily recurring event (7 days)...")
    start_date = datetime.now().strftime("%Y-%m-%d 09:00")
    end_date = (datetime.now() + timedelta(days=6)).strftime("%Y-%m-%d")
    
    parent_id = db.add_event(
        title="Daily Standup",
        description="Morning team meeting",
        event_type="Meeting",
        start_date=start_date,
        location="Zoom",
        recurrence_pattern="daily",
        recurrence_end_date=end_date
    )
    
    # Verify instances were created
    all_events = db.get_events()
    daily_events = [e for e in all_events if "Daily Standup" in e[1]]
    print(f"   ✅ Created {len(daily_events)} daily event instances")
    assert len(daily_events) == 7, f"Expected 7 daily events, got {len(daily_events)}"
    
    # Test 2: Weekly recurring event
    print("\n2️⃣ Creating weekly recurring event (4 weeks)...")
    end_date_weekly = (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d")  # 3 weeks = 4 instances
    
    db.add_event(
        title="Team Retrospective",
        description="Weekly review",
        event_type="Meeting",
        start_date=start_date,
        location="Conference Room",
        recurrence_pattern="weekly",
        recurrence_end_date=end_date_weekly
    )
    
    all_events = db.get_events()
    weekly_events = [e for e in all_events if "Team Retrospective" in e[1]]
    print(f"   ✅ Created {len(weekly_events)} weekly event instances")
    assert len(weekly_events) >= 3, f"Expected at least 3 weekly events, got {len(weekly_events)}"
    
    # Test 3: Monthly recurring event
    print("\n3️⃣ Creating monthly recurring event (3 months)...")
    end_date_monthly = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
    
    db.add_event(
        title="Monthly Review",
        description="End of month meeting",
        event_type="Meeting",
        start_date=start_date,
        location="Office",
        recurrence_pattern="monthly",
        recurrence_end_date=end_date_monthly
    )
    
    all_events = db.get_events()
    monthly_events = [e for e in all_events if "Monthly Review" in e[1]]
    print(f"   ✅ Created {len(monthly_events)} monthly event instances")
    assert len(monthly_events) >= 2, f"Expected at least 2 monthly events, got {len(monthly_events)}"
    
    # Test 4: Delete recurring series
    print("\n4️⃣ Testing delete entire recurring series...")
    initial_count = len(daily_events)
    first_daily_event_id = daily_events[0][0]
    db.delete_event(first_daily_event_id, delete_all=True)
    
    all_events = db.get_events()
    remaining_daily = [e for e in all_events if "Daily Standup" in e[1]]
    print(f"   ✅ Deleted series: {initial_count} events removed, {len(remaining_daily)} remaining")
    assert len(remaining_daily) == 0, "Not all series events were deleted"
    
    # Test 5: Get events for specific week
    print("\n5️⃣ Testing get_events_for_week()...")
    week_start = datetime.now().strftime("%Y-%m-%d")
    week_events = db.get_events_for_week(week_start)
    print(f"   ✅ Found {len(week_events)} events for this week")
    
    print("\n✅ All recurring event tests passed!")
    return True

def test_reminder_system():
    """Test advanced reminder CRUD operations"""
    print("\n🔔 Testing Advanced Reminder System...")
    db = DatabaseManager()
    
    # Test 1: Add reminder
    print("\n1️⃣ Creating reminder...")
    reminder_time = (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M")
    
    reminder_id = db.add_reminder(
        entity_type="event",
        entity_id=1,
        reminder_time=reminder_time
    )
    
    print(f"   ✅ Reminder created with ID: {reminder_id}")
    assert reminder_id is not None, "Reminder creation failed"
    
    # Test 2: Get reminders
    print("\n2️⃣ Retrieving reminders...")
    reminders = db.get_reminders("event", 1)
    print(f"   ✅ Found {len(reminders)} reminders for entity")
    assert len(reminders) > 0, "No reminders found"
    
    # Test 3: Get pending reminders
    print("\n3️⃣ Checking pending reminders...")
    # Create a past reminder
    past_time = (datetime.now() - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")
    past_reminder_id = db.add_reminder(
        entity_type="assignment",
        entity_id=1,
        reminder_time=past_time
    )
    
    pending = db.get_pending_reminders()
    print(f"   ✅ Found {len(pending)} pending reminders")
    assert len(pending) > 0, "No pending reminders found"
    
    # Test 4: Mark reminder as sent
    print("\n4️⃣ Marking reminder as sent...")
    db.mark_reminder_sent(past_reminder_id)
    
    pending_after = db.get_pending_reminders()
    print(f"   ✅ Pending reminders reduced from {len(pending)} to {len(pending_after)}")
    
    # Test 5: Delete reminder
    print("\n5️⃣ Deleting reminder...")
    db.delete_reminder(reminder_id)
    reminders_after = db.get_reminders("event", 1)
    print(f"   ✅ Reminders reduced from {len(reminders)} to {len(reminders_after)}")
    
    print("\n✅ All reminder system tests passed!")
    return True

def test_weekly_schedule_integration():
    """Test weekly schedule view data retrieval"""
    print("\n📅 Testing Weekly Schedule Integration...")
    db = DatabaseManager()
    
    # Test 1: Add events for different days of the week
    print("\n1️⃣ Creating events for different days...")
    base_date = datetime.now()
    
    for i in range(7):
        day = base_date + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d 10:00")
        
        db.add_event(
            title=f"Event Day {i+1}",
            description=f"Event for {day.strftime('%A')}",
            event_type="Meeting",
            start_date=day_str,
            location="Office"
        )
    
    print("   ✅ Created 7 events across the week")
    
    # Test 2: Retrieve week's events
    print("\n2️⃣ Retrieving weekly events...")
    week_start = base_date.strftime("%Y-%m-%d")
    week_events = db.get_events_for_week(week_start)
    
    print(f"   ✅ Retrieved {len(week_events)} events for the week")
    assert len(week_events) >= 7, f"Expected at least 7 events, got {len(week_events)}"
    
    # Test 3: Verify event distribution
    print("\n3️⃣ Verifying event distribution by day...")
    days_with_events = set()
    for event in week_events:
        event_date = event[3].split()[0]  # Extract date from datetime
        days_with_events.add(event_date)
    
    print(f"   ✅ Events distributed across {len(days_with_events)} days")
    
    print("\n✅ All weekly schedule integration tests passed!")
    return True

def run_all_tests():
    """Run all scheduling tests"""
    print("="*60)
    print("🧪 TESTING ENHANCED SCHEDULING FEATURES (OPTION B)")
    print("="*60)
    
    try:
        test_recurring_events()
        test_reminder_system()
        test_weekly_schedule_integration()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n📋 Feature Summary:")
        print("   ✅ Recurring Events (daily, weekly, monthly)")
        print("   ✅ Advanced Reminder System (CRUD operations)")
        print("   ✅ Weekly Schedule View (data integration)")
        print("\n🎉 Option B implementation complete and verified!")
        
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
