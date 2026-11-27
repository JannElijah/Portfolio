import {
  CheckSquare,
  Code2,
  Database,
  Layers,
  Network,
  Server,
  ShieldCheck,
  Terminal,
  X,
} from 'lucide-react';
import { additionalProjects, featuredProjects, skillColumns } from '../data/portfolioData';
import { countMatchingProjects } from '../utils/skillMatch';
import Reveal from './Reveal';

const columnIcons = {
  software: Code2,
  systems: Server,
};

const groupIcons = {
  Languages: Terminal,
  'Frameworks & Libraries': Layers,
  'Web Ops, DB & GitHub': Database,
  'Systems, Email & Security': ShieldCheck,
  Networking: Network,
  'QA & Design': CheckSquare,
};

const allProjects = [...featuredProjects, ...additionalProjects];

/**
 * Interactive 2-column Technical Capabilities overview with skill cross-filtering.
 */
export default function Skills({ activeSkill = null, onSelectSkill = null }) {
  return (
    <section id="skills" className="border-b border-zinc-800/80 bg-[#09090B] py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-5 sm:px-8">
        <Reveal className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div className="max-w-xl">
            <p className="font-mono text-[11px] uppercase tracking-widest text-zinc-500">
              03 · Technical Stack
            </p>
            <h2 className="mt-2 text-2xl font-bold tracking-tight text-white sm:text-3xl">
              Technical Capabilities
            </h2>
            <p className="mt-2 text-sm text-zinc-400 sm:text-base">
              Core stacks across full-stack software development and IT systems administration. Click
              any skill badge with a count to filter matching projects.
            </p>
          </div>

          {activeSkill && typeof onSelectSkill === 'function' && (
            <button
              type="button"
              onClick={() => onSelectSkill(activeSkill)}
              className="inline-flex items-center gap-1.5 self-start rounded-full border border-emerald-500/35 bg-emerald-500/10 px-3 py-1.5 text-xs font-medium text-emerald-300 transition-colors hover:border-emerald-400/60 hover:text-white sm:self-auto"
            >
              <span>Filtering by: {activeSkill}</span>
              <X className="h-3.5 w-3.5" aria-hidden="true" />
            </button>
          )}
        </Reveal>

        <div className="mt-10 grid grid-cols-1 gap-6 md:grid-cols-2">
          {skillColumns.map((column, colIdx) => {
            const ColumnIcon = columnIcons[column.id] || Code2;
            return (
              <Reveal
                key={column.id}
                delay={colIdx * 90}
                className="rounded-xl border border-zinc-800 bg-[#111114] p-6 transition-colors duration-200 hover:border-zinc-700 sm:p-7"
              >
                <div className="flex items-center gap-3 border-b border-zinc-800 pb-4">
                  <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-zinc-800 bg-zinc-950 text-zinc-300">
                    <ColumnIcon className="h-4 w-4" aria-hidden="true" />
                  </span>
                  <h3 className="text-lg font-semibold text-white">{column.title}</h3>
                </div>

                <div className="mt-6 space-y-5">
                  {column.groups.map((group) => {
                    const GroupIcon = groupIcons[group.label] || Terminal;
                    return (
                      <div key={group.label}>
                        <h4 className="inline-flex items-center gap-1.5 font-mono text-[11px] font-medium uppercase tracking-wider text-zinc-500">
                          <GroupIcon className="h-3 w-3 text-zinc-500" aria-hidden="true" />
                          <span>{group.label}</span>
                        </h4>
                        <div className="mt-2.5 flex flex-wrap gap-1.5">
                          {group.items.map((skill) => {
                            const matchCount = countMatchingProjects(allProjects, skill);
                            const isInteractive = matchCount > 0 && typeof onSelectSkill === 'function';
                            const isSelected = activeSkill === skill;

                            if (isInteractive) {
                              return (
                                <button
                                  key={skill}
                                  type="button"
                                  aria-pressed={isSelected}
                                  aria-label={`Filter projects by ${skill} (${matchCount} ${matchCount === 1 ? 'project' : 'projects'})`}
                                  onClick={() => onSelectSkill(skill)}
                                  className={`inline-flex items-center gap-1.5 rounded border px-2.5 py-1 text-xs font-medium transition-colors ${
                                    isSelected
                                      ? 'border-emerald-500/50 bg-emerald-500/15 text-emerald-200'
                                      : 'border-zinc-800 bg-zinc-950 text-zinc-200 hover:border-zinc-600 hover:text-white'
                                  }`}
                                >
                                  <span>{skill}</span>
                                  <span
                                    className={`rounded px-1 font-mono text-[10px] ${
                                      isSelected
                                        ? 'bg-emerald-500/20 text-emerald-200'
                                        : 'bg-zinc-900 text-zinc-500'
                                    }`}
                                  >
                                    {matchCount}
                                  </span>
                                </button>
                              );
                            }

                            return (
                              <span
                                key={skill}
                                className="rounded border border-zinc-800 bg-zinc-950 px-2.5 py-1 text-xs font-medium text-zinc-200 transition-colors hover:border-zinc-600 hover:text-white"
                              >
                                {skill}
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
