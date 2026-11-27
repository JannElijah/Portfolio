import { useState } from 'react';
import { ArrowUpRight, Github, Maximize2, Play, X } from 'lucide-react';
import { additionalProjects, featuredProjects, isConfiguredLink } from '../data/portfolioData';
import { matchProjectBySkill } from '../utils/skillMatch';
import LiveDemoModal from './LiveDemoModal';
import { ProjectDetailsModal, ScreenshotLightboxModal } from './Projects';
import Reveal from './Reveal';

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
 * Compact Engineering Archive ledger for IT/Ops utilities, UPHSD DMS, AuthGate, QA-Pilot, and EdgeOps.
 */
export default function SecondaryProjects({
  activeCategory = 'all',
  onResetFilter = null,
  activeSkill = null,
  onClearSkill = null,
  onNotify = null,
}) {
  const [liveDemoProject, setLiveDemoProject] = useState(null);
  const [selectedDetails, setSelectedDetails] = useState(null);
  const [lightboxIndex, setLightboxIndex] = useState(null);

  const visibleAdditional = activeSkill
    ? additionalProjects.filter((p) => matchProjectBySkill(p, activeSkill))
    : activeCategory === 'all'
      ? additionalProjects
      : additionalProjects.filter((p) => p.categories?.includes(activeCategory));

  return (
    <section
      id="additional-work"
      className="border-b border-zinc-800/80 bg-[#0D0D10] py-16 sm:py-20"
    >
      <div className="mx-auto max-w-6xl px-5 sm:px-8">
        <Reveal className="flex flex-wrap items-end justify-between gap-4">
          <div className="max-w-xl">
            <p className="font-mono text-[11px] uppercase tracking-widest text-zinc-500">
              02 · Engineering Archive
            </p>
            <h2 className="mt-2 text-xl font-semibold tracking-tight text-white sm:text-2xl">
              Additional Systems, UI/UX &amp; 3D Engineering
            </h2>
            <p className="mt-1.5 text-sm text-zinc-400">
              Supporting IT automation utilities, institutional workflow prototypes, and Unity C# builds.
            </p>
          </div>

          {!activeSkill && activeCategory !== 'all' && typeof onResetFilter === 'function' && (
            <button
              type="button"
              onClick={onResetFilter}
              className="rounded-md border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-300 transition-colors hover:border-zinc-500 hover:text-white"
            >
              Showing {visibleAdditional.length} matching · Show all
            </button>
          )}

          {activeSkill && typeof onClearSkill === 'function' && (
            <button
              type="button"
              onClick={onClearSkill}
              className="inline-flex items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-300 transition-colors hover:border-zinc-500 hover:text-white"
            >
              <span>
                {visibleAdditional.length} archive match{visibleAdditional.length === 1 ? '' : 'es'} ·
                Clear
              </span>
              <X className="h-3 w-3" aria-hidden="true" />
            </button>
          )}
        </Reveal>

        {visibleAdditional.length === 0 ? (
          <div className="mt-8 rounded-xl border border-zinc-800 bg-[#111114] px-6 py-6 text-center text-sm text-zinc-400">
            No archive systems match <strong>{activeSkill}</strong>.
          </div>
        ) : (
          <div className="mt-8 divide-y divide-zinc-800/80 overflow-hidden rounded-xl border border-zinc-800 bg-[#111114]">
            {visibleAdditional.map((project, idx) => {
              const shownStack = project.stack.slice(0, 4);
              const extraCount = project.stack.length - shownStack.length;

              return (
                <Reveal key={project.id} delay={Math.min(idx * 45, 220)}>
                  <article className="group relative flex flex-col gap-4 px-5 py-4 transition-colors duration-200 hover:bg-zinc-900/55 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:gap-6">
                    <span
                      aria-hidden="true"
                      className="pointer-events-none absolute inset-y-0 left-0 w-0.5 opacity-0 transition-opacity duration-200 group-hover:opacity-100"
                      style={{ backgroundColor: project.accentColor }}
                    />

                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2 text-xs">
                        <span
                          className="inline-flex items-center gap-1.5 font-medium"
                          style={{ color: project.accentColor }}
                        >
                          <span
                            className="h-1.5 w-1.5 rounded-full"
                            style={{ backgroundColor: project.accentColor }}
                            aria-hidden="true"
                          />
                          {project.category}
                        </span>
                        <span className="font-mono text-[10px] text-zinc-600">
                          A{idx + 1}
                        </span>
                      </div>

                      <h3 className="mt-1 text-base font-semibold text-white">
                        {project.title}
                      </h3>

                      <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-zinc-400 sm:text-sm">
                        {project.summary}
                      </p>

                      <div className="mt-2.5 flex flex-wrap gap-1.5">
                        {shownStack.map((tech) => (
                          <span
                            key={tech}
                            className="rounded border border-zinc-800 bg-zinc-950 px-2 py-0.5 text-[11px] text-zinc-400"
                          >
                            {tech}
                          </span>
                        ))}
                        {extraCount > 0 && (
                          <span className="rounded border border-zinc-800/80 bg-zinc-950/60 px-2 py-0.5 font-mono text-[11px] text-zinc-500">
                            +{extraCount}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-2 lg:shrink-0 lg:justify-end">
                      {project.image && (
                        <button
                          type="button"
                          onClick={() => {
                            const sIdx = allScreenshots.findIndex((s) => s.src === project.image);
                            setLightboxIndex(sIdx >= 0 ? sIdx : 0);
                          }}
                          className="inline-flex items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-200 transition-colors hover:border-zinc-500 hover:text-white"
                        >
                          <Maximize2 className="h-3 w-3" aria-hidden="true" />
                          <span>Preview UI</span>
                        </button>
                      )}

                      {project.demoId && (
                        <button
                          type="button"
                          onClick={() => setLiveDemoProject({ ...project, id: project.demoId })}
                          className="inline-flex items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-200 transition-colors hover:border-zinc-500 hover:text-white"
                        >
                          <Play className="h-3 w-3 fill-current" aria-hidden="true" />
                          <span>Live Sandbox</span>
                        </button>
                      )}

                      {project.details && (
                        <button
                          type="button"
                          onClick={() => setSelectedDetails(project)}
                          className="inline-flex items-center gap-1 rounded-md border border-zinc-800 bg-zinc-950 px-2.5 py-1.5 text-xs font-medium text-zinc-300 transition-colors hover:border-zinc-600 hover:text-white"
                        >
                          <span>Details</span>
                          <ArrowUpRight className="h-3 w-3 text-zinc-400" aria-hidden="true" />
                        </button>
                      )}

                      {(project.links || [])
                        .filter((l) => isConfiguredLink(l.url))
                        .map((link) => (
                          <a
                            key={link.label}
                            href={link.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 rounded-md border border-zinc-800 bg-zinc-950 px-2.5 py-1.5 text-xs font-medium text-zinc-300 transition-colors hover:border-zinc-600 hover:text-white"
                          >
                            <Github className="h-3 w-3" aria-hidden="true" />
                            <span>{link.label}</span>
                          </a>
                        ))}
                    </div>
                  </article>
                </Reveal>
              );
            })}
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

      <LiveDemoModal project={liveDemoProject} onClose={() => setLiveDemoProject(null)} />

      <ScreenshotLightboxModal
        items={allScreenshots}
        activeIndex={lightboxIndex}
        onNavigate={setLightboxIndex}
        onClose={() => setLightboxIndex(null)}
      />
    </section>
  );
}
