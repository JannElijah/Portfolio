import { useEffect, useMemo, useRef, useState } from 'react';
import {
  ArrowRight,
  Copy,
  FileDown,
  FolderGit2,
  Play,
  Search,
  X,
} from 'lucide-react';
import {
  additionalProjects,
  featuredProjects,
  navItems,
  profileData,
} from '../data/portfolioData';

/**
 * Keyboard-first Command Palette (Ctrl/Cmd + K) for jumping across sandboxes, projects, and actions.
 */
export default function CommandPalette({
  open,
  onClose,
  onOpenProjectDetails,
  onOpenLiveDemo,
  onCopyEmail,
  onSelectSection,
}) {
  const [query, setQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    setQuery('');
    setActiveIndex(0);
    inputRef.current?.focus();
  }, [open]);

  const allItems = useMemo(() => {
    const combinedProjects = [...featuredProjects, ...additionalProjects];

    const sandboxItems = combinedProjects
      .filter((p) => p.demoId)
      .map((p) => ({
        id: `sandbox-${p.id}`,
        group: 'Live Sandboxes',
        label: p.title,
        subtitle: `Interactive browser sandbox · ${p.categoryLabel || p.category}`,
        keywords: `${p.title} ${p.categoryLabel || p.category} ${(p.stack || []).join(' ')} sandbox live`,
        icon: 'sandbox',
        accentColor: p.accentColor,
        action: () => onOpenLiveDemo?.({ ...p, id: p.demoId }),
      }));

    const projectItems = combinedProjects.map((p) => ({
      id: `project-${p.id}`,
      group: 'Projects & Archive',
      label: p.title,
      subtitle: `${p.categoryLabel || p.category} · ${(p.stack || []).slice(0, 3).join(', ')}`,
      keywords: `${p.title} ${p.summary} ${p.categoryLabel || p.category} ${(p.stack || []).join(' ')}`,
      icon: 'project',
      accentColor: p.accentColor,
      action: () => onOpenProjectDetails?.(p),
    }));

    const quickActions = [
      ...profileData.resumeTracks.map((track) => ({
        id: `resume-${track.id}`,
        group: 'Quick Actions',
        label: `Download ${track.label}`,
        subtitle: track.description,
        keywords: `resume pdf cv download ${track.label} ${track.description}`,
        icon: 'resume',
        action: () => window.open(track.url, '_blank', 'noopener,noreferrer'),
      })),
      {
        id: 'action-copy-email',
        group: 'Quick Actions',
        label: `Copy Email (${profileData.email})`,
        subtitle: 'Copy contact email address to clipboard',
        keywords: `email mail contact copy ${profileData.email}`,
        icon: 'copy',
        action: () => onCopyEmail?.(),
      },
      ...navItems.map((item) => ({
        id: `nav-${item.href}`,
        group: 'Quick Actions',
        label: `Jump to ${item.label}`,
        subtitle: `Navigate to ${item.href}`,
        keywords: `jump navigate section ${item.label} ${item.href}`,
        icon: 'section',
        action: () => onSelectSection?.(item.href),
      })),
      {
        id: 'nav-additional-work',
        group: 'Quick Actions',
        label: 'Jump to Engineering Archive',
        subtitle: 'Navigate to #additional-work',
        keywords: 'jump navigate section archive additional work',
        icon: 'section',
        action: () => onSelectSection?.('#additional-work'),
      },
    ];

    return [...sandboxItems, ...projectItems, ...quickActions];
  }, [onCopyEmail, onOpenLiveDemo, onOpenProjectDetails, onSelectSection]);

  const filteredItems = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return allItems;
    return allItems.filter(
      (item) =>
        item.label.toLowerCase().includes(q) ||
        item.subtitle.toLowerCase().includes(q) ||
        item.keywords.toLowerCase().includes(q)
    );
  }, [allItems, query]);

  useEffect(() => {
    setActiveIndex(0);
  }, [query]);

  useEffect(() => {
    if (!open) return undefined;
    const onKeyDown = (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
        return;
      }
      if (!filteredItems.length) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setActiveIndex((prev) => (prev + 1) % filteredItems.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setActiveIndex((prev) => (prev - 1 + filteredItems.length) % filteredItems.length);
      } else if (e.key === 'Enter') {
        const selected = filteredItems[activeIndex];
        if (selected) {
          e.preventDefault();
          onClose();
          selected.action();
        }
      }
    };

    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [activeIndex, filteredItems, onClose, open]);

  if (!open) return null;

  const groupedSections = ['Live Sandboxes', 'Projects & Archive', 'Quick Actions']
    .map((group) => ({
      group,
      items: filteredItems.filter((item) => item.group === group),
    }))
    .filter((sec) => sec.items.length > 0);

  const renderIcon = (item) => {
    if (item.icon === 'sandbox') {
      return <Play className="h-3.5 w-3.5 shrink-0 fill-current text-emerald-400" aria-hidden="true" />;
    }
    if (item.icon === 'project') {
      return (
        <FolderGit2
          className="h-3.5 w-3.5 shrink-0"
          style={{ color: item.accentColor || '#A1A1AA' }}
          aria-hidden="true"
        />
      );
    }
    if (item.icon === 'resume') {
      return <FileDown className="h-3.5 w-3.5 shrink-0 text-sky-400" aria-hidden="true" />;
    }
    if (item.icon === 'copy') {
      return <Copy className="h-3.5 w-3.5 shrink-0 text-zinc-400" aria-hidden="true" />;
    }
    return <ArrowRight className="h-3.5 w-3.5 shrink-0 text-zinc-400" aria-hidden="true" />;
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/80 px-4 pt-16 pb-6 backdrop-blur-sm sm:pt-24"
      role="dialog"
      aria-modal="true"
      aria-label="Quick command palette"
      onClick={onClose}
    >
      <div
        className="animate-modal-in w-full max-w-xl overflow-hidden rounded-xl border border-zinc-700 bg-[#121215] shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 border-b border-zinc-800 px-4 py-3">
          <Search className="h-4 w-4 shrink-0 text-zinc-400" aria-hidden="true" />
          <input
            ref={inputRef}
            autoFocus
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search 18 projects, live sandboxes, skills, or actions..."
            className="w-full bg-transparent text-sm text-white placeholder-zinc-500 focus:outline-none"
          />
          <button
            type="button"
            onClick={onClose}
            aria-label="Close command palette"
            className="rounded border border-zinc-700 p-1 text-zinc-400 transition-colors hover:border-zinc-500 hover:text-white"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="max-h-[60vh] overflow-y-auto p-2">
          {groupedSections.length === 0 ? (
            <p className="px-3 py-8 text-center text-xs text-zinc-400">
              No projects or commands match &ldquo;{query}&rdquo;.
            </p>
          ) : (
            groupedSections.map((section) => (
              <div key={section.group} className="mb-2 last:mb-0">
                <p className="px-2.5 py-1.5 font-mono text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
                  {section.group}
                </p>
                <div className="space-y-0.5">
                  {section.items.map((item) => {
                    const flatIdx = filteredItems.indexOf(item);
                    const isActive = flatIdx === activeIndex;
                    return (
                      <button
                        key={item.id}
                        type="button"
                        onMouseEnter={() => setActiveIndex(flatIdx)}
                        onClick={() => {
                          onClose();
                          item.action();
                        }}
                        className={`flex w-full items-center justify-between gap-3 rounded-lg px-2.5 py-2 text-left transition-colors ${
                          isActive
                            ? 'bg-zinc-800/90 text-white'
                            : 'text-zinc-300 hover:bg-zinc-800/60 hover:text-white'
                        }`}
                      >
                        <div className="flex min-w-0 items-center gap-2.5">
                          {renderIcon(item)}
                          <div className="min-w-0">
                            <p className="truncate text-xs font-semibold">{item.label}</p>
                            <p className="truncate text-[11px] text-zinc-400">{item.subtitle}</p>
                          </div>
                        </div>
                        <span className="shrink-0 font-mono text-[10px] text-zinc-500">
                          {isActive ? 'Enter ↵' : ''}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="flex items-center justify-between border-t border-zinc-800 bg-zinc-950/70 px-4 py-2 font-mono text-[10px] text-zinc-500">
          <span>↑↓ Navigate · ↵ Select · Esc Close</span>
          <span>{filteredItems.length} results</span>
        </div>
      </div>
    </div>
  );
}
