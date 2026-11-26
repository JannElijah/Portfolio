/**
 * Full-bleed 16:9 StudentOS Flet Desktop Workspace preview aligned with its
 * actual Academic Slate-Indigo theme and 17-view sidebar layout.
 */
export default function ProjectVisual({ type }) {
  if (type === 'studentos') {
    return (
      <svg
        viewBox="0 0 640 360"
        className="h-full w-full"
        role="img"
        aria-label="StudentOS Academic Slate-Indigo Flet desktop application preview"
      >
        <rect width="640" height="360" fill="#0B1120" />
        {/* Window */}
        <rect x="16" y="14" width="608" height="332" rx="10" fill="#0F172A" stroke="#1E293B" strokeWidth="1.5" />
        <path d="M16 46 H624" stroke="#1E293B" />
        <circle cx="36" cy="30" r="4" fill="#475569" />
        <circle cx="52" cy="30" r="4" fill="#475569" />
        <circle cx="68" cy="30" r="4" fill="#6366F1" />
        <text x="86" y="34" fill="#E2E8F0" fontSize="11" fontFamily="sans-serif" fontWeight="600">
          StudentOS — Academic &amp; Productivity Workspace
        </text>
        <rect x="498" y="21" width="110" height="18" rx="4" fill="rgba(99,102,241,0.18)" />
        <text x="510" y="34" fill="#A5B4FC" fontSize="9.5" fontFamily="sans-serif" fontWeight="600">
          17 Flet Views · SQLite
        </text>

        {/* Left NavigationRail */}
        <rect x="16" y="46" width="112" height="300" fill="#0B1120" />
        <path d="M128 46 V346" stroke="#1E293B" />
        <rect x="26" y="60" width="92" height="24" rx="5" fill="rgba(99,102,241,0.22)" />
        <text x="38" y="76" fill="#C7D2FE" fontSize="10" fontFamily="sans-serif" fontWeight="600">Calendar</text>
        <text x="38" y="102" fill="#94A3B8" fontSize="10" fontFamily="sans-serif">Assignments</text>
        <text x="38" y="128" fill="#94A3B8" fontSize="10" fontFamily="sans-serif">Weekly Grid</text>
        <text x="38" y="154" fill="#94A3B8" fontSize="10" fontFamily="sans-serif">Focus Timer</text>
        <text x="38" y="180" fill="#94A3B8" fontSize="10" fontFamily="sans-serif">Study Stats</text>
        <text x="38" y="206" fill="#94A3B8" fontSize="10" fontFamily="sans-serif">Notes &amp; Goals</text>
        <text x="38" y="232" fill="#94A3B8" fontSize="10" fontFamily="sans-serif">Expense Log</text>
        <text x="38" y="328" fill="#6366F1" fontSize="9" fontFamily="monospace">Ctrl+Space · Ctrl+F</text>

        {/* Left Form Panel */}
        <rect x="142" y="60" width="194" height="272" rx="8" fill="#1E293B" fillOpacity="0.55" stroke="#334155" />
        <text x="156" y="84" fill="#F8FAFC" fontSize="12" fontFamily="sans-serif" fontWeight="600">Schedule &amp; Reminders</text>
        <rect x="156" y="98" width="166" height="26" rx="4" fill="#0F172A" stroke="#334155" />
        <text x="166" y="115" fill="#CBD5E1" fontSize="9.5" fontFamily="sans-serif">Capstone Defense Briefing</text>
        <rect x="156" y="134" width="166" height="26" rx="4" fill="#0F172A" stroke="#334155" />
        <text x="166" y="151" fill="#94A3B8" fontSize="9.5" fontFamily="sans-serif">Repeat: Weekly · 09:00</text>
        <rect x="156" y="170" width="166" height="28" rx="5" fill="#4F46E5" />
        <text x="196" y="188" fill="#FFFFFF" fontSize="10" fontFamily="sans-serif" fontWeight="600">+ Add Event</text>

        <rect x="156" y="214" width="166" height="104" rx="6" fill="#0F172A" stroke="#4F46E5" strokeOpacity="0.5" />
        <text x="166" y="234" fill="#A5B4FC" fontSize="9.5" fontFamily="sans-serif" fontWeight="600">Active Reminder Dialog</text>
        <text x="166" y="256" fill="#E2E8F0" fontSize="9.5" fontFamily="monospace">🔔 2026-12-01 08:00</text>
        <text x="166" y="276" fill="#E2E8F0" fontSize="9.5" fontFamily="monospace">🔔 2026-12-02 18:00</text>
        <text x="166" y="302" fill="#34D399" fontSize="9" fontFamily="sans-serif">60s Background Poll Active</text>

        {/* Right Upcoming Events List */}
        <rect x="350" y="60" width="260" height="272" rx="8" fill="#1E293B" fillOpacity="0.55" stroke="#334155" />
        <text x="364" y="84" fill="#F8FAFC" fontSize="12" fontFamily="sans-serif" fontWeight="600">Upcoming Events</text>

        <rect x="364" y="100" width="232" height="68" rx="6" fill="#0F172A" stroke="#6366F1" />
        <text x="376" y="120" fill="#F8FAFC" fontSize="11" fontFamily="sans-serif" fontWeight="600">Capstone Defense Briefing</text>
        <rect x="536" y="107" width="48" height="16" rx="8" fill="#4F46E5" />
        <text x="545" y="119" fill="#FFFFFF" fontSize="9" fontFamily="sans-serif">🔔 1</text>
        <text x="376" y="138" fill="#94A3B8" fontSize="9.5" fontFamily="sans-serif">Dec 01 · Meeting · Room 402</text>
        <text x="376" y="156" fill="#818CF8" fontSize="9" fontFamily="sans-serif">Manage Reminders · Recurring</text>

        <rect x="364" y="180" width="232" height="68" rx="6" fill="#0F172A" stroke="#334155" />
        <text x="376" y="200" fill="#F8FAFC" fontSize="11" fontFamily="sans-serif" fontWeight="600">IT402 Network Lab Exam</text>
        <text x="376" y="218" fill="#94A3B8" fontSize="9.5" fontFamily="sans-serif">Dec 03 · Exam · Cisco Lab</text>
        <text x="376" y="236" fill="#38BDF8" fontSize="9" fontFamily="sans-serif">Assignment Linked</text>

        <rect x="364" y="260" width="232" height="56" rx="6" fill="#0F172A" stroke="#334155" />
        <text x="376" y="280" fill="#F8FAFC" fontSize="11" fontFamily="sans-serif" fontWeight="600">Daily Focus Target: 120m</text>
        <rect x="376" y="292" width="206" height="8" rx="4" fill="#1E293B" />
        <rect x="376" y="292" width="164" height="8" rx="4" fill="#6366F1" />
      </svg>
    );
  }

  return null;
}
