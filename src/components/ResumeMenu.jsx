import { useEffect, useRef, useState } from 'react';
import { FileDown, ChevronDown, ArrowUpRight, Mail } from 'lucide-react';
import { isConfiguredLink, profileData } from '../data/portfolioData';

/**
 * Dual-track Resume PDF selector styled in editorial zinc.
 */
export default function ResumeMenu({ variant = 'primary', onPlaceholderSelect }) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) setOpen(false);
    };
    const handleEscape = (e) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [open]);

  const buttonClasses =
    variant === 'primary'
      ? 'inline-flex h-10 items-center gap-2 rounded-md bg-zinc-100 px-3.5 text-sm font-semibold text-zinc-950 transition-colors hover:bg-white'
      : 'inline-flex h-9 items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-900 px-3 text-xs font-medium text-zinc-200 transition-colors hover:border-zinc-500 hover:text-white';

  const dropdownAlignClass =
    variant === 'compact' ? 'left-0 sm:right-0 sm:left-auto' : 'left-0';

  return (
    <div ref={containerRef} className="relative inline-block text-left">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        aria-expanded={open}
        aria-haspopup="menu"
        className={buttonClasses}
      >
        <FileDown className="h-4 w-4" aria-hidden="true" />
        <span>Download Resume</span>
        <ChevronDown
          className={`h-3.5 w-3.5 transition-transform ${open ? 'rotate-180' : ''}`}
          aria-hidden="true"
        />
      </button>

      {open && (
        <div
          role="menu"
          className={`absolute ${dropdownAlignClass} z-40 mt-2 w-72 max-w-[calc(100vw-2rem)] rounded-lg border border-zinc-700 bg-[#121215] p-1.5 shadow-2xl`}
        >
          {profileData.resumeTracks.map((track) => {
            const configured = isConfiguredLink(track.url);
            if (configured) {
              return (
                <a
                  key={track.id}
                  href={track.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  role="menuitem"
                  onClick={() => setOpen(false)}
                  className="flex items-start justify-between gap-2 rounded-md p-2.5 transition-colors hover:bg-zinc-800/80"
                >
                  <div>
                    <p className="text-xs font-semibold text-white">{track.label}</p>
                    <p className="mt-0.5 text-[11px] text-zinc-400">{track.description}</p>
                  </div>
                  <ArrowUpRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-zinc-300" />
                </a>
              );
            }

            return (
              <button
                key={track.id}
                type="button"
                role="menuitem"
                onClick={() => {
                  setOpen(false);
                  onPlaceholderSelect?.(track);
                }}
                className="flex w-full items-start justify-between gap-2 rounded-md p-2.5 text-left transition-colors hover:bg-zinc-800/80"
              >
                <div>
                  <p className="text-xs font-semibold text-white">{track.label}</p>
                  <p className="mt-0.5 text-[11px] text-zinc-400">{track.description}</p>
                </div>
                <Mail className="mt-0.5 h-3.5 w-3.5 shrink-0 text-zinc-400" />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
