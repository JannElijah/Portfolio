import { useState } from 'react';
import { Github, Linkedin, Mail, MapPin, Copy, Check, ArrowUpRight } from 'lucide-react';
import { isConfiguredLink, profileData } from '../data/portfolioData';
import ResumeMenu from './ResumeMenu';

/**
 * Editorial asymmetric Hero layout without generic SaaS glow blobs or boxed cards.
 */
export default function Hero() {
  const [copiedEmail, setCopiedEmail] = useState(false);
  const [pendingTrack, setPendingTrack] = useState(null);

  const hasGithub = isConfiguredLink(profileData.links.github);
  const hasLinkedin = isConfiguredLink(profileData.links.linkedin);
  const hasAvatar = isConfiguredLink(profileData.avatarUrl);

  const handleCopyEmail = async () => {
    try {
      await navigator.clipboard.writeText(profileData.email);
      setCopiedEmail(true);
      setTimeout(() => setCopiedEmail(false), 2000);
    } catch {
      window.location.href = `mailto:${profileData.email}`;
    }
  };

  return (
    <section id="about" className="relative overflow-hidden border-b border-zinc-800/80 bg-[#09090B]">
      <div
        aria-hidden="true"
        className="bg-grid-subtle pointer-events-none absolute inset-0 opacity-45 [mask-image:radial-gradient(ellipse_at_center,black_25%,transparent_75%)]"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 -top-24 mx-auto h-72 max-w-3xl rounded-full bg-indigo-500/10 blur-3xl"
      />

      <div className="relative mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
        <div className="grid grid-cols-1 gap-12 lg:grid-cols-12 lg:items-end">
          {/* Left 8 Columns: Name, Role & Primary Actions */}
          <div className="lg:col-span-8">
            <div className="animate-fade-up flex items-center gap-4">
              {hasAvatar && (
                <img
                  src={profileData.avatarUrl}
                  alt={profileData.fullName}
                  className="h-14 w-14 rounded-full border border-zinc-700 object-cover"
                />
              )}
              <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/25 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400">
                <span className="relative flex h-2 w-2" aria-hidden="true">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
                </span>
                <span>{profileData.availability}</span>
              </div>
            </div>

            <h1
              style={{ animationDelay: '70ms' }}
              className="animate-fade-up mt-4 text-4xl font-bold tracking-tight text-white sm:text-5xl lg:text-[3.5rem] lg:leading-[1.08]"
            >
              {profileData.fullName}
            </h1>

            <p
              style={{ animationDelay: '130ms' }}
              className="animate-fade-up mt-3 text-lg font-medium text-zinc-300 sm:text-2xl"
            >
              {profileData.headline}
            </p>

            <p
              style={{ animationDelay: '190ms' }}
              className="animate-fade-up mt-5 max-w-2xl text-base leading-relaxed text-zinc-400"
            >
              {profileData.subheadline}
            </p>

            <p
              style={{ animationDelay: '240ms' }}
              className="animate-fade-up mt-3 inline-flex items-center gap-1.5 text-sm text-zinc-400"
            >
              <MapPin className="h-4 w-4 text-zinc-400" aria-hidden="true" />
              <span>
                {profileData.location} · {profileData.workPreference}
              </span>
            </p>

            <div
              style={{ animationDelay: '290ms' }}
              className="animate-fade-up mt-8 flex flex-wrap items-center gap-2.5"
            >
              <ResumeMenu
                variant="primary"
                onPlaceholderSelect={(track) => setPendingTrack(track)}
              />

              <div className="inline-flex h-10 items-center rounded-md border border-zinc-800 bg-[#121215]">
                <a
                  href={`mailto:${profileData.email}`}
                  className="inline-flex h-full items-center gap-2 rounded-l-md px-3 text-sm font-medium text-zinc-200 transition-colors hover:text-white"
                >
                  <Mail className="h-4 w-4 text-zinc-400" aria-hidden="true" />
                  <span>{profileData.email}</span>
                </a>
                <button
                  type="button"
                  onClick={handleCopyEmail}
                  aria-label="Copy email address"
                  className="inline-flex h-full items-center gap-1 rounded-r-md border-l border-zinc-800 px-2.5 text-xs text-zinc-400 transition-colors hover:text-white"
                >
                  {copiedEmail ? (
                    <>
                      <Check className="h-3.5 w-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <Copy className="h-3.5 w-3.5" />
                  )}
                </button>
              </div>

              {hasLinkedin && (
                <a
                  href={profileData.links.linkedin}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex h-10 items-center gap-1.5 rounded-md border border-zinc-800 bg-[#121215] px-3 text-sm font-medium text-zinc-300 transition-colors hover:border-zinc-600 hover:text-white"
                >
                  <Linkedin className="h-4 w-4 text-zinc-400" aria-hidden="true" />
                  <span>LinkedIn</span>
                  <ArrowUpRight className="h-3.5 w-3.5 text-zinc-400" aria-hidden="true" />
                </a>
              )}

              {hasGithub && (
                <a
                  href={profileData.links.github}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex h-10 items-center gap-1.5 rounded-md border border-zinc-800 bg-[#121215] px-3 text-sm font-medium text-zinc-300 transition-colors hover:border-zinc-600 hover:text-white"
                >
                  <Github className="h-4 w-4 text-zinc-400" aria-hidden="true" />
                  <span>GitHub</span>
                  <ArrowUpRight className="h-3.5 w-3.5 text-zinc-400" aria-hidden="true" />
                </a>
              )}
            </div>

            {pendingTrack && (
              <div className="mt-4 flex max-w-xl items-center justify-between gap-4 rounded-md border border-zinc-700 bg-zinc-900 px-4 py-2.5 text-xs text-zinc-300">
                <span>
                  Request <strong>{pendingTrack.label}</strong> via{' '}
                  <a
                    href={`mailto:${profileData.email}?subject=Resume%20Request%20(${encodeURIComponent(
                      pendingTrack.label
                    )})`}
                    className="font-semibold text-white underline"
                  >
                    {profileData.email}
                  </a>
                  .
                </span>
                <button
                  type="button"
                  onClick={() => setPendingTrack(null)}
                  className="text-zinc-400 hover:text-white"
                >
                  Dismiss
                </button>
              </div>
            )}
          </div>

          {/* Right 4 Columns: Clean Editorial Ledger */}
          <div
            style={{ animationDelay: '180ms' }}
            className="animate-fade-up lg:col-span-4"
          >
            <dl className="grid grid-cols-2 gap-3 lg:grid-cols-1">
              {profileData.highlights.map((item) => (
                <div
                  key={item.label}
                  className="rounded-lg border border-zinc-800/90 bg-[#111114]/90 px-4 py-3 transition-colors duration-200 hover:border-zinc-700"
                >
                  <dt className="font-mono text-[10px] font-medium uppercase tracking-widest text-zinc-500">
                    {item.label}
                  </dt>
                  <dd className="mt-1 text-base font-semibold tracking-tight text-white sm:text-lg">
                    {item.value}{' '}
                    <span className="block text-xs font-normal text-zinc-400">{item.detail}</span>
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>
    </section>
  );
}
