import { useEffect, useState } from 'react';
import {
  X,
  Play,
  Download,
  ShieldAlert,
  ShieldCheck,
  Terminal,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
} from 'lucide-react';

function WinOpsDemo() {
  const [profile, setProfile] = useState('developer');
  const [auditRun, setAuditRun] = useState(null);

  const packagesByProfile = {
    standard: ['Google.Chrome', '7zip.7zip'],
    it_support: ['Google.Chrome', '7zip.7zip', 'Notepad++.Notepad++'],
    developer: [
      'Google.Chrome',
      '7zip.7zip',
      'Notepad++.Notepad++',
      'Git.Git',
      'Python.Python.3.12',
      'Microsoft.VisualStudioCode',
    ],
  };

  const scriptText = [
    `# WinOps Baseline Provisioning Script (Profile: ${profile})`,
    "$ErrorActionPreference = 'Stop'",
    '$packages = @(',
    ...packagesByProfile[profile].map((pkg) => `    '${pkg}'`),
    ')',
    'foreach ($pkgId in $packages) {',
    '    winget install --id $pkgId --exact --silent --accept-package-agreements',
    '}',
  ].join('\n');

  const runAudit = (simulateIssue = false) => {
    const freePct = simulateIssue ? 11.4 : 42.8;
    const fwEnabled = !simulateIssue;
    const serial = simulateIssue ? 'Unknown' : 'PF4X9012-W11';
    const checks = [
      { check: 'Minimum 15% Free Disk Capacity', passed: freePct >= 15, observed: `${freePct}% free` },
      {
        check: 'Windows Firewall Profiles Enabled',
        passed: fwEnabled,
        observed: fwEnabled ? 'Domain:ON, Private:ON, Public:ON' : 'Public:OFF',
      },
      { check: 'Hardware Asset Serial Recorded', passed: serial !== 'Unknown', observed: serial },
    ];
    setAuditRun({
      hostname: 'LAB-ENG-WS04',
      os: 'Microsoft Windows 11 Pro (Build 22631)',
      compliant: checks.every((c) => c.passed),
      checks,
    });
  };

  const downloadPs1 = () => {
    const blob = new Blob([scriptText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `winops_${profile}.ps1`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4 text-xs">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1.5">
          {['standard', 'it_support', 'developer'].map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => setProfile(p)}
              className={`rounded-md px-2.5 py-1 font-mono uppercase transition-colors ${
                profile === p
                  ? 'bg-sky-400 font-semibold text-slate-950'
                  : 'border border-slate-700 bg-slate-900 text-slate-300 hover:border-slate-500'
              }`}
            >
              {p}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => runAudit(false)}
            className="inline-flex items-center gap-1.5 rounded-md bg-emerald-500/20 px-3 py-1.5 font-semibold text-emerald-300 border border-emerald-500/40 hover:bg-emerald-500/30"
          >
            <Play className="h-3.5 w-3.5" />
            Run Healthy Audit
          </button>
          <button
            type="button"
            onClick={() => runAudit(true)}
            className="inline-flex items-center gap-1.5 rounded-md bg-amber-500/15 px-3 py-1.5 font-semibold text-amber-300 border border-amber-500/40 hover:bg-amber-500/25"
          >
            <AlertTriangle className="h-3.5 w-3.5" />
            Simulate Non-Compliant
          </button>
          <button
            type="button"
            onClick={downloadPs1}
            className="inline-flex items-center gap-1.5 rounded-md border border-sky-400/40 bg-sky-400/10 px-3 py-1.5 font-semibold text-sky-300 hover:bg-sky-400/20"
          >
            <Download className="h-3.5 w-3.5" />
            Download .ps1
          </button>
        </div>
      </div>

      <pre className="overflow-x-auto rounded-lg border border-slate-800 bg-[#070B14] p-3 font-mono text-[11px] leading-relaxed text-sky-200">
        {scriptText}
      </pre>

      {auditRun && (
        <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-3.5">
          <div className="flex items-center justify-between">
            <span className="font-mono text-slate-300">
              {auditRun.hostname} · {auditRun.os}
            </span>
            <span
              className={`rounded px-2 py-0.5 font-mono font-semibold ${
                auditRun.compliant
                  ? 'bg-emerald-500/20 text-emerald-300'
                  : 'bg-rose-500/20 text-rose-300'
              }`}
            >
              {auditRun.compliant ? 'COMPLIANT' : 'NON-COMPLIANT'}
            </span>
          </div>
          <div className="mt-2.5 space-y-1.5">
            {auditRun.checks.map((c) => (
              <div
                key={c.check}
                className="flex items-center justify-between rounded border border-slate-800 bg-[#0B1120] px-3 py-1.5"
              >
                <span className="text-slate-200">{c.check}</span>
                <span className={c.passed ? 'font-mono text-emerald-400' : 'font-mono text-rose-400'}>
                  {c.passed ? 'PASS' : 'FAIL'} ({c.observed})
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function McuLabDemo() {
  const presets = [
    {
      label: 'Nominal Unit',
      frame: 'DEV=PIC32MX-001,FW=2.1.0,VDD_3V3=3.31,VCC_5V=5.02,MCU_TEMP_C=41.5,I_DRAW_MA=38.2',
    },
    {
      label: 'Voltage Brownout',
      frame: 'DEV=PIC32MX-002,FW=2.1.0,VDD_3V3=2.92,VCC_5V=4.98,MCU_TEMP_C=44.0,I_DRAW_MA=39.1',
    },
    {
      label: 'Thermal + Current Spike',
      frame: 'DEV=PIC32MX-003,FW=2.1.0,VDD_3V3=3.29,VCC_5V=5.04,MCU_TEMP_C=91.4,I_DRAW_MA=142.8',
    },
  ];

  const [rawFrame, setRawFrame] = useState(presets[0].frame);
  const [lotLog, setLotLog] = useState([]);

  const specs = {
    VDD_3V3: { min: 3.15, max: 3.45, unit: 'V' },
    VCC_5V: { min: 4.75, max: 5.25, unit: 'V' },
    MCU_TEMP_C: { min: -10, max: 85, unit: '°C' },
    I_DRAW_MA: { min: 5, max: 120, unit: 'mA' },
  };

  const evaluateFrame = (frameStr) => {
    const pairs = {};
    frameStr.split(',').forEach((part) => {
      const [k, v] = part.split('=');
      if (k && v) pairs[k.trim()] = v.trim();
    });
    const faults = [];
    Object.entries(specs).forEach(([ch, limit]) => {
      const val = parseFloat(pairs[ch]);
      if (Number.isNaN(val) || val < limit.min || val > limit.max) {
        faults.push(`${ch}=${pairs[ch] ?? 'N/A'} (${limit.min}..${limit.max}${limit.unit})`);
      }
    });
    return {
      dev: pairs.DEV || 'UNKNOWN',
      metrics: pairs,
      verdict: faults.length === 0 ? 'PASS' : 'FAIL',
      faults,
    };
  };

  const currentEval = evaluateFrame(rawFrame);

  const recordToLot = () => {
    setLotLog((prev) => [currentEval, ...prev].slice(0, 6));
  };

  const passCount = lotLog.filter((item) => item.verdict === 'PASS').length;
  const yieldPct = lotLog.length ? ((passCount / lotLog.length) * 100).toFixed(1) : '100.0';

  return (
    <div className="space-y-4 text-xs">
      <div className="flex flex-wrap items-center gap-2">
        {presets.map((p) => (
          <button
            key={p.label}
            type="button"
            onClick={() => setRawFrame(p.frame)}
            className="rounded-md border border-slate-700 bg-slate-900 px-2.5 py-1 font-medium text-slate-200 hover:border-sky-400/50"
          >
            Load: {p.label}
          </button>
        ))}
        <button
          type="button"
          onClick={recordToLot}
          className="ml-auto inline-flex items-center gap-1.5 rounded-md bg-sky-400 px-3 py-1.5 font-semibold text-slate-950 hover:bg-sky-300"
        >
          <Play className="h-3.5 w-3.5" />
          Log Frame to Lot
        </button>
      </div>

      <div>
        <label className="mb-1 block font-mono text-[10px] uppercase tracking-wider text-slate-400">
          UART Telemetry Packet
        </label>
        <input
          type="text"
          value={rawFrame}
          onChange={(e) => setRawFrame(e.target.value)}
          className="w-full rounded-lg border border-slate-700 bg-[#070B14] px-3 py-2 font-mono text-[11px] text-sky-300 focus:border-sky-400 focus:outline-none"
        />
      </div>

      <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-4">
        {Object.entries(specs).map(([ch, limit]) => {
          const val = parseFloat(currentEval.metrics[ch]);
          const ok = !Number.isNaN(val) && val >= limit.min && val <= limit.max;
          return (
            <div
              key={ch}
              className={`rounded-lg border p-2.5 ${
                ok
                  ? 'border-slate-800 bg-slate-900/80'
                  : 'border-rose-500/50 bg-rose-500/10'
              }`}
            >
              <p className="font-mono text-[10px] text-slate-400">{ch}</p>
              <p className={`mt-1 font-mono text-sm font-semibold ${ok ? 'text-white' : 'text-rose-300'}`}>
                {currentEval.metrics[ch] ?? '--'} {limit.unit}
              </p>
              <p className="mt-0.5 text-[10px] text-slate-500">
                Spec: {limit.min}–{limit.max}
              </p>
            </div>
          );
        })}
      </div>

      <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-[#070B14] px-3.5 py-2.5">
        <span className="font-mono text-slate-300">
          Frame Verdict:{' '}
          <strong className={currentEval.verdict === 'PASS' ? 'text-emerald-400' : 'text-rose-400'}>
            {currentEval.verdict}
          </strong>
        </span>
        <span className="font-mono text-slate-400">
          Lot Yield: <strong className="text-sky-300">{yieldPct}%</strong> ({passCount}/{lotLog.length || 0} logged)
        </span>
      </div>
    </div>
  );
}

function AuthGateDemo() {
  const [role, setRole] = useState('STAFF');
  const [attempts, setAttempts] = useState(0);
  const [logs, setLogs] = useState([
    { actor: 'admin1', action: 'LOGIN', resource: '/api/auth/login', outcome: '200_OK' },
  ]);

  const callEndpoint = (endpoint) => {
    let outcome = '200_OK';
    if (endpoint === '/api/audit-logs' && role !== 'ADMIN') {
      outcome = '403_FORBIDDEN';
    } else if (endpoint === '/api/auth/login-fail') {
      const next = attempts + 1;
      setAttempts(next);
      outcome = next > 4 ? '429_RATE_LIMITED' : '401_INVALID_CREDS';
    }

    setLogs((prev) => [
      {
        actor: role.toLowerCase(),
        action: endpoint === '/api/auth/login-fail' ? 'LOGIN_ATTEMPT' : 'GET_RESOURCE',
        resource: endpoint,
        outcome,
      },
      ...prev.slice(0, 5),
    ]);
  };

  return (
    <div className="space-y-4 text-xs">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1.5">
          <span className="font-mono text-slate-400">Active JWT Role:</span>
          {['STAFF', 'TECHNICIAN', 'ADMIN'].map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => setRole(r)}
              className={`rounded px-2.5 py-1 font-mono font-semibold ${
                role === r
                  ? 'bg-sky-400 text-slate-950'
                  : 'border border-slate-700 bg-slate-900 text-slate-300'
              }`}
            >
              {r}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={() => setAttempts(0)}
          className="inline-flex items-center gap-1 text-slate-400 hover:text-white"
        >
          <RotateCcw className="h-3 w-3" />
          Reset Rate Limiter ({attempts}/4)
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => callEndpoint('/api/me')}
          className="rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 font-mono text-slate-200 hover:border-sky-400/50"
        >
          GET /api/me
        </button>
        <button
          type="button"
          onClick={() => callEndpoint('/api/audit-logs')}
          className="rounded-md border border-sky-400/40 bg-sky-400/10 px-3 py-1.5 font-mono text-sky-300 hover:bg-sky-400/20"
        >
          GET /api/audit-logs (ADMIN)
        </button>
        <button
          type="button"
          onClick={() => callEndpoint('/api/auth/login-fail')}
          className="rounded-md border border-amber-500/40 bg-amber-500/10 px-3 py-1.5 font-mono text-amber-300 hover:bg-amber-500/20"
        >
          Test Failed Login ({attempts}/4)
        </button>
      </div>

      <div className="space-y-1.5 rounded-lg border border-slate-800 bg-[#070B14] p-3 font-mono text-[11px]">
        <p className="text-[10px] uppercase tracking-wider text-slate-500">
          Immutable SQLite Audit Stream
        </p>
        {logs.map((entry, idx) => (
          <div key={`${entry.resource}-${idx}`} className="flex items-center justify-between border-b border-slate-800/70 py-1 last:border-0">
            <span className="text-slate-300">
              [{entry.actor}] {entry.action} → {entry.resource}
            </span>
            <span
              className={
                entry.outcome.startsWith('200')
                  ? 'text-emerald-400'
                  : entry.outcome.startsWith('403')
                    ? 'text-amber-400'
                    : 'text-rose-400'
              }
            >
              {entry.outcome}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function SysTriageDemo() {
  const [tickets, setTickets] = useState([
    { id: 1, title: 'DNS latency spike on Floor-2 Switch', priority: 'P2', status: 'OPEN' },
  ]);
  const [lastScan, setLastScan] = useState(null);

  const runScan = (warnMode) => {
    const status = warnMode ? 'WARN' : 'HEALTHY';
    setLastScan({
      host: 'CONCENTRIX-POD-14',
      diskUsed: warnMode ? '84.6%' : '46.2%',
      ramUsed: warnMode ? '87.1%' : '54.0%',
      dnsLatency: warnMode ? '142.4 ms' : '11.8 ms',
      status,
    });
    if (warnMode) {
      setTickets((prev) => [
        {
          id: prev.length + 1,
          title: 'Automated alert: CONCENTRIX-POD-14 status WARN',
          priority: 'P2',
          status: 'OPEN',
        },
        ...prev,
      ]);
    }
  };

  const resolveTicket = (id) => {
    setTickets((prev) =>
      prev.map((t) => (t.id === id ? { ...t, status: 'RESOLVED' } : t))
    );
  };

  return (
    <div className="space-y-4 text-xs">
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => runScan(false)}
          className="inline-flex items-center gap-1.5 rounded-md border border-emerald-500/40 bg-emerald-500/15 px-3 py-1.5 font-semibold text-emerald-300 hover:bg-emerald-500/25"
        >
          <ShieldCheck className="h-3.5 w-3.5" />
          Scan Healthy Endpoint
        </button>
        <button
          type="button"
          onClick={() => runScan(true)}
          className="inline-flex items-center gap-1.5 rounded-md border border-amber-500/40 bg-amber-500/15 px-3 py-1.5 font-semibold text-amber-300 hover:bg-amber-500/25"
        >
          <ShieldAlert className="h-3.5 w-3.5" />
          Scan High-Load + Auto-Ticket
        </button>
      </div>

      {lastScan && (
        <div className="grid grid-cols-2 gap-2 rounded-lg border border-slate-800 bg-[#070B14] p-3 font-mono sm:grid-cols-4">
          <div>
            <span className="text-[10px] text-slate-500">HOST</span>
            <p className="text-slate-200">{lastScan.host}</p>
          </div>
          <div>
            <span className="text-[10px] text-slate-500">DISK</span>
            <p className="text-slate-200">{lastScan.diskUsed}</p>
          </div>
          <div>
            <span className="text-[10px] text-slate-500">RAM</span>
            <p className="text-slate-200">{lastScan.ramUsed}</p>
          </div>
          <div>
            <span className="text-[10px] text-slate-500">DNS PROBE</span>
            <p className={lastScan.status === 'WARN' ? 'text-amber-400' : 'text-emerald-400'}>
              {lastScan.dnsLatency} ({lastScan.status})
            </p>
          </div>
        </div>
      )}

      <div className="space-y-1.5">
        {tickets.map((t) => (
          <div
            key={t.id}
            className="flex items-center justify-between gap-2 rounded-lg border border-slate-800 bg-slate-900/70 px-3 py-2"
          >
            <div>
              <span className="mr-2 rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[10px] text-sky-300">
                #{t.id} · {t.priority}
              </span>
              <span className="text-slate-200">{t.title}</span>
            </div>
            {t.status === 'OPEN' ? (
              <button
                type="button"
                onClick={() => resolveTicket(t.id)}
                className="rounded border border-emerald-500/40 bg-emerald-500/15 px-2.5 py-1 font-mono text-[10px] text-emerald-300 hover:bg-emerald-500/25"
              >
                Resolve
              </button>
            ) : (
              <span className="font-mono text-[10px] text-emerald-400">RESOLVED</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function QaTelemetryDemo() {
  const [selectedRun, setSelectedRun] = useState('b2');
  const [minPassRate, setMinPassRate] = useState(95);

  const runs = {
    b1: {
      suite: 'api-regression',
      build: 'build-101',
      total: 4,
      passed: 4,
      failed: 0,
      p95: '0.19s',
      regressions: [],
    },
    b2: {
      suite: 'api-regression',
      build: 'build-102',
      total: 4,
      passed: 3,
      failed: 1,
      p95: '0.28s',
      regressions: ['tests.test_auth::test_token_refresh'],
    },
  };

  const run = runs[selectedRun];
  const passRate = Math.round((run.passed / run.total) * 1000) / 10;
  const verdict = passRate >= minPassRate && run.failed === 0 ? 'PASS' : 'BLOCKED';

  return (
    <div className="space-y-4 text-xs">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setSelectedRun('b1')}
            className={`rounded-md px-3 py-1.5 font-mono font-semibold ${
              selectedRun === 'b1'
                ? 'bg-sky-400 text-slate-950'
                : 'border border-slate-700 bg-slate-900 text-slate-300'
            }`}
          >
            Run #101 (Clean)
          </button>
          <button
            type="button"
            onClick={() => setSelectedRun('b2')}
            className={`rounded-md px-3 py-1.5 font-mono font-semibold ${
              selectedRun === 'b2'
                ? 'bg-sky-400 text-slate-950'
                : 'border border-slate-700 bg-slate-900 text-slate-300'
            }`}
          >
            Run #102 (Regression)
          </button>
        </div>

        <label className="flex items-center gap-2 font-mono text-slate-300">
          <span>Gate Threshold: {minPassRate}%</span>
          <input
            type="range"
            min="70"
            max="100"
            value={minPassRate}
            onChange={(e) => setMinPassRate(Number(e.target.value))}
            className="accent-sky-400"
          />
        </label>
      </div>

      <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-4">
        <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-3">
          <p className="font-mono text-[10px] text-slate-400">YIELD / PASS RATE</p>
          <p className="mt-1 font-mono text-lg font-bold text-white">{passRate}%</p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-3">
          <p className="font-mono text-[10px] text-slate-400">FAILURES</p>
          <p className={`mt-1 font-mono text-lg font-bold ${run.failed ? 'text-rose-400' : 'text-emerald-400'}`}>
            {run.failed}
          </p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-3">
          <p className="font-mono text-[10px] text-slate-400">P95 DURATION</p>
          <p className="mt-1 font-mono text-lg font-bold text-white">{run.p95}</p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-3">
          <p className="font-mono text-[10px] text-slate-400">RELEASE GATE</p>
          <p className={`mt-1 font-mono text-lg font-bold ${verdict === 'PASS' ? 'text-emerald-400' : 'text-rose-400'}`}>
            {verdict}
          </p>
        </div>
      </div>

      {run.regressions.length > 0 ? (
        <div className="rounded-lg border border-rose-500/40 bg-rose-500/10 px-3.5 py-2.5 font-mono text-rose-200">
          Regression Detected vs Baseline: {run.regressions.join(', ')}
        </div>
      ) : (
        <div className="flex items-center gap-2 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3.5 py-2.5 font-mono text-emerald-300">
          <CheckCircle2 className="h-4 w-4" />
          <span>Zero regressions detected · Ready for release sign-off.</span>
        </div>
      )}
    </div>
  );
}

function NetAuditDemo() {
  const [preset, setPreset] = useState('insecure');
  const [cidrInput, setCidrInput] = useState('192.168.10.0/26');

  const configs = {
    secure: {
      hostname: 'CORE-SW-ALABANG',
      checks: [
        { rule: 'SSHv2 VTY Transport Only', passed: true, detail: 'transport input ssh (no Telnet)' },
        { rule: 'Service Password-Encryption', passed: true, detail: 'Enabled' },
        { rule: 'Enable Secret (Type 5/8/9)', passed: true, detail: 'Configured' },
      ],
      vlans: ['VLAN 10 · STAFF_LAN', 'VLAN 20 · VOIP_VOICE', 'VLAN 99 · MGMT'],
    },
    insecure: {
      hostname: 'EDGE-RTR-LEGACY',
      checks: [
        { rule: 'SSHv2 VTY Transport Only', passed: false, detail: 'Telnet allowed on line vty 0 4' },
        { rule: 'Service Password-Encryption', passed: false, detail: 'Disabled (plaintext risk)' },
        { rule: 'Enable Secret (Type 5/8/9)', passed: false, detail: 'Missing enable secret' },
      ],
      vlans: ['VLAN 1 · DEFAULT'],
    },
  };

  const subnets = {
    '192.168.10.0/24': { mask: '255.255.255.0', range: '192.168.10.1 – 192.168.10.254', hosts: 254 },
    '192.168.10.0/26': { mask: '255.255.255.192', range: '192.168.10.1 – 192.168.10.62', hosts: 62 },
    '192.168.10.64/27': { mask: '255.255.255.224', range: '192.168.10.65 – 192.168.10.94', hosts: 30 },
    '192.168.10.96/28': { mask: '255.255.255.240', range: '192.168.10.97 – 192.168.10.110', hosts: 14 },
  };

  const activeCfg = configs[preset];
  const sub = subnets[cidrInput];

  return (
    <div className="space-y-4 text-xs">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setPreset('insecure')}
            className={`rounded-md px-3 py-1.5 font-mono font-semibold ${
              preset === 'insecure'
                ? 'bg-sky-400 text-slate-950'
                : 'border border-slate-700 bg-slate-900 text-slate-300'
            }`}
          >
            Audit Legacy Config
          </button>
          <button
            type="button"
            onClick={() => setPreset('secure')}
            className={`rounded-md px-3 py-1.5 font-mono font-semibold ${
              preset === 'secure'
                ? 'bg-sky-400 text-slate-950'
                : 'border border-slate-700 bg-slate-900 text-slate-300'
            }`}
          >
            Audit Hardened Config
          </button>
        </div>

        <span className="font-mono text-slate-400">Device: {activeCfg.hostname}</span>
      </div>

      <div className="space-y-2 rounded-lg border border-slate-800 bg-[#070B14] p-3">
        {activeCfg.checks.map((c) => (
          <div key={c.rule} className="flex items-center justify-between gap-2">
            <span className="flex items-center gap-2 text-slate-200">
              {c.passed ? (
                <ShieldCheck className="h-4 w-4 text-emerald-400" />
              ) : (
                <ShieldAlert className="h-4 w-4 text-rose-400" />
              )}
              {c.rule}
            </span>
            <span className={`font-mono ${c.passed ? 'text-emerald-400' : 'text-rose-400'}`}>
              {c.detail}
            </span>
          </div>
        ))}
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span className="font-mono text-[11px] text-slate-400">VLSM SUBNET VERIFIER</span>
          <select
            value={cidrInput}
            onChange={(e) => setCidrInput(e.target.value)}
            aria-label="Select CIDR block"
            className="rounded border border-slate-700 bg-[#070B14] px-2 py-1 font-mono text-sky-300"
          >
            {Object.keys(subnets).map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
        </div>
        <div className="mt-2.5 grid grid-cols-3 gap-2 font-mono text-[11px]">
          <div>
            <span className="text-slate-500">MASK:</span>{' '}
            <span className="text-slate-200">{sub.mask}</span>
          </div>
          <div>
            <span className="text-slate-500">USABLE:</span>{' '}
            <span className="text-sky-300">{sub.range}</span>
          </div>
          <div>
            <span className="text-slate-500">HOSTS:</span>{' '}
            <span className="text-emerald-400">{sub.hosts}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function LogPulseDemo() {
  const [scenario, setScenario] = useState('critical');
  const [spoolerRestarted, setSpoolerRestarted] = useState(false);

  const isCritical = scenario === 'critical' && !spoolerRestarted;
  const isWarn = scenario === 'warn';
  const status = isCritical ? 'CRITICAL' : isWarn ? 'WARN' : 'HEALTHY';

  const events =
    scenario === 'healthy'
      ? []
      : scenario === 'warn'
        ? [
            { id: 10016, level: 'Error', provider: 'DistributedCOM', count: 3 },
            { id: 1000, level: 'Error', provider: 'ApplicationError', count: 1 },
          ]
        : [
            { id: 7031, level: 'Error', provider: 'Service Control Manager', count: 4 },
            { id: 41, level: 'Critical', provider: 'Kernel-Power', count: 1 },
          ];

  return (
    <div className="space-y-4 text-xs">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => {
              setScenario('critical');
              setSpoolerRestarted(false);
            }}
            className={`rounded-md px-3 py-1.5 font-mono font-semibold ${
              scenario === 'critical'
                ? 'bg-amber-400 text-slate-950'
                : 'border border-slate-700 bg-slate-900 text-slate-300'
            }`}
          >
            Simulate Stopped Service
          </button>
          <button
            type="button"
            onClick={() => setScenario('warn')}
            className={`rounded-md px-3 py-1.5 font-mono font-semibold ${
              scenario === 'warn'
                ? 'bg-sky-400 text-slate-950'
                : 'border border-slate-700 bg-slate-900 text-slate-300'
            }`}
          >
            Simulate Event Spike
          </button>
          <button
            type="button"
            onClick={() => setScenario('healthy')}
            className={`rounded-md px-3 py-1.5 font-mono font-semibold ${
              scenario === 'healthy'
                ? 'bg-emerald-400 text-slate-950'
                : 'border border-slate-700 bg-slate-900 text-slate-300'
            }`}
          >
            Healthy Baseline
          </button>
        </div>

        <span
          className={`rounded px-2.5 py-1 font-mono font-bold ${
            status === 'CRITICAL'
              ? 'bg-rose-500/20 text-rose-300'
              : status === 'WARN'
                ? 'bg-amber-500/20 text-amber-300'
                : 'bg-emerald-500/20 text-emerald-300'
          }`}
        >
          STATUS: {status}
        </span>
      </div>

      <div className="rounded-lg border border-slate-800 bg-[#070B14] p-3">
        <div className="flex items-center justify-between">
          <span className="font-mono text-[11px] text-slate-400">
            AUTO-START SERVICE WATCHDOG (Win32_Service)
          </span>
          {scenario === 'critical' && !spoolerRestarted && (
            <button
              type="button"
              onClick={() => setSpoolerRestarted(true)}
              className="inline-flex items-center gap-1 rounded border border-emerald-500/40 bg-emerald-500/15 px-2.5 py-1 font-mono text-[10px] text-emerald-300 hover:bg-emerald-500/25"
            >
              <RotateCcw className="h-3 w-3" />
              Restart Spooler
            </button>
          )}
        </div>
        <p className="mt-1.5 font-mono text-slate-200">
          {scenario === 'critical' && !spoolerRestarted
            ? 'ALERT: Print Spooler (Spooler) · StartMode=Auto · State=Stopped'
            : 'All Auto-start Windows services running normally.'}
        </p>
      </div>

      {events.length > 0 && (
        <div className="space-y-1.5">
          {events.map((ev) => (
            <div
              key={ev.id}
              className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/70 px-3 py-2 font-mono"
            >
              <span className="flex items-center gap-2 text-slate-200">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
                Event ID {ev.id} · {ev.provider}
              </span>
              <span className="text-slate-400">
                {ev.level} (×{ev.count})
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function EdgeOpsDemo() {
  const [routed, setRouted] = useState(5);
  const [throttled429, setThrottled429] = useState(0);
  const [authUp, setAuthUp] = useState(true);

  const simulateBurst = () => {
    setRouted((r) => r + 5);
    setThrottled429((t) => t + 3);
  };

  return (
    <div className="space-y-4 text-xs">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={simulateBurst}
            className="rounded-md bg-violet-500 px-3 py-1.5 font-mono font-semibold text-white hover:bg-violet-400"
          >
            Simulate Traffic Burst (429)
          </button>
          <button
            type="button"
            onClick={() => setAuthUp((v) => !v)}
            className="rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 font-mono text-slate-200 hover:border-slate-500"
          >
            Toggle auth-api ({authUp ? 'UP' : 'DOWN'})
          </button>
        </div>

        <span className="font-mono text-slate-300">
          Routed: <strong>{routed}</strong> · 429 Throttled:{' '}
          <strong className={throttled429 ? 'text-amber-400' : 'text-emerald-400'}>
            {throttled429}
          </strong>
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2 font-mono">
        <div className="rounded-lg border border-slate-800 bg-[#070B14] p-2.5">
          <p className="text-[10px] text-slate-500">auth-api</p>
          <p className={authUp ? 'text-emerald-400' : 'text-rose-400'}>
            {authUp ? '200 UP · 0.7ms' : '502 BAD GATEWAY'}
          </p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-[#070B14] p-2.5">
          <p className="text-[10px] text-slate-500">dms-core</p>
          <p className="text-emerald-400">200 UP · 0.9ms</p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-[#070B14] p-2.5">
          <p className="text-[10px] text-slate-500">wafer-api</p>
          <p className="text-emerald-400">200 UP · 0.8ms</p>
        </div>
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-3 font-mono text-[11px] text-slate-300">
        Nginx Hardening: X-Frame-Options=SAMEORIGIN · X-Content-Type-Options=nosniff · limit_req=10r/s
      </div>
    </div>
  );
}

function QaPilotDemo() {
  const [targetRole, setTargetRole] = useState('DEAN');
  const [ranE2E, setRanE2E] = useState(false);

  return (
    <div className="space-y-4 text-xs">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="font-mono text-slate-400">Target Role Actor:</span>
          <select
            value={targetRole}
            onChange={(e) => {
              setTargetRole(e.target.value);
              setRanE2E(false);
            }}
            aria-label="Select QA-Pilot role scenario"
            className="rounded border border-slate-700 bg-slate-900 px-2.5 py-1 font-mono text-amber-300"
          >
            <option value="DEAN">DEAN (Full Approval E2E)</option>
            <option value="STAFF">STAFF (Negative RBAC Guard E2E)</option>
          </select>
        </div>

        <button
          type="button"
          onClick={() => setRanE2E(true)}
          className="inline-flex items-center gap-1.5 rounded-md bg-amber-400 px-3 py-1.5 font-mono font-semibold text-slate-950"
        >
          <Play className="h-3.5 w-3.5 fill-current" />
          Run Playwright POM + Contract Check
        </button>
      </div>

      <div className="space-y-1.5 rounded-lg border border-slate-800 bg-[#070B14] p-3 font-mono">
        <div className="flex justify-between">
          <span className="text-slate-300">GET /api/documents Schema &amp; Latency (&lt;250ms)</span>
          <span className="text-emerald-400">{ranE2E ? 'PASSED (18ms)' : 'READY'}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-300">
            Playwright DmsPage ({targetRole === 'DEAN' ? 'Submit -> Review -> Approve' : 'Verify 403 RBAC UI Error'})
          </span>
          <span className={ranE2E ? 'text-emerald-400' : 'text-slate-500'}>
            {ranE2E ? 'PASSED (DOM Verified)' : 'PENDING'}
          </span>
        </div>
      </div>
    </div>
  );
}

function MailPilotDemo() {
  const [sampleIdx, setSampleIdx] = useState(0);
  const [sentOutbox, setSentOutbox] = useState(false);

  const threads = [
    {
      sender: 'ops@clientportal.ph',
      subject: 'Urgent: 502 Bad Gateway on staging checkout page',
      category: 'Incident / Support',
      priority: 'P1',
      confidence: '94%',
      draft:
        'Hi ops, thank you for flagging this urgent 502 timeout. Our support team has logged a P1 incident and is inspecting Nginx upstream telemetry now.',
    },
    {
      sender: 'marketing@partner.ph',
      subject: 'Website maintenance: update hero banner & broken footer link',
      category: 'Website Maintenance',
      priority: 'P2',
      confidence: '89%',
      draft:
        'Hi marketing, we have queued the landing-page SSL check and footer fix in our GitHub staging branch for QA verification.',
    },
  ];
  const active = threads[sampleIdx];

  return (
    <div className="space-y-4 text-xs">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => {
              setSampleIdx(0);
              setSentOutbox(false);
            }}
            className={`rounded-md px-3 py-1.5 font-mono font-semibold ${
              sampleIdx === 0
                ? 'bg-indigo-400 text-slate-950'
                : 'border border-slate-700 bg-slate-900 text-slate-300'
            }`}
          >
            Thread #1 (P1 Incident)
          </button>
          <button
            type="button"
            onClick={() => {
              setSampleIdx(1);
              setSentOutbox(false);
            }}
            className={`rounded-md px-3 py-1.5 font-mono font-semibold ${
              sampleIdx === 1
                ? 'bg-indigo-400 text-slate-950'
                : 'border border-slate-700 bg-slate-900 text-slate-300'
            }`}
          >
            Thread #2 (Web Maintenance)
          </button>
        </div>

        <span className="font-mono text-emerald-400">IMAPS:993 · STARTTLS:587 OK</span>
      </div>

      <div className="rounded-lg border border-slate-800 bg-[#070B14] p-3">
        <div className="flex items-center justify-between font-mono text-[11px]">
          <span className="text-indigo-300">
            {active.priority} · {active.category}
          </span>
          <span className="text-slate-400">Confidence: {active.confidence}</span>
        </div>
        <p className="mt-1.5 font-semibold text-white">{active.subject}</p>
        <p className="mt-1 text-slate-400">From: {active.sender}</p>
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-3">
        <p className="font-mono text-[10px] uppercase text-slate-400">AI Suggested Draft</p>
        <p className="mt-1.5 text-slate-200">{active.draft}</p>
        <div className="mt-3 flex items-center justify-between">
          <span className="font-mono text-[11px] text-slate-400">
            Outbox State: {sentOutbox ? 'SENT & LOGGED' : 'PENDING_REVIEW'}
          </span>
          <button
            type="button"
            onClick={() => setSentOutbox(true)}
            className="rounded border border-emerald-500/40 bg-emerald-500/15 px-3 py-1 font-mono font-semibold text-emerald-300 hover:bg-emerald-500/25"
          >
            {sentOutbox ? 'Queued in Outbox' : 'Approve & Send Reply'}
          </button>
        </div>
      </div>
    </div>
  );
}

function SiteCareDemo() {
  const [target, setTarget] = useState('prod');

  const scans = {
    prod: {
      url: 'dist/index.html (Production Build)',
      score: '100%',
      broken: 0,
      branch: 'main · GitHub CI Active',
      checks: [
        { name: 'SEO Title & Meta Description', status: 'PASS' },
        { name: 'Open Graph Tags & Favicon', status: 'PASS' },
        { name: 'Image Alt Attributes & Local Refs', status: 'PASS' },
      ],
    },
    staging: {
      url: 'staging/preview.html (Unmerged PR)',
      score: '67%',
      broken: 2,
      branch: 'feat/landing-refresh · Needs Fix',
      checks: [
        { name: 'SEO Title & Meta Description', status: 'PASS' },
        { name: 'Open Graph Tags & Favicon', status: 'WARN (Missing og:image)' },
        { name: 'Image Alt Attributes & Local Refs', status: 'FAIL (2 missing assets)' },
      ],
    },
  };

  const active = scans[target];

  return (
    <div className="space-y-4 text-xs">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setTarget('prod')}
            className={`rounded-md px-3 py-1.5 font-mono font-semibold ${
              target === 'prod'
                ? 'bg-emerald-400 text-slate-950'
                : 'border border-slate-700 bg-slate-900 text-slate-300'
            }`}
          >
            Scan Production (main)
          </button>
          <button
            type="button"
            onClick={() => setTarget('staging')}
            className={`rounded-md px-3 py-1.5 font-mono font-semibold ${
              target === 'staging'
                ? 'bg-amber-400 text-slate-950'
                : 'border border-slate-700 bg-slate-900 text-slate-300'
            }`}
          >
            Scan Staging PR Branch
          </button>
        </div>
        <span className="font-mono text-slate-400">{active.branch}</span>
      </div>

      <div className="grid grid-cols-3 gap-2 font-mono">
        <div className="rounded-lg border border-slate-800 bg-[#070B14] p-2.5">
          <p className="text-[10px] text-slate-500">SITE HEALTH</p>
          <p className={active.score === '100%' ? 'text-lg font-bold text-emerald-400' : 'text-lg font-bold text-amber-400'}>
            {active.score}
          </p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-[#070B14] p-2.5">
          <p className="text-[10px] text-slate-500">BROKEN ASSETS</p>
          <p className={active.broken ? 'text-lg font-bold text-rose-400' : 'text-lg font-bold text-emerald-400'}>
            {active.broken}
          </p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-[#070B14] p-2.5">
          <p className="text-[10px] text-slate-500">SITEMAP XML</p>
          <p className="text-lg font-bold text-sky-400">VALID</p>
        </div>
      </div>

      <div className="space-y-1.5 rounded-lg border border-slate-800 bg-slate-900/70 p-3 font-mono">
        {active.checks.map((c) => (
          <div key={c.name} className="flex justify-between">
            <span className="text-slate-200">{c.name}</span>
            <span className={c.status === 'PASS' ? 'text-emerald-400' : 'text-amber-400'}>{c.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

const demoComponents = {
  winops: WinOpsDemo,
  'mcu-lab': McuLabDemo,
  authgate: AuthGateDemo,
  systriage: SysTriageDemo,
  'qa-telemetry': QaTelemetryDemo,
  netaudit: NetAuditDemo,
  logpulse: LogPulseDemo,
  edgeops: EdgeOpsDemo,
  'qa-pilot': QaPilotDemo,
  mailpilot: MailPilotDemo,
  sitecare: SiteCareDemo,
};

/**
 * Interactive browser-based Live Demo modal executing authentic client-side
 * simulations of the workspace engineering tools.
 */
export default function LiveDemoModal({ project, onClose }) {
  useEffect(() => {
    if (!project) return undefined;
    const onKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [project, onClose]);

  if (!project) return null;
  const ActiveDemo = demoComponents[project.id];
  if (!ActiveDemo) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="live-demo-title"
      onClick={onClose}
    >
      <div
        className="animate-modal-in w-full max-w-3xl rounded-xl border border-sky-400/40 bg-[#0B1120] p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg border border-sky-400/40 bg-sky-400/10 text-sky-400">
              <Terminal className="h-4 w-4" />
            </span>
            <div>
              <p className="font-mono text-[10px] uppercase tracking-wider text-sky-400">
                Interactive Live Sandbox // Client-Side Simulation
              </p>
              <h3 id="live-demo-title" className="text-lg font-semibold text-white">
                {project.title}
              </h3>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close live demo modal"
            className="rounded-md border border-slate-700 p-1.5 text-slate-400 hover:border-slate-500 hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="mt-5">
          <ActiveDemo />
        </div>
      </div>
    </div>
  );
}
