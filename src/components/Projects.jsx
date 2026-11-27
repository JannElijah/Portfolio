import { useEffect, useState } from 'react';
import {
  ArrowUpRight,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  Copy,
  ExternalLink,
  Figma,
  FileCode2,
  Github,
  Maximize2,
  Play,
  Sparkles,
  Terminal,
  X,
} from 'lucide-react';
import {
  additionalProjects,
  featuredProjects,
  isConfiguredLink,
  projectFilterTabs,
} from '../data/portfolioData';
import { matchProjectBySkill } from '../utils/skillMatch';
import ProjectVisual from './ProjectVisuals';
import LiveDemoModal from './LiveDemoModal';
import Reveal from './Reveal';
import SpotlightCard from './SpotlightCard';

const linkIconMap = {
  live: ExternalLink,
  github: Github,
  architecture: FileCode2,
  figma: Figma,
};

export function ProjectDetailsModal({
  project,
  onClose,
  onLaunchDemo = null,
  onNotify = null,
}) {
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

  const activeLinks = (project.links || []).filter((l) => isConfiguredLink(l.url));
  const hasSandboxAction = Boolean(project.demoId && typeof onLaunchDemo === 'function');

  const handleCopyCli = async () => {
    try {
      await navigator.clipboard.writeText(project.details.cliUsage);
      setCopiedCli(true);
      onNotify?.('CLI command copied to clipboard');
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
        className="animate-modal-in max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl border border-zinc-700 bg-[#121215] shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {project.image && (
          <div className="relative aspect-video w-full overflow-hidden border-b border-zinc-800 bg-zinc-950">
            <img
              src={project.image}
              alt={project.imageAlt || project.title}
              className="h-full w-full object-cover object-top"
            />
            <div
              aria-hidden="true"
              className="pointer-events-none absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-[#121215] via-[#121215]/45 to-transparent"
            />
          </div>
        )}

        <div className="p-6">
          <div className="flex items-start justify-between gap-4 border-b border-zinc-800 pb-4">
            <div>
              <p className="text-xs font-medium" style={{ color: project.accentColor }}>
                {project.categoryLabel || project.category}
                {project.role && <span className="text-zinc-400"> · {project.role}</span>}
              </p>
              <h3 id="project-details-title" className="mt-1 text-xl font-semibold text-white">
                {project.title}
              </h3>
            </div>
            <button
              type="button"
              onClick={onClose}
              aria-label="Close project details"
              className="rounded-md border border-zinc-700 p-1.5 text-zinc-400 transition-colors hover:text-white"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="mt-5 space-y-5 text-sm">
            <p className="leading-relaxed text-zinc-300">{project.details.overview}</p>

            {Array.isArray(project.stack) && project.stack.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                  Complete Tech Stack
                </h4>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {project.stack.map((tech) => (
                    <span
                      key={tech}
                      className="rounded border border-zinc-800 bg-zinc-950 px-2.5 py-0.5 text-xs font-medium text-zinc-200"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            )}

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
                    className="inline-flex items-center gap-1 rounded border border-zinc-800 px-2 py-0.5 text-[10px] text-zinc-300 transition-colors hover:border-zinc-600 hover:text-white"
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

          {(hasSandboxAction || activeLinks.length > 0) && (
            <div className="mt-6 flex flex-wrap items-center gap-2.5 border-t border-zinc-800 pt-4">
              {hasSandboxAction && (
                <button
                  type="button"
                  onClick={() => onLaunchDemo(project)}
                  className="inline-flex items-center gap-1.5 rounded-md bg-zinc-100 px-3.5 py-2 text-xs font-semibold text-zinc-950 transition-colors hover:bg-white"
                >
                  <Play className="h-3.5 w-3.5 fill-current" aria-hidden="true" />
                  <span>Launch Live Sandbox</span>
                </button>
              )}

              {activeLinks.map((link) => {
                const Icon = linkIconMap[link.kind] || ExternalLink;
                return (
                  <a
                    key={link.label}
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-900 px-3.5 py-2 text-xs font-medium text-zinc-200 transition-colors hover:border-zinc-500 hover:text-white"
                  >
                    <Icon className="h-3.5 w-3.5" aria-hidden="true" />
                    <span>{link.label}</span>
                  </a>
                );
              })}
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
        className="animate-modal-in w-full max-w-5xl rounded-xl border border-zinc-700 bg-[#121215] p-4 shadow-2xl"
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
                  className="rounded-md border border-zinc-700 p-1.5 text-zinc-300 transition-colors hover:border-zinc-500 hover:text-white"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  onClick={() => onNavigate((activeIndex + 1) % items.length)}
                  aria-label="Next screenshot"
                  className="rounded-md border border-zinc-700 p-1.5 text-zinc-300 transition-colors hover:border-zinc-500 hover:text-white"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </>
            )}
            <button
              type="button"
              onClick={onClose}
              aria-label="Close screenshot preview"
              className="rounded-md border border-zinc-700 p-1.5 text-zinc-400 transition-colors hover:border-zinc-500 hover:text-white"
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

const allScreenshots = [...featuredProjects, ...additionalProjects]
  .filter((p) => p.image)
  .map((p) => ({
    src: p.image,
    alt: p.imageAlt || p.title,
    title: p.title,
    categoryLabel: p.categoryLabel || p.category,
    accentColor: p.accentColor,
  }));

const COLLAPSED_FEATURED_COUNT = 5;

/**
 * Spotlight Bento + 2-column Featured Projects grid with progressive disclosure and skill filtering.
 */
export default function Projects({
  activeCategory: controlledCategory = undefined,
  onCategoryChange = undefined,
  activeSkill = null,
  onClearSkill = null,
  onNotify = null,
}) {
  const [internalCategory, setInternalCategory] = useState('all');
  const [showAllFeatured, setShowAllFeatured] = useState(false);
  const [selectedDetails, setSelectedDetails] = useState(null);
  const [liveDemoProject, setLiveDemoProject] = useState(null);
  const [lightboxIndex, setLightboxIndex] = useState(null);

  const activeCategory =
    controlledCategory !== undefined ? controlledCategory : internalCategory;
  const setCategory = (next) => {
    if (typeof onCategoryChange === 'function') onCategoryChange(next);
    if (controlledCategory === undefined) setInternalCategory(next);
  };

  const isFiltered = activeCategory !== 'all' || Boolean(activeSkill);

  const visibleProjects = activeSkill
    ? featuredProjects.filter((p) => matchProjectBySkill(p, activeSkill))
    : activeCategory === 'all'
      ? featuredProjects
      : featuredProjects.filter((p) => p.categories.includes(activeCategory));

  const displayedProjects =
    isFiltered || showAllFeatured
      ? visibleProjects
      : visibleProjects.slice(0, COLLAPSED_FEATURED_COUNT);

  const hiddenCount = visibleProjects.length - displayedProjects.length;
  const useSpotlightLayout = displayedProjects.length >= 3;
  const hasBottomSpotlight = useSpotlightLayout && (displayedProjects.length - 1) % 2 === 1;

  const getTabCount = (tabId) =>
    tabId === 'all'
      ? featuredProjects.length
      : featuredProjects.filter((p) => p.categories.includes(tabId)).length;

  const renderCardMedia = (project, extraClassName = '') => (
    <div
      className={`relative aspect-video w-full overflow-hidden bg-zinc-950 ${extraClassName}`}
    >
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
            className="h-full w-full object-cover object-top transition-transform duration-500 ease-out group-hover:scale-[1.03]"
          />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-[#111114]/80 via-[#111114]/25 to-transparent"
          />
          <span className="pointer-events-none absolute right-2.5 bottom-2.5 inline-flex items-center gap-1 rounded border border-zinc-700/90 bg-zinc-950/90 px-2 py-1 text-[11px] font-medium text-zinc-200 opacity-0 transition-opacity duration-200 group-hover/img:opacity-100">
            <Maximize2 className="h-3 w-3" aria-hidden="true" />
            <span>Zoom</span>
          </span>
        </button>
      ) : (
        <ProjectVisual type={project.visualType} />
      )}
    </div>
  );

  const renderCardActions = (project, activeLinks) => (
    <div className="mt-auto flex flex-wrap items-center gap-2 pt-5">
      {project.demoId && (
        <button
          type="button"
          onClick={() => setLiveDemoProject({ ...project, id: project.demoId })}
          className="inline-flex items-center gap-1.5 rounded-md bg-zinc-100 px-3 py-1.5 text-xs font-semibold text-zinc-950 transition-all duration-200 hover:-translate-y-0.5 hover:bg-white active:translate-y-0"
        >
          <Play className="h-3.5 w-3.5 fill-current" aria-hidden="true" />
          <span>Live Sandbox</span>
        </button>
      )}

      <button
        type="button"
        onClick={() => setSelectedDetails(project)}
        className="inline-flex items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-200 transition-colors hover:border-zinc-500 hover:text-white"
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
            className="inline-flex items-center gap-1.5 rounded-md border border-zinc-800 bg-zinc-950 px-3 py-1.5 text-xs font-medium text-zinc-300 transition-colors hover:border-zinc-600 hover:text-white"
          >
            <Icon className="h-3.5 w-3.5" aria-hidden="true" />
            <span>{link.label}</span>
          </a>
        );
      })}
    </div>
  );

  return (
    <section id="projects" className="border-b border-zinc-800/80 bg-[#09090B] py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-5 sm:px-8">
        <Reveal className="flex flex-col justify-between gap-6 sm:flex-row sm:items-end">
          <div className="max-w-xl">
            <p className="font-mono text-[11px] uppercase tracking-widest text-zinc-500">
              01 · Selected Work
            </p>
            <h2 className="mt-2 text-2xl font-bold tracking-tight text-white sm:text-3xl">
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
              const selected = !activeSkill && activeCategory === tab.id;
              return (
                <button
                  key={tab.id}
                  type="button"
                  role="tab"
                  aria-selected={selected}
                  onClick={() => setCategory(tab.id)}
                  className={`rounded-md px-3 py-1.5 text-xs font-medium transition-all duration-200 ${
                    selected
                      ? 'bg-zinc-100 font-semibold text-zinc-950 shadow-sm'
                      : 'text-zinc-400 hover:text-zinc-200'
                  }`}
                >
                  {tab.label} ({getTabCount(tab.id)})
                </button>
              );
            })}
          </div>
        </Reveal>

        {activeSkill && (
          <div className="mt-6 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-2.5 text-xs text-emerald-200">
            <span>
              Filtered by skill: <strong>{activeSkill}</strong> · {visibleProjects.length} featured
              {visibleProjects.length === 1 ? ' project' : ' projects'}
            </span>
            {typeof onClearSkill === 'function' && (
              <button
                type="button"
                onClick={onClearSkill}
                className="inline-flex items-center gap-1 rounded border border-emerald-500/35 bg-zinc-950/70 px-2.5 py-1 text-xs font-medium text-emerald-200 transition-colors hover:border-emerald-400 hover:text-white"
              >
                <span>Clear skill filter</span>
                <X className="h-3 w-3" aria-hidden="true" />
              </button>
            )}
          </div>
        )}

        {displayedProjects.length === 0 ? (
          <div className="mt-8 rounded-xl border border-zinc-800 bg-[#111114] px-6 py-8 text-center">
            <p className="text-sm text-zinc-300">
              No featured cards match <strong>{activeSkill}</strong> — check the matching entries in
              the Engineering Archive below or clear the skill filter.
            </p>
            {typeof onClearSkill === 'function' && (
              <button
                type="button"
                onClick={onClearSkill}
                className="mt-4 inline-flex items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-900 px-3.5 py-1.5 text-xs font-medium text-zinc-200 transition-colors hover:border-zinc-500 hover:text-white"
              >
                <span>Reset to all projects</span>
              </button>
            )}
          </div>
        ) : (
          <div className="mt-10 grid grid-cols-1 gap-6 md:grid-cols-2">
            {displayedProjects.map((project, index) => {
              const activeLinks = project.links.filter((l) => isConfiguredLink(l.url));
              const isSpotlight =
                useSpotlightLayout &&
                (index === 0 || (hasBottomSpotlight && index === displayedProjects.length - 1));
              const shownStack = isSpotlight ? project.stack : project.stack.slice(0, 4);
              const extraStackCount = project.stack.length - shownStack.length;

              if (isSpotlight) {
                return (
                  <Reveal key={project.id} className="md:col-span-2">
                    <SpotlightCard
                      accentColor={project.accentColor}
                      className="rounded-xl border border-zinc-800 bg-[#111114] transition-all duration-300 hover:-translate-y-1 hover:border-zinc-700 hover:shadow-[0_18px_42px_-18px_rgba(0,0,0,0.9)]"
                    >
                      <div className="grid grid-cols-1 lg:grid-cols-12">
                        {renderCardMedia(
                          project,
                          'border-b border-zinc-800/80 lg:col-span-7 lg:h-full lg:border-r lg:border-b-0'
                        )}

                        <div className="flex flex-col p-6 sm:p-7 lg:col-span-5">
                          <div className="flex items-center justify-between gap-2 text-xs">
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
                            <span className="inline-flex items-center gap-1 rounded-full border border-zinc-700/80 bg-zinc-900 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-zinc-300">
                              <Sparkles className="h-2.5 w-2.5 text-zinc-400" aria-hidden="true" />
                              <span>{index === 0 ? 'Flagship Spotlight' : 'Hardware & QA'}</span>
                            </span>
                          </div>

                          <h3 className="mt-2.5 text-xl font-semibold tracking-tight text-white sm:text-2xl">
                            {project.title}
                          </h3>

                          <p className="mt-2.5 text-sm leading-relaxed text-zinc-400">
                            {project.summary}
                          </p>

                          {project.details?.highlights?.length > 0 && (
                            <ul className="mt-4 space-y-1.5 text-xs text-zinc-300">
                              {project.details.highlights.slice(0, 2).map((item) => (
                                <li key={item} className="flex items-start gap-2">
                                  <CheckCircle2
                                    className="mt-0.5 h-3.5 w-3.5 shrink-0"
                                    style={{ color: project.accentColor }}
                                  />
                                  <span>{item}</span>
                                </li>
                              ))}
                            </ul>
                          )}

                          <div className="mt-4 flex flex-wrap gap-1.5">
                            {shownStack.map((tech) => (
                              <span
                                key={tech}
                                className="rounded border border-zinc-800 bg-zinc-950 px-2 py-0.5 text-[11px] font-medium text-zinc-300"
                              >
                                {tech}
                              </span>
                            ))}
                          </div>

                          {renderCardActions(project, activeLinks)}
                        </div>
                      </div>
                    </SpotlightCard>
                  </Reveal>
                );
              }

              return (
                <Reveal key={project.id} delay={((index - (useSpotlightLayout ? 1 : 0)) % 2) * 70} className="h-full">
                  <SpotlightCard
                    accentColor={project.accentColor}
                    className="flex h-full flex-col rounded-xl border border-zinc-800 bg-[#111114] transition-all duration-300 hover:-translate-y-1 hover:border-zinc-700 hover:shadow-[0_16px_38px_-18px_rgba(0,0,0,0.85)]"
                  >
                    {renderCardMedia(project, 'border-b border-zinc-800/80')}

                    <div className="flex flex-1 flex-col p-5 sm:p-6">
                      <div className="flex items-center justify-between gap-2 text-xs">
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
                        <span className="font-mono text-[11px] text-zinc-500">
                          {String(index + 1).padStart(2, '0')}
                        </span>
                      </div>

                      <h3 className="mt-2 text-lg font-semibold tracking-tight text-white sm:text-xl">
                        {project.title}
                      </h3>

                      <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-zinc-400">
                        {project.summary}
                      </p>

                      <div className="mt-4 flex flex-wrap gap-1.5">
                        {shownStack.map((tech) => (
                          <span
                            key={tech}
                            className="rounded border border-zinc-800 bg-zinc-950 px-2 py-0.5 text-[11px] font-medium text-zinc-300"
                          >
                            {tech}
                          </span>
                        ))}
                        {extraStackCount > 0 && (
                          <span className="rounded border border-zinc-800/80 bg-zinc-950/60 px-2 py-0.5 font-mono text-[11px] text-zinc-500">
                            +{extraStackCount}
                          </span>
                        )}
                      </div>

                      {renderCardActions(project, activeLinks)}
                    </div>
                  </SpotlightCard>
                </Reveal>
              );
            })}
          </div>
        )}

        {!isFiltered && visibleProjects.length > COLLAPSED_FEATURED_COUNT && (
          <div className="mt-8 flex justify-center">
            <button
              type="button"
              onClick={() => setShowAllFeatured((prev) => !prev)}
              className="inline-flex items-center gap-2 rounded-lg border border-zinc-700 bg-[#121215] px-4 py-2 text-xs font-medium text-zinc-200 transition-all duration-200 hover:-translate-y-0.5 hover:border-zinc-500 hover:bg-zinc-900 hover:text-white"
            >
              {showAllFeatured ? (
                <>
                  <span>Show fewer projects</span>
                  <ChevronUp className="h-3.5 w-3.5 text-zinc-400" aria-hidden="true" />
                </>
              ) : (
                <>
                  <span>
                    Show all {visibleProjects.length} featured projects (+{hiddenCount} more)
                  </span>
                  <ChevronDown className="h-3.5 w-3.5 text-zinc-400" aria-hidden="true" />
                </>
              )}
            </button>
          </div>
        )}
      </div>

      <ProjectDetailsModal
        project={selectedDetails}
        onClose={() => setSelectedDetails(null)}
        onLaunchDemo={(project) => {
          setSelectedDetails(null);
          setLiveDemoProject({ ...project, id: project.demoId });
        }}
        onNotify={onNotify}
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
