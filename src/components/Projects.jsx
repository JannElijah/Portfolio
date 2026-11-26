import { useEffect, useState } from 'react';
import {
  ExternalLink,
  Github,
  FileCode2,
  Figma,
  Play,
  ArrowUpRight,
  CheckCircle2,
  Maximize2,
  ChevronLeft,
  ChevronRight,
  Copy,
  Check,
  Terminal,
  X,
} from 'lucide-react';
import {
  additionalProjects,
  featuredProjects,
  isConfiguredLink,
  projectFilterTabs,
} from '../data/portfolioData';
import ProjectVisual from './ProjectVisuals';
import LiveDemoModal from './LiveDemoModal';

export function ProjectDetailsModal({ project, onClose }) {
  const [copiedCli, setCopiedCli] = useState(false);

  useEffect(() => {
    setCopiedCli(false);
  }, [project]);

  useEffect(() => {
    if (!project) return undefined;
    const onKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [project, onClose]);

  if (!project || !project.details) return null;

  const handleCopyCli = async () => {
    try {
      await navigator.clipboard.writeText(project.details.cliUsage);
      setCopiedCli(true);
      setTimeout(() => setCopiedCli(false), 1800);
    } catch {
      setCopiedCli(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="project-details-title"
      onClick={onClose}
    >
      <div
        className="w-full max-w-xl rounded-xl border border-zinc-700 bg-[#121215] p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 border-b border-zinc-800 pb-4">
          <div>
            <p className="text-xs font-medium" style={{ color: project.accentColor }}>
              {project.categoryLabel || project.category}
            </p>
            <h3 id="project-details-title" className="mt-1 text-xl font-semibold text-white">
              {project.title}
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close project details"
            className="rounded-md border border-zinc-700 p-1.5 text-zinc-400 hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="mt-5 space-y-4 text-sm">
          <p className="leading-relaxed text-zinc-300">{project.details.overview}</p>
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
              Engineering Highlights
            </h4>
            <ul className="mt-2.5 space-y-2 text-zinc-200">
              {project.details.highlights.map((item) => (
                <li key={item} className="flex items-start gap-2.5">
                  <CheckCircle2
                    className="mt-0.5 h-4 w-4 shrink-0"
                    style={{ color: project.accentColor }}
                  />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {project.details.cliUsage && (
            <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-3">
              <div className="flex items-center justify-between gap-2 pb-1.5">
                <span className="inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-zinc-500">
                  <Terminal className="h-3 w-3" aria-hidden="true" />
                  <span>Local Run / CLI</span>
                </span>
                <button
                  type="button"
                  onClick={handleCopyCli}
                  className="inline-flex items-center gap-1 rounded border border-zinc-800 px-2 py-0.5 text-[10px] text-zinc-300 hover:border-zinc-600 hover:text-white"
                >
                  {copiedCli ? (
                    <>
                      <Check className="h-2.5 w-2.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-2.5 w-2.5" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
              <code className="block overflow-x-auto font-mono text-xs text-zinc-200">
                {project.details.cliUsage}
              </code>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function ScreenshotLightboxModal({
  item = null,
  items = [],
  activeIndex = null,
  onNavigate = null,
  onClose,
}) {
  const hasGallery = Array.isArray(items) && items.length > 0 && activeIndex !== null;
  const currentItem = hasGallery ? items[activeIndex] : item;
  const canNavigate = hasGallery && items.length > 1 && typeof onNavigate === 'function';

  useEffect(() => {
    if (!currentItem) return undefined;
    const onKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
      if (canNavigate && e.key === 'ArrowLeft') {
        onNavigate((activeIndex - 1 + items.length) % items.length);
      }
      if (canNavigate && e.key === 'ArrowRight') {
        onNavigate((activeIndex + 1) % items.length);
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [currentItem, canNavigate, activeIndex, items.length, onNavigate, onClose]);

  if (!currentItem) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="lightbox-title"
      onClick={onClose}
    >
      <div
        className="w-full max-w-5xl rounded-xl border border-zinc-700 bg-[#121215] p-4 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between gap-4 border-b border-zinc-800 pb-3">
          <div className="min-w-0">
            {currentItem.categoryLabel && (
              <p className="text-xs font-medium" style={{ color: currentItem.accentColor || '#A1A1AA' }}>
                {currentItem.categoryLabel}
                {hasGallery && ` · ${activeIndex + 1} / ${items.length}`}
              </p>
            )}
            <h3 id="lightbox-title" className="truncate text-base font-semibold text-white sm:text-lg">
              {currentItem.title}
            </h3>
          </div>
          <div className="flex shrink-0 items-center gap-1.5">
            {canNavigate && (
              <>
                <button
                  type="button"
                  onClick={() => onNavigate((activeIndex - 1 + items.length) % items.length)}
                  aria-label="Previous screenshot"
                  className="rounded-md border border-zinc-700 p-1.5 text-zinc-300 hover:border-zinc-500 hover:text-white"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  onClick={() => onNavigate((activeIndex + 1) % items.length)}
                  aria-label="Next screenshot"
                  className="rounded-md border border-zinc-700 p-1.5 text-zinc-300 hover:border-zinc-500 hover:text-white"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </>
            )}
            <button
              type="button"
              onClick={onClose}
              aria-label="Close screenshot preview"
              className="rounded-md border border-zinc-700 p-1.5 text-zinc-400 hover:border-zinc-500 hover:text-white"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        <div className="mt-4 overflow-hidden rounded-lg border border-zinc-800 bg-zinc-950">
          <img
            src={currentItem.src}
            alt={currentItem.alt || currentItem.title}
            className="max-h-[72vh] w-full object-contain"
          />
        </div>
      </div>
    </div>
  );
}

const linkIconMap = {
  live: ExternalLink,
  github: Github,
  architecture: FileCode2,
  figma: Figma,
};

const allScreenshots = [...featuredProjects, ...additionalProjects]
  .filter((p) => p.image)
  .map((p) => ({
    src: p.image,
    alt: p.imageAlt || p.title,
    title: p.title,
    categoryLabel: p.categoryLabel || p.category,
    accentColor: p.accentColor,
  }));

/**
 * Editorial Featured Projects displaying real captured screenshots of each
 * uniquely themed app alongside concise descriptions and per-project accents.
 */
export default function Projects({
  activeCategory: controlledCategory = undefined,
  onCategoryChange = undefined,
}) {
  const [internalCategory, setInternalCategory] = useState('all');
  const [selectedDetails, setSelectedDetails] = useState(null);
  const [liveDemoProject, setLiveDemoProject] = useState(null);
  const [lightboxIndex, setLightboxIndex] = useState(null);

  const activeCategory =
    controlledCategory !== undefined ? controlledCategory : internalCategory;
  const setCategory = (next) => {
    if (typeof onCategoryChange === 'function') onCategoryChange(next);
    if (controlledCategory === undefined) setInternalCategory(next);
  };

  const visibleProjects =
    activeCategory === 'all'
      ? featuredProjects
      : featuredProjects.filter((p) => p.categories.includes(activeCategory));

  const getTabCount = (tabId) =>
    tabId === 'all'
      ? featuredProjects.length
      : featuredProjects.filter((p) => p.categories.includes(tabId)).length;

  return (
    <section id="projects" className="border-b border-zinc-800/80 bg-[#09090B] py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-5 sm:px-8">
        <div className="flex flex-col justify-between gap-6 sm:flex-row sm:items-end">
          <div className="max-w-xl">
            <h2 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
              Selected Projects
            </h2>
            <p className="mt-2 text-sm text-zinc-400 sm:text-base">
              Real applications and engineering systems built across web, Python, networking, and QA.
            </p>
          </div>

          <div
            role="tablist"
            aria-label="Filter projects"
            className="inline-flex flex-wrap gap-1 rounded-lg border border-zinc-800 bg-[#121215] p-1"
          >
            {projectFilterTabs.map((tab) => {
              const selected = activeCategory === tab.id;
              return (
                <button
                  key={tab.id}
                  type="button"
                  role="tab"
                  aria-selected={selected}
                  onClick={() => setCategory(tab.id)}
                  className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                    selected
                      ? 'bg-zinc-100 font-semibold text-zinc-950'
                      : 'text-zinc-400 hover:text-zinc-200'
                  }`}
                >
                  {tab.label} ({getTabCount(tab.id)})
                </button>
              );
            })}
          </div>
        </div>

        <div className="mt-10 space-y-6">
          {visibleProjects.map((project, index) => {
            const activeLinks = project.links.filter((l) => isConfiguredLink(l.url));
            return (
              <article
                key={project.id}
                className="group grid grid-cols-1 gap-6 rounded-xl border border-zinc-800 bg-[#111114] p-5 transition-colors hover:border-zinc-700 sm:p-6 md:grid-cols-12 md:items-center md:gap-8"
              >
                {/* Left 16:9 Screenshot / Visual */}
                <div className="md:col-span-5">
                  <div className="aspect-video w-full overflow-hidden rounded-lg border border-zinc-800 bg-zinc-950">
                    {project.image ? (
                      <button
                        type="button"
                        onClick={() => {
                          const idx = allScreenshots.findIndex((s) => s.src === project.image);
                          setLightboxIndex(idx >= 0 ? idx : 0);
                        }}
                        aria-label={`Inspect ${project.title} screenshot`}
                        className="group/img relative block h-full w-full cursor-zoom-in text-left focus:outline-none focus:ring-2 focus:ring-zinc-400"
                      >
                        <img
                          src={project.image}
                          alt={project.imageAlt}
                          className="h-full w-full object-cover object-top transition-transform duration-500 group-hover:scale-[1.02]"
                        />
                        <span className="pointer-events-none absolute right-2.5 bottom-2.5 inline-flex items-center gap-1 rounded border border-zinc-700/90 bg-zinc-950/85 px-2 py-1 text-[11px] font-medium text-zinc-200 opacity-0 transition-opacity group-hover/img:opacity-100">
                          <Maximize2 className="h-3 w-3" aria-hidden="true" />
                          <span>Zoom</span>
                        </span>
                      </button>
                    ) : (
                      <ProjectVisual type={project.visualType} />
                    )}
                  </div>
                </div>

                {/* Right Project Copy with Per-Project Theme Accent */}
                <div className="flex flex-col md:col-span-7">
                  <div className="flex flex-wrap items-center gap-2.5 text-xs">
                    <span className="font-mono text-zinc-400">
                      {String(index + 1).padStart(2, '0')}
                    </span>
                    <span
                      className="inline-flex items-center gap-1.5 font-medium"
                      style={{ color: project.accentColor }}
                    >
                      <span
                        className="h-1.5 w-1.5 rounded-full"
                        style={{ backgroundColor: project.accentColor }}
                        aria-hidden="true"
                      />
                      {project.categoryLabel}
                    </span>
                    <span className="text-zinc-400">· {project.role}</span>
                    {project.folderPath && (
                      <span className="font-mono text-[11px] text-zinc-400">
                        {project.folderPath}
                      </span>
                    )}
                  </div>

                  <h3 className="mt-2 text-xl font-semibold tracking-tight text-white">
                    {project.title}
                  </h3>

                  <p className="mt-2.5 text-sm leading-relaxed text-zinc-300">
                    {project.summary}
                  </p>

                  <div className="mt-4 flex flex-wrap gap-1.5">
                    {project.stack.map((tech) => (
                      <span
                        key={tech}
                        className="rounded border border-zinc-800 bg-zinc-950 px-2.5 py-0.5 text-xs font-medium text-zinc-300"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>

                  <div className="mt-5 flex flex-wrap items-center gap-2.5">
                    {project.demoId && (
                      <button
                        type="button"
                        onClick={() => setLiveDemoProject({ ...project, id: project.demoId })}
                        className="inline-flex items-center gap-1.5 rounded-md bg-zinc-100 px-3.5 py-1.5 text-xs font-semibold text-zinc-950 transition-colors hover:bg-white"
                      >
                        <Play className="h-3.5 w-3.5 fill-current" aria-hidden="true" />
                        <span>Live Sandbox</span>
                      </button>
                    )}

                    <button
                      type="button"
                      onClick={() => setSelectedDetails(project)}
                      className="inline-flex items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-900 px-3.5 py-1.5 text-xs font-medium text-zinc-200 transition-colors hover:border-zinc-500 hover:text-white"
                    >
                      <span>Project Details</span>
                      <ArrowUpRight className="h-3.5 w-3.5 text-zinc-400" aria-hidden="true" />
                    </button>

                    {activeLinks.map((link) => {
                      const Icon = linkIconMap[link.kind] || ExternalLink;
                      return (
                        <a
                          key={link.label}
                          href={link.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-900 px-3.5 py-1.5 text-xs font-medium text-zinc-200 transition-colors hover:border-zinc-500 hover:text-white"
                        >
                          <Icon className="h-3.5 w-3.5" aria-hidden="true" />
                          <span>{link.label}</span>
                        </a>
                      );
                    })}
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </div>

      <ProjectDetailsModal
        project={selectedDetails}
        onClose={() => setSelectedDetails(null)}
      />

      <LiveDemoModal
        project={liveDemoProject}
        onClose={() => setLiveDemoProject(null)}
      />

      <ScreenshotLightboxModal
        items={allScreenshots}
        activeIndex={lightboxIndex}
        onNavigate={setLightboxIndex}
        onClose={() => setLightboxIndex(null)}
      />
    </section>
  );
}
