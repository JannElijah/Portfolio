import { useEffect, useState } from 'react';
import { Menu, X } from 'lucide-react';
import { navItems, profileData } from '../data/portfolioData';

/**
 * Minimal architectural top navigation bar.
 */
export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [activeId, setActiveId] = useState('about');

  useEffect(() => {
    const sections = navItems
      .map((item) => ({
        id: item.href.replace('#', ''),
        el: document.getElementById(item.href.replace('#', '')),
      }))
      .filter((s) => s.el);

    if (!sections.length) return undefined;

    let frameId = null;
    const updateActive = () => {
      frameId = null;
      if (window.scrollY < 40) {
        setActiveId(sections[0].id);
        return;
      }
      const docEl = document.documentElement;
      if (
        docEl.scrollHeight > window.innerHeight &&
        window.innerHeight + window.scrollY >= docEl.scrollHeight - 24
      ) {
        setActiveId('contact');
        return;
      }

      const probeY = window.scrollY + 130;
      let current = sections[0].id;
      for (const sec of sections) {
        if (sec.el.offsetTop <= probeY) {
          current = sec.id;
        }
      }
      setActiveId(current);
    };

    const onScroll = () => {
      if (frameId === null) {
        frameId = window.requestAnimationFrame(updateActive);
      }
    };

    updateActive();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
      if (frameId !== null) window.cancelAnimationFrame(frameId);
    };
  }, []);

  return (
    <header className="sticky top-0 z-50 border-b border-zinc-800/80 bg-[#09090B]/90 backdrop-blur-md">
      <a
        href="#projects"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-4 focus:z-50 focus:rounded-md focus:bg-zinc-100 focus:px-3 focus:py-1.5 focus:text-xs focus:font-semibold focus:text-zinc-950"
      >
        Skip to projects
      </a>
      <div className="mx-auto flex h-15 max-w-6xl items-center justify-between px-5 sm:px-8">
        <a
          href="#about"
          className="text-sm font-semibold tracking-tight text-zinc-100 transition-colors hover:text-white"
        >
          {profileData.fullName}
        </a>

        <nav className="hidden items-center gap-7 md:flex" aria-label="Primary Navigation">
          {navItems.map((item) => {
            const isActive = activeId === item.href.replace('#', '');
            return (
              <a
                key={item.href}
                href={item.href}
                className={`text-sm transition-colors ${
                  isActive ? 'font-medium text-white' : 'text-zinc-400 hover:text-zinc-200'
                }`}
              >
                {item.label}
              </a>
            );
          })}
        </nav>

        <a
          href={`mailto:${profileData.email}`}
          className="hidden rounded-md border border-zinc-700 bg-zinc-900 px-3.5 py-1.5 text-xs font-medium text-zinc-100 transition-colors hover:border-zinc-500 hover:bg-zinc-800 md:inline-flex"
        >
          Get in Touch
        </a>

        <button
          type="button"
          onClick={() => setMobileOpen((prev) => !prev)}
          aria-expanded={mobileOpen}
          aria-label="Toggle navigation menu"
          className="rounded-md border border-zinc-800 p-2 text-zinc-300 hover:text-white md:hidden"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {mobileOpen && (
        <div className="border-t border-zinc-800 bg-[#09090B] px-5 py-4 md:hidden">
          <nav className="flex flex-col gap-2" aria-label="Mobile Navigation">
            {navItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className="rounded px-2 py-1.5 text-sm font-medium text-zinc-300 hover:text-white"
              >
                {item.label}
              </a>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
