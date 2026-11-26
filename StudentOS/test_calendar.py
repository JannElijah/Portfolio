"""Test specifically the calendar view functionality"""
from database import DatabaseManager

print("Testing Calendar View")
print("=" * 30)

# Initialize database
db = DatabaseManager()

# Test get_events method
print("1. Testing get_events()...")
try:
    events = db.get_events()
    print(f"   [OK] Retrieved {len(events)} events")
    if events:
        event = events[0]
        print(f"   [INFO] First event has {len(event)} fields: {event}")
    
except Exception as e:
    print(f"   [FAIL] get_events error: {e}")
    import traceback
    traceback.print_exc()

# Test CalendarView initialization
print("\n2. Testing CalendarView initialization...")
try:
    from views.calendar_view import CalendarView
    calendar_view = CalendarView(db)
    print("   [OK] CalendarView initialized")
    
    # Test load_events
    print("\n3. Testing load_events()...")
    calendar_view.load_events()
    print("   [OK] load_events completed")
    
except Exception as e:
    print(f"   [FAIL] CalendarView error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 30)
print("Calendar test completed")