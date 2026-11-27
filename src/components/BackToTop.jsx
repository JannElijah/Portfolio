import { useEffect, useState } from 'react';
import { ArrowUp } from 'lucide-react';

/**
 * Minimal floating back-to-top trigger visible after scrolling past the hero fold.
 */
export default function BackToTop() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setVisible(window.scrollY > 480);
    };

    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleClick = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      aria-label="Back to top"
      className={`no-print fixed right-5 bottom-5 z-40 inline-flex h-10 w-10 items-center justify-center rounded-full border border-zinc-700/90 bg-zinc-950/90 text-zinc-200 shadow-xl backdrop-blur-md transition-all duration-300 hover:-translate-y-0.5 hover:border-zinc-500 hover:text-white ${
        visible ? 'translate-y-0 opacity-100' : 'pointer-events-none translate-y-3 opacity-0'
      }`}
    >
      <ArrowUp className="h-4 w-4" aria-hidden="true" />
    </button>
  );
}
