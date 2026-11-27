import fs from 'node:fs';
import path from 'node:path';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import App from '../App';
import {
  additionalProjects,
  credentialsColumns,
  featuredProjects,
  profileData,
} from '../data/portfolioData';

describe('Portfolio data integrity', () => {
  const publicDir = path.resolve(process.cwd(), 'public');

  it('ensures every configured project image exists in public/', () => {
    const allProjects = [...featuredProjects, ...additionalProjects];
    const imagePaths = allProjects.map((p) => p.image).filter(Boolean);
    expect(imagePaths.length).toBeGreaterThanOrEqual(13);

    for (const rel of imagePaths) {
      const fullPath = path.join(publicDir, rel.replace(/^\//, ''));
      expect(fs.existsSync(fullPath), `Missing image asset: ${fullPath}`).toBe(true);
    }
  });

  it('ensures every configured resume PDF and certificate URL exists in public/', () => {
    const resumeUrls = profileData.resumeTracks.map((r) => r.url).filter((u) => u.startsWith('/'));
    expect(resumeUrls).toHaveLength(2);
    for (const rel of resumeUrls) {
      const fullPath = path.join(publicDir, rel.replace(/^\//, ''));
      expect(fs.existsSync(fullPath), `Missing resume asset: ${fullPath}`).toBe(true);
    }

    const certUrls = credentialsColumns
      .flatMap((col) => col.items)
      .map((item) => item.certificateUrl)
      .filter(Boolean);
    expect(certUrls.length).toBeGreaterThanOrEqual(7);

    for (const rel of certUrls) {
      const fullPath = path.join(publicDir, rel.replace(/^\//, ''));
      expect(fs.existsSync(fullPath), `Missing certificate asset: ${fullPath}`).toBe(true);
    }
  });

  it('ensures every configured Portfolio GitHub tree link maps to a local folder', () => {
    const repoPrefix = 'https://github.com/JannElijah/Portfolio/tree/main/';
    const allProjects = [...featuredProjects, ...additionalProjects];
    const repoLinks = allProjects
      .flatMap((p) => p.links || [])
      .map((l) => l.url)
      .filter((u) => typeof u === 'string' && u.startsWith(repoPrefix));

    expect(repoLinks.length).toBeGreaterThanOrEqual(15);

    for (const url of repoLinks) {
      const relPath = url.slice(repoPrefix.length);
      const fullPath = path.join(process.cwd(), relPath);
      expect(fs.existsSync(fullPath), `Missing repo folder for link ${url}: ${fullPath}`).toBe(true);
    }
  });
});

describe('Portfolio UI & interactive workflows', () => {
  it('filters both featured and additional project sections consistently', async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(screen.getByRole('link', { name: 'About' })).toHaveClass('text-white');
    expect(screen.getByText(/CogniCore — Adaptive Cognitive Training Platform/i)).toBeInTheDocument();
    expect(screen.getByText(/UPHSD Document Management System \(DMS\)/i)).toBeInTheDocument();
    expect(screen.getByText(/NetAudit — Cisco IOS Auditor & VLSM Planner/i)).toBeInTheDocument();

    const systemsTab = screen.getByRole('tab', { name: /IT, Security & Validation/i });
    await user.click(systemsTab);

    expect(screen.queryByText(/CogniCore — Adaptive Cognitive Training Platform/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/UPHSD Document Management System \(DMS\)/i)).not.toBeInTheDocument();
    expect(screen.getByText(/WaferBench — MCU Telemetry & QA Validation Suite/i)).toBeInTheDocument();
    expect(screen.getByText(/NetAudit — Cisco IOS Auditor & VLSM Planner/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Show all/i }));
    expect(screen.getByText(/CogniCore — Adaptive Cognitive Training Platform/i)).toBeInTheDocument();
  });

  it('opens the screenshot Lightbox with Next navigation and closes on Escape', async () => {
    const user = userEvent.setup();
    render(<App />);

    const zoomBtn = screen.getByRole('button', {
      name: /Inspect CogniCore — Adaptive Cognitive Training Platform screenshot/i,
    });
    await user.click(zoomBtn);

    const dialog = screen.getByRole('dialog');
    expect(within(dialog).getByText(/CogniCore — Adaptive Cognitive Training Platform/i)).toBeInTheDocument();

    await user.click(within(dialog).getByRole('button', { name: /Next screenshot/i }));
    expect(within(dialog).getByText(/MailPilot AI — Email Triage & Draft Automation/i)).toBeInTheDocument();

    await user.keyboard('{Escape}');
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('opens Architecture Details for secondary projects with CLI run snippet', async () => {
    const user = userEvent.setup();
    render(<App />);

    const additionalSection = document.getElementById('additional-work');
    const netAuditCard = within(additionalSection)
      .getByText(/NetAudit — Cisco IOS Auditor & VLSM Planner/i)
      .closest('article');
    await user.click(within(netAuditCard).getByRole('button', { name: /Details/i }));

    const dialog = screen.getByRole('dialog');
    expect(within(dialog).getByText(/netaudit\.cli audit sample_router\.cfg/i)).toBeInTheDocument();
    await user.keyboard('{Escape}');
  });

  it('runs interactive NetAudit & LogPulse sandboxes and drafts an OJT email inquiry', async () => {
    const user = userEvent.setup();
    render(<App />);

    const additionalSection = document.getElementById('additional-work');
    const logPulseCard = within(additionalSection)
      .getByText(/LogPulse — Windows Event & Service Watchdog/i)
      .closest('article');
    await user.click(within(logPulseCard).getByRole('button', { name: /Live Sandbox/i }));

    const dialog = screen.getByRole('dialog');
    expect(within(dialog).getByText(/STATUS: CRITICAL/i)).toBeInTheDocument();
    await user.click(within(dialog).getByRole('button', { name: /Restart Spooler/i }));
    expect(within(dialog).getByText(/STATUS: HEALTHY/i)).toBeInTheDocument();
    await user.keyboard('{Escape}');

    await user.click(screen.getByRole('button', { name: /Draft OJT Inquiry/i }));
    await user.type(screen.getByPlaceholderText(/Microchip Alabang/i), 'Microchip Technology');
    const mailtoLink = screen.getByRole('link', { name: /Open in Email App/i });
    expect(mailtoLink.getAttribute('href')).toContain('Microchip%20Technology');
  });

  it('runs EdgeOps and QA-Pilot dedicated sandboxes', async () => {
    const user = userEvent.setup();
    render(<App />);

    const additionalSection = document.getElementById('additional-work');
    const edgeCard = within(additionalSection)
      .getByText(/EdgeOps — Nginx Reverse Proxy & Health Stack/i)
      .closest('article');
    await user.click(within(edgeCard).getByRole('button', { name: /Live Sandbox/i }));
    const edgeDialog = screen.getByRole('dialog');
    await user.click(within(edgeDialog).getByRole('button', { name: /Simulate Traffic Burst \(429\)/i }));
    expect(within(edgeDialog).getByText(/429 Throttled:/i).parentElement).toHaveTextContent('3');
    await user.keyboard('{Escape}');

    const qaCard = within(additionalSection)
      .getByText(/QA-Pilot — E2E & API Contract Framework/i)
      .closest('article');
    await user.click(within(qaCard).getByRole('button', { name: /Live Sandbox/i }));
    const qaDialog = screen.getByRole('dialog');
    await user.click(within(qaDialog).getByRole('button', { name: /Run Playwright POM/i }));
    expect(within(qaDialog).getByText(/PASSED \(DOM Verified\)/i)).toBeInTheDocument();
    await user.keyboard('{Escape}');

    const mailCard = screen.getByText(/MailPilot AI — Email Triage/i).closest('article');
    await user.click(within(mailCard).getByRole('button', { name: /Live Sandbox/i }));
    const mailDialog = screen.getByRole('dialog');
    await user.click(within(mailDialog).getByRole('button', { name: /Approve & Send Reply/i }));
    expect(within(mailDialog).getByText(/SENT & LOGGED/i)).toBeInTheDocument();
    await user.keyboard('{Escape}');

    const siteCard = screen.getByText(/SiteCare — Website Maintenance/i).closest('article');
    await user.click(within(siteCard).getByRole('button', { name: /Live Sandbox/i }));
    const siteDialog = screen.getByRole('dialog');
    await user.click(within(siteDialog).getByRole('button', { name: /Scan Staging PR Branch/i }));
    expect(within(siteDialog).getByText(/Missing og:image/i)).toBeInTheDocument();
  });

  it('supports progressive disclosure of featured projects and upgraded Case Study modal actions', async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(screen.queryByText(/CryptoSight — Quantitative Market/i)).not.toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /Show all 10 featured projects/i }));
    expect(screen.getByText(/CryptoSight — Quantitative Market/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Show fewer projects/i })).toBeInTheDocument();

    const mailCard = screen.getByText(/MailPilot AI — Email Triage/i).closest('article');
    await user.click(within(mailCard).getByRole('button', { name: /Project Details/i }));

    const detailsDialog = screen.getByRole('dialog');
    expect(within(detailsDialog).getByText(/Complete Tech Stack/i)).toBeInTheDocument();
    expect(within(detailsDialog).getByText('pytest')).toBeInTheDocument();

    await user.click(within(detailsDialog).getByRole('button', { name: /Launch Live Sandbox/i }));
    const sandboxDialog = screen.getByRole('dialog');
    expect(within(sandboxDialog).getByRole('button', { name: /Approve & Send Reply/i })).toBeInTheDocument();
  });

  it('cross-filters projects from Skills badges and launches projects via Command Palette', async () => {
    const user = userEvent.setup();
    render(<App />);

    const skillsSection = document.getElementById('skills');
    const reactSkillBtn = within(skillsSection).getByRole('button', {
      name: /Filter projects by React\b/i,
    });
    await user.click(reactSkillBtn);

    expect(screen.getByText(/Filtered by skill:/i)).toBeInTheDocument();
    expect(screen.getByText(/CogniCore — Adaptive Cognitive Training Platform/i)).toBeInTheDocument();
    expect(screen.queryByText(/MailPilot AI — Email Triage/i)).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Clear skill filter/i }));
    expect(screen.getByText(/MailPilot AI — Email Triage/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Open quick search/i }));
    const paletteDialog = screen.getByRole('dialog', { name: /Quick command palette/i });
    await user.type(within(paletteDialog).getByPlaceholderText(/Search 18 projects/i), 'WaferBench');

    const projectMatches = within(paletteDialog).getAllByRole('button', {
      name: /WaferBench — MCU Telemetry/i,
    });
    await user.click(projectMatches[projectMatches.length - 1]);

    const detailsDialog = screen.getByRole('dialog');
    expect(within(detailsDialog).getByText(/WaferBench — MCU Telemetry/i)).toBeInTheDocument();
  });
});
