"""Chart generation and productivity analytics utilities for StudentOS."""

import base64
import io
from datetime import datetime, timedelta

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

plt.style.use("dark_background")

_FIG_BG = "#11131a"
_AX_BG = "#161923"


def _style_axis(ax) -> None:
    ax.set_facecolor(_AX_BG)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#2e3447")
    ax.spines["bottom"].set_color("#2e3447")


def _to_base64(fig) -> str:
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=110, facecolor=_FIG_BG, edgecolor="none")
    buf.seek(0)
    payload = base64.b64encode(buf.read()).decode("ascii")
    plt.close(fig)
    return payload


def create_spending_chart(data, budget=50.0):
    """Create spending trend line chart with translucent area fill and mean baseline."""
    if not data:
        return None

    dates = [datetime.strptime(date_str, "%Y-%m-%d") for date_str, _ in data]
    amounts = [float(amount) for _, amount in data]
    if not dates:
        return None

    start_date, end_date = dates[0], dates[-1]
    all_dates, all_amounts = [], []
    current = start_date
    while current <= end_date:
        all_dates.append(current)
        try:
            all_amounts.append(amounts[dates.index(current)])
        except ValueError:
            all_amounts.append(0.0)
        current += timedelta(days=1)

    fig, ax = plt.subplots(figsize=(8, 4), facecolor=_FIG_BG)
    _style_axis(ax)
    ax.plot(all_dates, all_amounts, marker="o", linewidth=2.2, markersize=5, color="#38bdf8", label="Daily Spending")
    ax.fill_between(all_dates, all_amounts, color="#38bdf8", alpha=0.14)
    mean_val = sum(all_amounts) / len(all_amounts)
    ax.axhline(y=mean_val, color="#a78bfa", linestyle=":", linewidth=1.3, label=f"Mean (${mean_val:.2f})")
    ax.axhline(y=budget, color="#f43f5e", linestyle="--", linewidth=1.4, label=f"Budget (${budget:.0f})")

    ax.set_xlabel("Date", color="#cbd5e1", fontsize=10)
    ax.set_ylabel("Amount ($)", color="#cbd5e1", fontsize=10)
    ax.set_title("Spending Trend (Last 7 Days)", color="#ffffff", fontsize=12, fontweight="bold", pad=10)
    ax.grid(True, alpha=0.18, linestyle="--")
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    return _to_base64(fig)


def create_grades_chart(data):
    """Create grades bar chart by subject with 85% Dean's Lister benchmark."""
    if not data:
        return None

    subjects = [row[0][:12] for row in data]
    grades = [float(row[1]) for row in data]
    colors = [
        "#10b981" if g >= 90 else "#38bdf8" if g >= 80 else "#f59e0b" if g >= 70 else "#f43f5e"
        for g in grades
    ]

    fig, ax = plt.subplots(figsize=(8, 4), facecolor=_FIG_BG)
    _style_axis(ax)
    bars = ax.bar(subjects, grades, color=colors, alpha=0.88, edgecolor="#1e2433", linewidth=0.8)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, height + 1.2, f"{height:.1f}%", ha="center", va="bottom", color="#f8fafc", fontsize=9)

    ax.axhline(y=85.0, color="#10b981", linestyle="--", linewidth=1.3, label="Dean's Lister Benchmark (85%)")
    ax.set_xlabel("Subject", color="#cbd5e1", fontsize=10)
    ax.set_ylabel("Grade (%)", color="#cbd5e1", fontsize=10)
    ax.set_title("Grades by Subject", color="#ffffff", fontsize=12, fontweight="bold", pad=10)
    ax.set_ylim(0, 108)
    ax.grid(True, axis="y", alpha=0.18, linestyle="--")
    ax.legend(loc="lower right", fontsize=8.5, frameon=False)
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    return _to_base64(fig)


def create_focus_chart(data):
    """Create focus session timeline chart with 60-minute daily target line."""
    if not data:
        return None

    dates = [datetime.strptime(date_str, "%Y-%m-%d") for date_str, _ in data]
    minutes = [float(total_min) for _, total_min in data]
    if not dates:
        return None

    start_date, end_date = dates[0], dates[-1]
    all_dates, all_minutes = [], []
    current = start_date
    while current <= end_date:
        all_dates.append(current)
        try:
            all_minutes.append(minutes[dates.index(current)])
        except ValueError:
            all_minutes.append(0.0)
        current += timedelta(days=1)

    fig, ax = plt.subplots(figsize=(8, 4), facecolor=_FIG_BG)
    _style_axis(ax)
    bars = ax.bar(all_dates, all_minutes, color="#a78bfa", alpha=0.85, edgecolor="#1e2433", linewidth=0.8)
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width() / 2.0, height + 1.2, f"{int(height)}m", ha="center", va="bottom", color="#f8fafc", fontsize=8.5)

    ax.axhline(y=60.0, color="#10b981", linestyle="--", linewidth=1.3, label="Daily Target (60m)")
    ax.set_xlabel("Date", color="#cbd5e1", fontsize=10)
    ax.set_ylabel("Focus Time (minutes)", color="#cbd5e1", fontsize=10)
    ax.set_title("Focus Sessions (Last 7 Days)", color="#ffffff", fontsize=12, fontweight="bold", pad=10)
    ax.grid(True, axis="y", alpha=0.18, linestyle="--")
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    return _to_base64(fig)


def compute_productivity_score(completed: int, total: int, focus_minutes: int, streak_days: int) -> dict:
    """Compute a 0-100 composite productivity score and tier label."""
    task_ratio = (completed / total) if total > 0 else 0.0
    focus_ratio = min(1.0, max(0.0, focus_minutes / 180.0))
    streak_ratio = min(1.0, max(0.0, streak_days / 7.0))
    score = round((task_ratio * 50.0) + (focus_ratio * 35.0) + (streak_ratio * 15.0))
    if score >= 80:
        tier = "Peak Flow"
    elif score >= 50:
        tier = "On Track"
    else:
        tier = "Building Momentum"
    return {"score": score, "tier": tier}


def export_weekly_markdown(report: dict) -> str:
    """Render a clean Markdown summary from DatabaseManager.generate_weekly_report()."""
    tasks = report.get("tasks", {})
    focus = report.get("focus", {})
    spending = report.get("spending", {})
    streak = report.get("streak", {})
    gpa = report.get("gpa")
    gpa_txt = f"{gpa:.2f} / 4.0" if gpa is not None else "N/A"
    return (
        f"# StudentOS Weekly Report ({report.get('period', 'Current Week')})\n\n"
        f"- **Tasks:** {tasks.get('completed', 0)}/{tasks.get('total', 0)} completed ({tasks.get('completion_rate', 0)}%)\n"
        f"- **Focus Time:** {focus.get('hours', 0)}h {focus.get('total_minutes', 0) % 60}m ({focus.get('sessions', 0)} sessions)\n"
        f"- **Spending:** ${spending.get('total', 0.0):.2f} (Avg ${spending.get('daily_average', 0.0):.2f}/day)\n"
        f"- **GPA / Streak:** {gpa_txt} · {streak.get('current', 0)} days\n"
    )
