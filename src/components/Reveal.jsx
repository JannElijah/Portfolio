import { useEffect, useRef, useState } from 'react';

/**
 * Lightweight GPU-composited scroll-reveal wrapper using IntersectionObserver.
 * Falls back immediately to visible when IntersectionObserver is unavailable (jsdom / SSR).
 */
export default function Reveal({ children, className = '', delay = 0 }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(
    () => typeof window === 'undefined' || typeof IntersectionObserver === 'undefined'
  );

  useEffect(() => {
    if (visible || !ref.current) return undefined;
    const node = ref.current;
    if (node.getBoundingClientRect().top < window.innerHeight * 0.96) {
      setVisible(true);
      return undefined;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setVisible(true);
            observer.unobserve(node);
            break;
          }
        }
      },
      { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [visible]);

  return (
    <div
      ref={ref}
      style={delay ? { transitionDelay: `${delay}ms` } : undefined}
      className={`transform-gpu transition-[opacity,transform] duration-500 ease-out ${
        visible ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'
      } ${className}`}
    >
      {children}
    </div>
  );
}
