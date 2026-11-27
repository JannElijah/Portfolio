const SKILL_ALIASES = {
  'postgresql (supabase)': ['supabase', 'postgresql', 'postgres'],
  'html5 / css3': ['html5', 'html', 'css'],
  'git / github actions': ['github actions', 'git'],
  'seo & sitemaps': ['seo', 'sitemap'],
  'docker / nginx': ['docker', 'nginx'],
  'windows 11 administration': ['windows', 'powershell', 'cim', 'event'],
  'email clients (imaps / smtp)': ['imaps', 'smtp', 'email'],
  'device configuration & management': ['winget', 'cim', 'uart', 'cisco', 'workstation'],
  'winget & cim provisioning': ['winget', 'cim'],
  'fernet / pbkdf2 / rbac': ['fernet', 'pbkdf2', 'rbac', 'jwt'],
  'multi-branch ospf routing': ['ospf', 'cisco', 'vlsm'],
  'cisco cme voip telephony': ['voip', 'cme', 'cisco'],
  'playwright e2e': ['playwright', 'e2e'],
  'automated testing (pytest / vitest)': ['pytest', 'vitest', 'junit'],
  'technical documentation': ['audit', 'report', 'dms', 'docs'],
  'figma prototyping': ['figma'],
  'unity 6 lts': ['unity'],
  'c#': ['c#', 'unity'],
  javascript: ['javascript', 'react', 'vite', 'phaser'],
  sql: ['sqlite', 'supabase', 'postgresql', 'sql'],
  vercel: ['vercel', 'cognicore'],
  render: ['render', 'cognicore'],
};

function buildSearchCorpus(project) {
  const parts = [
    project.title,
    project.summary,
    project.categoryLabel,
    project.category,
    ...(project.stack || []),
    ...(project.details?.highlights || []),
  ];
  return parts.filter(Boolean).join(' ').toLowerCase();
}

/**
 * Checks whether a project matches a given skill chip label.
 */
export function matchProjectBySkill(project, skillLabel) {
  if (!project || !skillLabel) return false;
  const normalized = skillLabel.trim().toLowerCase();
  if (!normalized) return false;

  const terms = SKILL_ALIASES[normalized] || [normalized];
  const corpus = buildSearchCorpus(project);
  return terms.some((term) => corpus.includes(term));
}

/**
 * Counts how many projects in a collection match a given skill chip label.
 */
export function countMatchingProjects(projects, skillLabel) {
  if (!Array.isArray(projects) || !skillLabel) return 0;
  return projects.reduce(
    (count, project) => (matchProjectBySkill(project, skillLabel) ? count + 1 : count),
    0
  );
}
