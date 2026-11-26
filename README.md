# Jann Elijah B. Limpiado — Developer & IT Systems OJT Portfolio

Executive dark-theme portfolio built with **React, Vite, and Tailwind CSS** (ready for Vercel deployment), showcasing deployed web platforms, Streamlit/Flet desktop apps, and thirteen `pytest`-verified Python, AI email automation, website maintenance, QA, DevOps, networking, and systems projects in `projects/`.

## Updating Links, Resumes, Headshot & Screenshots
Edit [`src/data/portfolioData.js`](src/data/portfolioData.js):
1. **Dual-Track Resumes:** Drop your two PDFs into `public/resumes/` (`Jann_Limpiado_Software_QA_Resume.pdf` and `Jann_Limpiado_IT_Support_Resume.pdf`) and update `profileData.resumeTracks[].url`.
2. **Optional Profile Photo:** Drop a square headshot at `public/profile.jpg` and set `profileData.avatarUrl` to `"/profile.jpg"`.
3. **Project Links:** Update each project's `links[]` entries (`github.com/JannElijah` is already wired in `profileData.links.github`). Any placeholder starting with `[INSERT_` automatically hides until populated.
4. **Project Screenshots:** Screenshots live in `public/screenshots/` and support click-to-zoom Lightbox previews in the portfolio UI.

## Workspace Engineering Projects (`projects/`)
- [`projects/mailpilot`](projects/mailpilot/README.md) — **MailPilot AI**: AI-Powered Email Automation & IMAPS/SMTP Client Config Validator with Gemini/NLP intent triage and Outbox approval queue (`pytest` verified).
- [`projects/sitecare`](projects/sitecare/README.md) — **SiteCare**: Website Maintenance, SEO/Open Graph Auditor, Broken-Asset Scanner, XML Sitemap Generator & GitHub CI Monitor (`pytest` verified).
- [`projects/qa-pilot`](projects/qa-pilot/README.md) — **QA-Pilot**: Headless Playwright Page Object Model E2E & HTTP API Contract Framework generating dark HTML Sign-Off reports and JUnit XML (`pytest` verified).
- [`projects/edgeops`](projects/edgeops/README.md) — **EdgeOps**: Docker Compose + Nginx Reverse Proxy & Service Health Stack featuring sliding-window rate limiting (`429`), security header audits, `/metrics`, and an SRE Console (`pytest` verified).
- [`projects/waferbench`](projects/waferbench/README.md) — **WaferBench**: Unified Semiconductor Test Floor Web Console integrating `mcu-lab` UART validation and `qa-telemetry` CI release gates (`pytest` verified).
- [`projects/mcu-lab`](projects/mcu-lab/README.md) — Microcontroller Telemetry & Pass-Fail Bench Logger (UART frame parser, spec limits, lot yield % engine, SQLite + CSV export, `pytest` verified).
- [`projects/qa-telemetry`](projects/qa-telemetry/README.md) — Automated Test Verification & Defect Analytics Engine (JUnit XML + JSON bench parser, regression detection, HTML sign-off report, `pytest` verified).
- [`projects/uphsd-dms`](projects/uphsd-dms/README.md) — **UPHSD Document Management System**: REST web portal + SQLite workflow engine with RBAC role approvals and immutable audit log (`pytest` verified).
- [`projects/netaudit`](projects/netaudit/README.md) — **NetAudit**: Cisco IOS Running-Config Security Auditor & CIDR/VLSM Subnet Planner (`pytest` verified).
- [`projects/logpulse`](projects/logpulse/README.md) — **LogPulse**: Windows Event Log (`Get-WinEvent`) & Auto-Start Service Watchdog with SQLite triage history (`pytest` verified).
- [`projects/winops`](projects/winops/README.md) — Windows 11 Provisioning & Asset Audit Toolkit (Winget baseline manifests, CIM hardware/firewall compliance checks, `pytest` verified).
- [`projects/systriage`](projects/systriage/README.md) — Endpoint Health & IT Helpdesk Triage Tool (Windows CIM / procfs, TCP/DNS probing, SQLite foreign-key tickets, `pytest` verified).
- [`projects/authgate`](projects/authgate/README.md) — Role-Based Access & Audit Trail REST API (PBKDF2-SHA256, HS256 JWT rotation, rate limiting, RBAC, immutable SQLite audit trail, `pytest` verified).

## Full Application Folders
- [`StockPilot`](StockPilot/app.py) — Enterprise Inventory & QR Asset Manager (Streamlit + Supabase / SQLite, `pytest` verified).
- [`StormWatchPH`](StormWatchPH/app.py) — PHVS / Open-Meteo Multi-Hazard Monitor (Streamlit + Folium, `pytest` verified).
- [`CryptoSight`](CryptoSight/app.py) — Quantitative Market & Sentiment Terminal (Streamlit + Plotly + yfinance, `pytest` verified).
- [`DevChat`](DevChat/app.py) — Zero-Trust Fernet AES Encrypted Relay (Streamlit + Cryptography + SQLite, `pytest` verified).
- [`StudentOS`](StudentOS/main.py) — 17-View Academic & Productivity Suite (Flet + SQLite, integration-test verified).

## Development & Deployment
```bash
npm install
npm run dev
npm run build
```
