"""Test script to verify charts generation"""
import sys
import traceback

try:
    from database import DatabaseManager
    from charts import create_spending_chart, create_grades_chart, create_focus_chart
    from datetime import datetime, timedelta

    db = DatabaseManager()

    print("Testing chart generation...")

    # Test spending chart
    print("\n1. Testing spending chart...")
    try:
        spending_data = db.get_spending_chart_data(days=7)
        print(f"   Spending data points: {len(spending_data)}")
        spending_chart = create_spending_chart(spending_data, 50.0)
        if spending_chart:
            print("   ✓ Spending chart generated successfully")
        else:
            print("   ⚠ No spending data available")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        traceback.print_exc()

    # Test grades chart
    print("\n2. Testing grades chart...")
    try:
        grades_data = db.get_grades_chart_data()
        print(f"   Grade data points: {len(grades_data)}")
        grades_chart = create_grades_chart(grades_data)
        if grades_chart:
            print("   ✓ Grades chart generated successfully")
        else:
            print("   ⚠ No grades data available")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        traceback.print_exc()

    # Test focus chart
    print("\n3. Testing focus chart...")
    try:
        focus_data = db.get_focus_chart_data(days=7)
        print(f"   Focus data points: {len(focus_data)}")
        focus_chart = create_focus_chart(focus_data)
        if focus_chart:
            print("   ✓ Focus chart generated successfully")
        else:
            print("   ⚠ No focus data available")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        traceback.print_exc()

    # Test streak calculation
    print("\n4. Testing streak counter...")
    try:
        current_streak, longest_streak = db.get_study_streak()
        print(f"   Current streak: {current_streak} days")
        print(f"   Longest streak: {longest_streak} days")
        print("   ✓ Streak calculation working")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        traceback.print_exc()

    # Test weekly report
    print("\n5. Testing weekly report generation...")
    try:
        report = db.generate_weekly_report()
        print(f"   Report generated for: {report['period']}")
        print(f"   Tasks completed: {report['tasks']['completed']}/{report['tasks']['total']}")
        print(f"   Focus sessions: {report['focus']['sessions']}")
        print(f"   Total spending: ${report['spending']['total']:.2f}")
        print(f"   Current GPA: {report['gpa'] if report['gpa'] else 'N/A'}")
        print(f"   Study streak: {report['streak']['current']} days")
        print("   ✓ Weekly report generated successfully")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        traceback.print_exc()

    print("\n✅ All tests completed!")
    
except Exception as e:
    print(f"\n❌ Fatal error: {e}")
    traceback.print_exc()
    sys.exit(1)

