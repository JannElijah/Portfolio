"""Chart generation utilities for StudentOS"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import io
import base64

# Set dark theme for matplotlib
plt.style.use('dark_background')

def create_spending_chart(data, budget=50.0):
    """Create spending trend line chart"""
    if not data:
        return None
    
    # Parse data
    dates = []
    amounts = []
    for date_str, amount in data:
        dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
        amounts.append(amount)
    
    # Fill in missing dates with 0
    if dates:
        start_date = dates[0]
        end_date = dates[-1]
        all_dates = []
        all_amounts = []
        
        current = start_date
        while current <= end_date:
            all_dates.append(current)
            # Find amount for this date
            try:
                idx = dates.index(current)
                all_amounts.append(amounts[idx])
            except ValueError:
                all_amounts.append(0)
            current += timedelta(days=1)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 4), facecolor='#1e1e1e')
        ax.set_facecolor('#1e1e1e')
        
        # Plot line
        ax.plot(all_dates, all_amounts, marker='o', linewidth=2, markersize=6, 
                color='#00d4ff', label='Daily Spending')
        
        # Add budget line
        ax.axhline(y=budget, color='#ff4444', linestyle='--', linewidth=1.5, 
                   label=f'Budget (${budget})')
        
        # Formatting
        ax.set_xlabel('Date', color='#cccccc', fontsize=10)
        ax.set_ylabel('Amount ($)', color='#cccccc', fontsize=10)
        ax.set_title('Spending Trend (Last 7 Days)', color='#ffffff', fontsize=12, pad=10)
        ax.grid(True, alpha=0.2, linestyle='--')
        ax.legend(loc='upper left', fontsize=9)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.xticks(rotation=45, ha='right')
        
        # Tight layout
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, facecolor='#1e1e1e', edgecolor='none')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode()
        plt.close(fig)
        
        return img_base64
    
    return None


def create_grades_chart(data):
    """Create grades bar chart by subject"""
    if not data:
        return None
    
    subjects = [row[0][:10] for row in data]  # Truncate long names
    grades = [row[1] for row in data]
    
    # Color based on grade
    colors = []
    for grade in grades:
        if grade >= 90:
            colors.append('#00ff88')  # Green
        elif grade >= 80:
            colors.append('#00ccff')  # Blue
        elif grade >= 70:
            colors.append('#ffaa00')  # Orange
        else:
            colors.append('#ff4444')  # Red
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 4), facecolor='#1e1e1e')
    ax.set_facecolor('#1e1e1e')
    
    # Create bars
    bars = ax.bar(subjects, grades, color=colors, alpha=0.8, edgecolor='white', linewidth=0.5)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', color='white', fontsize=9)
    
    # Formatting
    ax.set_xlabel('Subject', color='#cccccc', fontsize=10)
    ax.set_ylabel('Grade (%)', color='#cccccc', fontsize=10)
    ax.set_title('Grades by Subject', color='#ffffff', fontsize=12, pad=10)
    ax.set_ylim(0, 105)
    ax.grid(True, axis='y', alpha=0.2, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    
    # Tight layout
    plt.tight_layout()
    
    # Convert to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, facecolor='#1e1e1e', edgecolor='none')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    
    return img_base64


def create_focus_chart(data):
    """Create focus session timeline chart"""
    if not data:
        return None
    
    # Parse data
    dates = []
    minutes = []
    for date_str, total_min in data:
        dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
        minutes.append(total_min)
    
    # Fill in missing dates with 0
    if dates:
        start_date = dates[0]
        end_date = dates[-1]
        all_dates = []
        all_minutes = []
        
        current = start_date
        while current <= end_date:
            all_dates.append(current)
            try:
                idx = dates.index(current)
                all_minutes.append(minutes[idx])
            except ValueError:
                all_minutes.append(0)
            current += timedelta(days=1)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 4), facecolor='#1e1e1e')
        ax.set_facecolor('#1e1e1e')
        
        # Create bars
        bars = ax.bar(all_dates, all_minutes, color='#bb86fc', alpha=0.8, 
                      edgecolor='white', linewidth=0.5)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}m',
                        ha='center', va='bottom', color='white', fontsize=8)
        
        # Formatting
        ax.set_xlabel('Date', color='#cccccc', fontsize=10)
        ax.set_ylabel('Focus Time (minutes)', color='#cccccc', fontsize=10)
        ax.set_title('Focus Sessions (Last 7 Days)', color='#ffffff', fontsize=12, pad=10)
        ax.grid(True, axis='y', alpha=0.2, linestyle='--')
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.xticks(rotation=45, ha='right')
        
        # Tight layout
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, facecolor='#1e1e1e', edgecolor='none')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode()
        plt.close(fig)
        
        return img_base64
    
    return None
