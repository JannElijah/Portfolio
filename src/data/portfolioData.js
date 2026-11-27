/**
 * Centralized Portfolio Data Configuration
 * -----------------------------------------------------------------------------
 * Update profile links, dual-track resume URLs, and project assets here.
 */

export const isConfiguredLink = (url) =>
  typeof url === 'string' && url.trim().length > 0 && !url.trim().startsWith('[INSERT_');

const REPO_TREE_BASE = 'https://github.com/JannElijah/Portfolio/tree/main';

export const navItems = [
  { label: 'About', href: '#about' },
  { label: 'Projects', href: '#projects' },
  { label: 'Skills', href: '#skills' },
  { label: 'Credentials', href: '#credentials' },
  { label: 'Contact', href: '#contact' },
];

export const profileData = {
  fullName: 'Jann Elijah B. Limpiado',
  headline: 'Software Developer & IT Systems Intern',
  subheadline:
    "4th-Year BSIT student (1.40 GWA, Dean's Lister) building deployed full-stack web applications, data-driven Python tools, and enterprise Cisco network topologies.",
  location: 'Bacoor, Cavite, Philippines',
  workPreference: 'Available onsite or hybrid in Alabang, Makati & Cavite',
  availability: 'Open for 500-Hour OJT Internship (2027)',
  email: 'jannelijahl@gmail.com',
  phone: '0927-330-7614',
  avatarUrl: '[INSERT_AVATAR_PATH]',
  links: {
    github: 'https://github.com/JannElijah',
    linkedin: 'https://www.linkedin.com/in/jannlimpiado',
  },
  resumeTracks: [
    {
      id: 'software-qa',
      label: 'Software Dev & QA Resume',
      description: 'Full-Stack, Applied AI & QA Engineering',
      suggestedFile: '/resumes/Jann_Limpiado_Software_QA_Resume.pdf',
      url: '/resumes/Jann_Limpiado_Software_QA_Resume.pdf',
    },
    {
      id: 'it-support',
      label: 'IT Support & Systems Resume',
      description: 'Network Ops, Hardware & Systems Admin',
      suggestedFile: '/resumes/Jann_Limpiado_IT_Support_Resume.pdf',
      url: '/resumes/Jann_Limpiado_IT_Support_Resume.pdf',
    },
  ],
  highlights: [
    { label: 'Standing', value: '1.40 GWA', detail: "Dean's Lister · BSIT 4th Year" },
    { label: 'Certified', value: 'ITS · IC3 · TESDA', detail: 'Devices & Systems Servicing' },
    { label: 'English', value: 'TOEIC 850+', detail: 'Professional Working Proficiency' },
    { label: 'Availability', value: '500 Hours', detail: 'Makati, Alabang & Cavite Onsite' },
  ],
};

export const projectFilterTabs = [
  { id: 'all', label: 'All Projects' },
  { id: 'software', label: 'Full-Stack & Data Apps' },
  { id: 'systems', label: 'IT, Security & Validation' },
];

/**
 * Each featured project carries its own authentic domain accent color
 * matching the live theme of its codebase.
 */
export const featuredProjects = [
  {
    id: 'cognicore',
    categories: ['software'],
    accentColor: '#818CF8',
    categoryLabel: 'Capstone · Web & Applied ML',
    title: 'CogniCore — Adaptive Cognitive Training Platform',
    role: 'Project Manager & Lead Developer',
    summary:
      'Deployed full-stack platform combining 14 interactive Phaser 3 cognitive modules with a Python Flask Random Forest API that scales difficulty dynamically from real-time user performance.',
    stack: ['React', 'Vite', 'Flask', 'Scikit-Learn', 'Supabase'],
    image: '/screenshots/cognicore.jpg',
    imageAlt: 'CogniCore adaptive cognitive training platform dashboard',
    details: {
      overview:
        'Built to replace static difficulty curves with real-time Item Response Theory and Random Forest calibration across 14 cognitive modules, hosted on Vercel and Render.',
      highlights: [
        '14 Phaser 3 assessment modules integrated inside a React SPA',
        'Flask inference API evaluating reaction latency & response accuracy',
        'Supabase PostgreSQL telemetry persistence for longitudinal tracking',
      ],
    },
    links: [
      { label: 'Live Demo', url: 'https://cognicore-workspace.vercel.app', kind: 'live' },
      { label: 'GitHub', url: '[INSERT_LINK]', kind: 'github' },
    ],
  },
  {
    id: 'mailpilot',
    categories: ['software'],
    accentColor: '#6366F1',
    categoryLabel: 'AI-Powered Email Automation',
    title: 'MailPilot AI — Email Triage & Draft Automation',
    role: 'Python & AI Developer',
    summary:
      'Python AI workflow authenticating IMAPS/STARTTLS client configs, classifying incoming RFC-822 emails via Gemini / NLP fallback, extracting action items, and queueing drafts to an audited outbox.',
    stack: ['Python', 'Gemini API', 'IMAPS / SMTP', 'SQLite', 'pytest'],
    image: '/screenshots/mailpilot.png',
    imageAlt: 'MailPilot AI inbox priority queue and AI-generated reply draft console screenshot',
    demoId: 'mailpilot',
    folderPath: 'projects/mailpilot',
    details: {
      overview:
        'Combines corporate email client configuration validation (IMAPS 993 / STARTTLS 587) with automated intent classification and human-in-the-loop outbox approval.',
      highlights: [
        'Validates encrypted IMAP/SMTP profiles and parses raw RFC-822 .eml payloads',
        'Classifies emails (Incident/P1, Web Maintenance, Billing, HR/OJT) with confidence scoring',
        'Includes live browser triage & draft-approval sandbox via Live Sandbox button',
      ],
      cliUsage: 'cd projects/mailpilot && python -m mailpilot.server',
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/projects/mailpilot`, kind: 'github' }],
  },
  {
    id: 'sitecare',
    categories: ['software'],
    accentColor: '#10B981',
    categoryLabel: 'Web Maintenance & GitHub CI',
    title: 'SiteCare — Website Maintenance & Release Auditor',
    role: 'Web & DevOps Developer',
    summary:
      'Automated Python site maintenance console scanning production builds for broken local assets, SEO/Open Graph tags, image alt coverage, XML sitemaps, and GitHub Actions workflow status.',
    stack: ['Python', 'HTML5 / SEO', 'GitHub Actions', 'Sitemap XML', 'pytest'],
    image: '/screenshots/sitecare.png',
    imageAlt: 'SiteCare website maintenance audit checks and GitHub workflow status console screenshot',
    demoId: 'sitecare',
    folderPath: 'projects/sitecare',
    details: {
      overview:
        'Built to automate routine website maintenance checks: verifies dist/ & public/ asset integrity, generates standards-compliant sitemap.xml, and surfaces GitHub CI branch status.',
      highlights: [
        'Audits HTML <title>, meta description, og:title/og:image, favicon, and alt compliance',
        'Scans .github/workflows/*.yml CI automation and local Git branch commit history',
        'Includes live site-scan & staging PR failure simulation via Live Sandbox button',
      ],
      cliUsage: 'cd projects/sitecare && python -m sitecare.cli audit --site-dir ../../dist',
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/projects/sitecare`, kind: 'github' }],
  },
  {
    id: 'netguard-network',
    categories: ['systems'],
    accentColor: '#38BDF8',
    categoryLabel: 'Enterprise Networking',
    title: 'Multi-Branch OSPF Network & Cisco CME VoIP',
    role: 'Network & Systems Designer',
    summary:
      'Consolidated multi-site office topologies into dynamic OSPF routing with Cisco CallManager Express (CME) VoIP extension provisioning, paired with a Python reachability diagnostic tool.',
    stack: ['Cisco Packet Tracer', 'OSPF Routing', 'Cisco CME VoIP', 'Python'],
    image: '/screenshots/enterprise-network.jpg',
    imageAlt: 'Multi-branch Cisco OSPF and VoIP network architecture',
    details: {
      overview:
        'Engineered inter-branch packet routing across simulated offices with segmented data/voice VLANs and ISP edge connectivity.',
      highlights: [
        'OSPF Area 0 core connecting HQ and multiple regional branch routers',
        'Cisco CME VoIP dial-peer configuration across branch IP phones',
        'Python NetGuard utility automating ICMP/TCP port health checks',
      ],
    },
    links: [
      { label: 'Architecture', url: '[INSERT_LINK]', kind: 'architecture' },
      { label: 'GitHub', url: '[INSERT_LINK]', kind: 'github' },
    ],
  },
  {
    id: 'stockpilot',
    categories: ['software'],
    accentColor: '#F59E0B',
    categoryLabel: 'Industrial Logistics · Cloud CRUD',
    title: 'StockPilot — Inventory & QR Operations Dashboard',
    role: 'Full-Stack Developer',
    summary:
      'Cloud-backed inventory management dashboard built with Python, Streamlit, Supabase PostgreSQL, and Altair, featuring low-stock threshold alerts, CSV reporting, and per-SKU QR tag generation.',
    stack: ['Python', 'Streamlit', 'Supabase', 'Altair', 'QRCode'],
    image: '/screenshots/stockpilot.png',
    imageAlt: 'StockPilot Inventory Operations Overview screenshot',
    folderPath: 'StockPilot/',
    details: {
      overview:
        'Unifies Supabase PostgreSQL cloud storage with a resilient local SQLite workspace fallback, fixed category editing, low-stock threshold tracking, and printable SKU QR tags.',
      highlights: [
        'Executive KPI overview with Altair stock quantity & category valuation charts',
        'Full CRUD inventory workflow with safe error handling and CSV export',
        'Instant QR tag generation and PNG download per product SKU',
      ],
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/StockPilot`, kind: 'github' }],
  },
  {
    id: 'stormwatch',
    categories: ['software'],
    accentColor: '#14B8A6',
    categoryLabel: 'Geospatial Radar Ops',
    title: 'StormWatch PH — Seismic & Weather Ops Center',
    role: 'Data & Python Developer',
    summary:
      'Real-time Philippine disaster monitoring dashboard ingesting concurrent USGS earthquake feeds and Open-Meteo city telemetry onto dark geospatial Folium maps with PAGASA heat-index risk tiers.',
    stack: ['Python', 'Streamlit', 'Folium', 'Open-Meteo API', 'USGS GeoJSON'],
    image: '/screenshots/stormwatch.png',
    imageAlt: 'StormWatch PH Geospatial Radar Map and telemetry screenshot',
    folderPath: 'StormWatchPH/',
    details: {
      overview:
        'Aggregates live seismic events inside the Philippine Area of Responsibility alongside concurrent city weather telemetry, tectonic boundaries, and 24-hour magnitude timelines.',
      highlights: [
        'Concurrent Open-Meteo city ingestion with PAGASA heat-index classification',
        'Interactive Folium dark-gray archipelago map with magnitude markers & city overlays',
        'Graceful offline telemetry fallback and CSV weather matrix export',
      ],
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/StormWatchPH`, kind: 'github' }],
  },
  {
    id: 'cryptosight',
    categories: ['software'],
    accentColor: '#EAB308',
    categoryLabel: 'Quant Finance Terminal',
    title: 'CryptoSight — Quantitative Market & Sentiment Terminal',
    role: 'Python & Analytics Developer',
    summary:
      'Quantitative crypto dashboard plotting OHLCV candlesticks, 20-day SMA, volume, and 14-day RSI alongside SQLite portfolio valuation and Gemini / momentum-based market sentiment.',
    stack: ['Python', 'Streamlit', 'Plotly', 'yfinance', 'SQLite'],
    image: '/screenshots/cryptosight.png',
    imageAlt: 'CryptoSight BTC-USD market terminal and candlestick RSI chart screenshot',
    folderPath: 'CryptoSight/',
    details: {
      overview:
        'Combines live yfinance market feeds, relative multi-asset indexing, persistent SQLite holdings tracking, and resilient AI/quantitative headline sentiment.',
      highlights: [
        '3-row Plotly terminal chart: Candlestick + SMA 20, Volume, and RSI (14D)',
        'Supports nested & flat yfinance news schemas with Gemini 2.0 / RSI fallback',
        'Persistent SQLite portfolio tracker with allocation chart and CSV export',
      ],
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/CryptoSight`, kind: 'github' }],
  },
  {
    id: 'devchat',
    categories: ['systems'],
    accentColor: '#10B981',
    categoryLabel: 'Zero-Trust Security',
    title: 'DevChat — Encrypted Channel Relay',
    role: 'Security & Python Developer',
    summary:
      'End-to-end encrypted messaging relay deriving channel-isolated Fernet AES-128-CBC keys from 480k-iteration PBKDF2-SHA256 passphrases with key fingerprint verification and SQLite ciphertext storage.',
    stack: ['Python', 'Cryptography (Fernet)', 'PBKDF2-SHA256', 'SQLite', 'Streamlit'],
    image: '/screenshots/devchat.png',
    imageAlt: 'DevChat encrypted channel relay screenshot',
    folderPath: 'DevChat/',
    details: {
      overview:
        'Demonstrates symmetric encryption, per-channel PBKDF2 salt isolation, XSS-safe message rendering, and live ciphertext audit inspection.',
      highlights: [
        '480,000-iteration PBKDF2-SHA256 key derivation with room fingerprint verification',
        'Custom channel creation, per-channel clear, and XSS-escaped HTML message bubbles',
        'Audit mode exposing raw Fernet ciphertext in SQLite alongside decrypted export',
      ],
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/DevChat`, kind: 'github' }],
  },
  {
    id: 'studentos',
    categories: ['software'],
    accentColor: '#6366F1',
    categoryLabel: 'Desktop Productivity OS',
    title: 'StudentOS — Modular Academic & Task Desktop App',
    role: 'Solo Developer',
    summary:
      'Cross-platform desktop productivity suite in Python, Flet, and SQLite featuring 17 integrated workspaces—including recurring calendar events, weekly schedule grid, focus timer, and reminder dialogs.',
    stack: ['Python', 'Flet', 'SQLite', 'Desktop Notifications'],
    image: '/screenshots/studentos.png',
    imageAlt: 'StudentOS modular academic and analytics dashboard screenshot',
    folderPath: 'StudentOS/',
    details: {
      overview:
        'Completed with recurring event generation (daily/weekly/monthly), interactive reminder dialogs on Calendar & Assignments views, global Ctrl+F search, and Ctrl+Space quick capture.',
      highlights: [
        '17 modular Flet views sharing a normalized SQLite relational database',
        'Interactive reminder management dialogs integrated in Calendar & Assignments',
        'Verified with automated scheduling and reminder integration tests',
      ],
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/StudentOS`, kind: 'github' }],
  },
  {
    id: 'mcu-lab',
    categories: ['systems'],
    accentColor: '#2DD4BF',
    categoryLabel: 'Hardware & QA Validation',
    title: 'WaferBench — MCU Telemetry & QA Validation Suite',
    role: 'QA & Automation Developer',
    summary:
      'Python + SQLite semiconductor validation dashboard combining live PIC32MX UART voltage/thermal telemetry logging with JUnit XML CI/CD release gates, flaky-test detection, and regression analysis.',
    stack: ['Python', 'SQLite', 'UART Telemetry', 'JUnit XML', 'pytest'],
    image: '/screenshots/waferbench.png',
    imageAlt: 'WaferBench live semiconductor UART telemetry and CI release gate dashboard screenshot',
    demoId: 'mcu-lab',
    folderPath: 'projects/waferbench',
    details: {
      overview:
        'Unifies microcontroller hardware bench telemetry (projects/mcu-lab) and automated CI/CD JUnit verification (projects/qa-telemetry) into one REST web console (projects/waferbench), verified with pytest.',
      highlights: [
        'UART frame parser validating VDD_3V3, VCC_5V, temperature, and current draw across wafer lots',
        'JUnit XML & JSON ingestor tracking yield %, p50/p95 latency, and deterministic CI release gates',
        'Includes live HTTP web console + interactive browser sandbox via Live Sandbox button',
      ],
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/projects/waferbench`, kind: 'github' }],
  },
];

export const additionalProjects = [
  {
    id: 'systriage',
    categories: ['systems'],
    accentColor: '#38BDF8',
    category: 'IT Support & Workstation Automation',
    title: 'SysTriage & WinOps — Provisioning & Triage',
    folderPath: 'projects/winops & systriage',
    stack: ['PowerShell', 'Windows CIM', 'Winget', 'Python', 'SQLite'],
    demoId: 'systriage',
    summary:
      'Automates Windows 11 Winget software baselines, hardware serial/firewall audits, DNS/TCP health checks, and P1–P3 SLA ticket persistence.',
    details: {
      overview:
        'Combines declarative Winget workstation provisioning and Windows CIM hardware/firewall audits (projects/winops) with live endpoint CPU/RAM/TCP telemetry and SLA ticket tracking (projects/systriage).',
      highlights: [
        'Exports compliance baselines to JSON, CSV, and printable HTML workstation sign-off reports',
        'Foreign-key linked SQLite incident database enforcing P1–P3 SLA state transitions',
        'Verified by 11 combined automated pytest cases (winops + systriage)',
      ],
      cliUsage: 'cd projects/systriage && python -m systriage.cli scan --export report.json',
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/projects/systriage`, kind: 'github' }],
  },
  {
    id: 'uphsd-dms',
    categories: ['software'],
    accentColor: '#E11D48',
    category: 'Full-Stack Workflow & UI/UX',
    title: 'UPHSD Document Management System (DMS)',
    folderPath: 'projects/uphsd-dms',
    stack: ['Python HTTP API', 'SQLite RBAC', 'Audit Trail', 'Figma (11 Frames)'],
    image: '/screenshots/uphsd-dms.png',
    imageAlt: 'UPHSD Document Management System live workflow queue screenshot',
    summary:
      'Live web document routing portal and 11-frame Figma prototype enforcing Student vs. Dean/Registrar RBAC approvals, state transitions, and immutable audit trails.',
    details: {
      overview:
        'Digitizes institutional campus routing across SUBMITTED, IN_REVIEW, APPROVED, and RETURNED stages with role-gated actions and append-only audit logs.',
      highlights: [
        'Interactive HTML web queue backed by Python ThreadingHTTPServer REST API',
        'Role check preventing unauthorized self-approval while recording every reviewer note',
        'Matches the 11-frame UPHSD DMS Figma blueprint with end-to-end pytest coverage',
      ],
      cliUsage: 'cd projects/uphsd-dms && python -m dms.server',
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/projects/uphsd-dms`, kind: 'github' }],
  },
  {
    id: 'netaudit',
    categories: ['systems'],
    accentColor: '#38BDF8',
    category: 'Network Automation & CCNA/OSPF',
    title: 'NetAudit — Cisco IOS Auditor & VLSM Planner',
    folderPath: 'projects/netaudit',
    stack: ['Python', 'ipaddress', 'Cisco IOS CLI', 'VLSM', 'pytest'],
    demoId: 'netaudit',
    summary:
      'Parses Cisco IOS running-configs to audit SSHv2, Telnet exposure, password encryption, VLANs, and OSPF networks alongside a deterministic CIDR/VLSM subnet allocator.',
    details: {
      overview:
        'Built for CCNA/enterprise network operations to catch insecure VTY Telnet rules, missing enable secrets, and subnet allocation conflicts before rollout.',
      highlights: [
        'Parses interfaces, VLAN database blocks, OSPF router areas, and line VTY transport rules',
        'Deterministic VLSM subnet planner sorting host demands to prevent CIDR overlaps',
        'CLI JSON report output and 4 automated pytest cases',
      ],
      cliUsage: 'cd projects/netaudit && python -m netaudit.cli audit sample_router.cfg',
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/projects/netaudit`, kind: 'github' }],
  },
  {
    id: 'logpulse',
    categories: ['systems'],
    accentColor: '#F59E0B',
    category: 'IT Operations & Systems Triage',
    title: 'LogPulse — Windows Event & Service Watchdog',
    folderPath: 'projects/logpulse',
    stack: ['Python', 'PowerShell (Get-WinEvent)', 'Win32_Service CIM', 'SQLite'],
    demoId: 'logpulse',
    summary:
      'Collects Windows System/Application error events and stopped Auto-start services, ranking top Event IDs and computing HEALTHY/WARN/CRITICAL snapshots.',
    details: {
      overview:
        'Automates L1/L2 Windows workstation incident triage by correlating stopped Auto-start services with recurring System/Application critical event IDs.',
      highlights: [
        'Native PowerShell Get-WinEvent & Get-CimInstance Win32_Service integration',
        'Escalates recurring Event ID spikes (WARN) and stopped critical services (CRITICAL)',
        'Stores snapshot time-series in SQLite with CLI query & pytest verification',
      ],
      cliUsage: 'cd projects/logpulse && python -m logpulse.cli scan --save-db',
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/projects/logpulse`, kind: 'github' }],
  },
  {
    id: 'authgate',
    categories: ['systems'],
    accentColor: '#10B981',
    category: 'Identity & Security Microservice',
    title: 'AuthGate — RBAC Identity & Audit API',
    folderPath: 'projects/authgate',
    stack: ['Python', 'PBKDF2-SHA256', 'HS256 JWT', 'SQLite', 'RBAC'],
    demoId: 'authgate',
    summary:
      'Zero-dependency REST authentication service featuring salted PBKDF2 password hashing, JWT rotation, rate limiting, role permissions, and append-only audit logging.',
    details: {
      overview:
        'Implements production security fundamentals in standard-library Python without framework black boxes: cryptographic password hashing, token rotation, brute-force throttling, and strict role guards.',
      highlights: [
        'Salted PBKDF2-SHA256 credential hashing and HMAC-SHA256 JWT verification',
        'Sliding-window login rate limiter blocking credential-stuffing attempts',
        'Append-only SQLite audit log recording allow/deny RBAC decisions',
      ],
      cliUsage: 'cd projects/authgate && python -m pytest -v',
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/projects/authgate`, kind: 'github' }],
  },
  {
    id: 'qa-pilot',
    categories: ['software'],
    accentColor: '#F59E0B',
    category: 'QA Automation & Playwright E2E',
    title: 'QA-Pilot — E2E & API Contract Framework',
    folderPath: 'projects/qa-pilot',
    stack: ['Python', 'Playwright POM', 'pytest', 'API Contracts', 'HTML Report'],
    image: '/screenshots/qa-pilot.png',
    imageAlt: 'QA-Pilot dark HTML QA Sign-Off report from automated Playwright E2E and API Contract tests',
    demoId: 'qa-pilot',
    summary:
      'Executes headless Chromium Page Object Model workflows and HTTP JSON schema/latency contracts against UPHSD-DMS, generating dark HTML sign-off reports and JUnit XML.',
    details: {
      overview:
        'Provides deterministic Playwright E2E workflows (using expect_response synchronization instead of fragile sleeps) and schema/latency SLA validation exported into JUnit XML + HTML dashboards.',
      highlights: [
        'Page Object Model (DmsPage) verifying Kanban document review & RBAC role rejection',
        'Validates API response HTTP status codes, JSON types, and sub-250ms latency SLOs',
        'Converts pytest --junitxml output into HTML sign-off reports ingested by QA-Telemetry',
      ],
      cliUsage: 'cd projects/qa-pilot && python -m pytest -v --junitxml=junit.xml',
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/projects/qa-pilot`, kind: 'github' }],
  },
  {
    id: 'edgeops',
    categories: ['systems'],
    accentColor: '#8B5CF6',
    category: 'Backend, Cloud & Nginx DevOps',
    title: 'EdgeOps — Nginx Reverse Proxy & Health Stack',
    folderPath: 'projects/edgeops',
    stack: ['Docker Compose', 'Nginx 1.27', 'Python Gateway', 'Rate Limit (429)', 'SRE Metrics'],
    image: '/screenshots/edgeops.png',
    imageAlt: 'EdgeOps Nginx reverse proxy and upstream health monitoring web console screenshot',
    demoId: 'edgeops',
    summary:
      'Containerized Docker Compose + Nginx reverse proxy paired with a Python HTTP gateway enforcing rate limiting, security headers, upstream probes, and Prometheus /metrics.',
    details: {
      overview:
        'Combines production Dockerfile/docker-compose.yml and hardened Nginx config (limit_req_zone, SAMEORIGIN/nosniff headers, /healthz) with a runnable Python SRE proxy gateway.',
      highlights: [
        'Nginx config auditor parsing upstreams, security headers, and rate-limit zones',
        'Sliding-window rate limiter returning 429 Too Many Requests + /proxy/<service> routing',
        'Live upstream health probes (UP/DOWN) with p50/p95 latency tracking & /metrics',
      ],
      cliUsage: 'cd projects/edgeops && python -m edgeops.gateway',
    },
    links: [{ label: 'GitHub', url: `${REPO_TREE_BASE}/projects/edgeops`, kind: 'github' }],
  },
  {
    id: 'unity-games',
    categories: ['software'],
    accentColor: '#A78BFA',
    category: 'Unity 6 LTS · C# & Multiplayer',
    title: 'Pawmart Co-Op, Lumen 3D & Surge Block (Android)',
    folderPath: 'Unity C# Portfolio',
    stack: ['Unity 6 LTS', 'C#', 'Netcode for GameObjects', 'Shader Graph', 'Blender'],
    summary:
      'Built a 2-player networked retail simulation in Netcode for GameObjects alongside modular C# gameplay state machines, custom Shader Graph pipelines, and Android frame profiling.',
    details: {
      overview:
        'Led architecture and C# engineering across three Unity projects spanning synchronized multiplayer state, stylized Shader Graph lighting, and mobile performance optimization.',
      highlights: [
        'Pawmart: 2-player Netcode for GameObjects item pickup/checkout synchronization + Blender Rigify characters',
        'Lumen: 3D platformer controller state machine and custom URP Shader Graph materials',
        'Surge Block: Android puzzle-RPG touch input loop profiled for steady mobile frame pacing',
      ],
    },
  },
];

export const skillColumns = [
  {
    id: 'software',
    title: 'Software & Data Engineering',
    groups: [
      {
        label: 'Languages',
        items: ['Python', 'JavaScript', 'C#', 'SQL', 'PowerShell', 'HTML5 / CSS3', 'Java'],
      },
      {
        label: 'Frameworks & Libraries',
        items: ['React', 'Vite', 'Flask', 'Streamlit', 'Flet', 'Scikit-Learn', 'Gemini API', 'Phaser 3', 'Plotly'],
      },
      {
        label: 'Web Ops, DB & GitHub',
        items: ['PostgreSQL (Supabase)', 'SQLite', 'Git / GitHub Actions', 'SEO & Sitemaps', 'Docker / Nginx', 'Vercel', 'Render'],
      },
    ],
  },
  {
    id: 'systems',
    title: 'IT Systems, Networking & QA',
    groups: [
      {
        label: 'Systems, Email & Security',
        items: [
          'Windows 11 Administration',
          'Email Clients (IMAPS / SMTP)',
          'Device Configuration & Management',
          'Winget & CIM Provisioning',
          'Fernet / PBKDF2 / RBAC',
        ],
      },
      {
        label: 'Networking',
        items: ['Cisco Packet Tracer', 'Multi-Branch OSPF Routing', 'Cisco CME VoIP Telephony'],
      },
      {
        label: 'QA & Design',
        items: ['Playwright E2E', 'Automated Testing (pytest / Vitest)', 'Technical Documentation', 'Figma Prototyping', 'Unity 6 LTS'],
      },
    ],
  },
];

export const credentialsColumns = [
  {
    id: 'certification',
    title: 'Certifications',
    items: [
      {
        heading: 'Certiport ITS — Devices Configuration & Management',
        meta: 'Certiport · 2026',
      },
      {
        heading: 'IC3 Digital Literacy Certification (GS6 Level 1)',
        meta: 'Certiport / Pearson VUE · May 2024 · ID: vzE6-uTdJ',
        certificateUrl: '/certificates/IC3_GS6_Level_1.pdf',
      },
      {
        heading: 'TESDA — Installing & Configuring Computer Systems',
        meta: 'eTESDA · Aug 2023 · Code: bEpkc2xTGj',
        certificateUrl: '/certificates/TESDA_Installing_Configuring_Computer_Systems.pdf',
      },
      {
        heading: 'TESDA — Introduction to Computer Systems Servicing',
        meta: 'eTESDA · Jun 2023 · Code: 540OUkGH78',
        certificateUrl: '/certificates/TESDA_Intro_CSS.pdf',
      },
      {
        heading: 'Modern AI Training Program',
        meta: 'DICT Calabarzon / Cisco NetAcad · 2026',
      },
      {
        heading: 'Python Certification Course',
        meta: 'Programming Hub · Aug 2023 · ID: 1691238692580',
        certificateUrl: '/certificates/Programming_Hub_Python.jpg',
      },
      {
        heading: 'Learn CSS — Web Styling',
        meta: 'Udemy · Feb 2024 · ID: UC-a9754d74',
        certificateUrl: '/certificates/Udemy_Learn_CSS.pdf',
      },
    ],
  },
  {
    id: 'communication',
    title: 'Communication & Seminars',
    items: [
      {
        heading: 'TOEIC Score 850+ / 1000',
        meta: 'Professional Working Proficiency',
        detail:
          'Verified workplace English proficiency for technical documentation, team coordination, and client support.',
      },
      {
        heading: 'Onsite Seminar: Data Mining',
        meta: 'UPHSD Molino · Jun 2024',
        certificateUrl: '/certificates/Seminar_Data_Mining.pdf',
      },
      {
        heading: 'Research & AI Integrated Technologies',
        meta: 'UPHSD Molino · Nov 2024',
        certificateUrl: '/certificates/Webinar_Research_AI.pdf',
      },
    ],
  },
  {
    id: 'academic',
    title: 'Education & Leadership',
    items: [
      {
        heading: 'BS in Information Technology (4th Year)',
        meta: 'UPHSD – Molino Campus · 2023–Present',
        detail: "1.40 GWA · Dean's Lister (1st Sem SY 2025–2026) · Capstone Passed (CogniCore).",
      },
      {
        heading: 'Senior High School — ICT Strand',
        meta: 'Arellano University — Juan Sumulong Campus · 2020–2023',
        detail: 'Information & Communications Technology foundational track.',
      },
      {
        heading: 'Technical Lead, Game Dev Committee',
        meta: 'UPHSD E.L.I.T.E. Program · Team Torvalds & JPCS',
        detail: 'Led technical architecture and collaborative developer initiatives.',
      },
    ],
  },
];
