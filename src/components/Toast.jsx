import { CheckCircle2, X } from 'lucide-react';

/**
 * Subtle floating toast notification for clipboard & quick filter actions.
 */
export default function Toast({ message, onDismiss }) {
  if (!message) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className="no-print animate-modal-in fixed bottom-5 left-1/2 z-[60] flex max-w-[calc(100vw-2rem)] -translate-x-1/2 items-center gap-2.5 rounded-full border border-zinc-700/90 bg-zinc-950/95 px-4 py-2 text-xs font-medium text-zinc-100 shadow-2xl backdrop-blur-md"
    >
      <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-emerald-400" aria-hidden="true" />
      <span className="truncate">{message}</span>
      {typeof onDismiss === 'function' && (
        <button
          type="button"
          onClick={onDismiss}
          aria-label="Dismiss notification"
          className="rounded-full p-0.5 text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-white"
        >
          <X className="h-3 w-3" />
        </button>
      )}
    </div>
  );
}
