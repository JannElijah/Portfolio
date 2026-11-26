import { useState } from 'react';
import {
  Mail,
  Phone,
  MapPin,
  Linkedin,
  Github,
  Copy,
  Check,
  ArrowUpRight,
  MessageSquarePlus,
} from 'lucide-react';
import { isConfiguredLink, profileData } from '../data/portfolioData';
import ResumeMenu from './ResumeMenu';

/**
 * Clean editorial Footer CTA & contact bar with quick OJT inquiry builder.
 */
export default function Footer() {
  const [copied, setCopied] = useState(false);
  const [pendingTrack, setPendingTrack] = useState(null);
  const [inquiryOpen, setInquiryOpen] = useState(false);
  const [roleTrack, setRoleTrack] = useState('Software Dev & QA Intern');
  const [companyName, setCompanyName] = useState('');
  const [noteText, setNoteText] = useState('');
  const [copiedInquiry, setCopiedInquiry] = useState(false);

  const hasGithub = isConfiguredLink(profileData.links.github);
  const hasLinkedin = isConfiguredLink(profileData.links.linkedin);

  const inquirySubject = `OJT Internship Inquiry (${roleTrack})${companyName.trim() ? ` — ${companyName.trim()}` : ''}`;
  const inquiryBody = [
    `Hi Jann,`,
    '',
    `We are reaching out regarding a 500-hour OJT internship opportunity (${roleTrack})${companyName.trim() ? ` at ${companyName.trim()}` : ''}.`,
    noteText.trim() ? `\nDetails: ${noteText.trim()}` : '',
    '',
    'Best regards,',
  ]
    .filter((line) => line !== undefined)
    .join('\n');

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(profileData.email);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      window.location.href = `mailto:${profileData.email}`;
    }
  };

  const handleCopyInquiry = async () => {
    try {
      await navigator.clipboard.writeText(`To: ${profileData.email}\nSubject: ${inquirySubject}\n\n${inquiryBody}`);
      setCopiedInquiry(true);
      setTimeout(() => setCopiedInquiry(false), 2000);
    } catch {
      setCopiedInquiry(false);
    }
  };

  return (
    <footer id="contact" className="bg-[#09090B] py-16">
      <div className="mx-auto max-w-6xl px-5 sm:px-8">
        <div className="rounded-xl border border-zinc-800 bg-[#111114] p-7 sm:p-10">
          <div className="flex flex-col justify-between gap-8 lg:flex-row lg:items-center">
            <div className="max-w-md">
              <h2 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
                Let&apos;s Connect
              </h2>
              <p className="mt-2.5 text-sm leading-relaxed text-zinc-300 sm:text-base">
                Available for a <strong>500-hour OJT internship (2027)</strong> in software
                development, QA, or IT systems operations.
              </p>

              <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-zinc-400">
                <span className="inline-flex items-center gap-1.5">
                  <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
                  {profileData.location}
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <Phone className="h-3.5 w-3.5" aria-hidden="true" />
                  {profileData.phone}
                </span>
              </div>
            </div>

            <div className="flex flex-col gap-2.5 lg:shrink-0 lg:items-end">
              <div className="flex flex-wrap items-center gap-2 lg:flex-nowrap lg:justify-end">
                <div className="inline-flex h-9 items-center rounded-md border border-zinc-700 bg-zinc-100">
                  <a
                    href={`mailto:${profileData.email}`}
                    className="inline-flex h-full items-center gap-2 rounded-l-md px-3 text-xs font-semibold text-zinc-950 transition-colors hover:bg-white sm:text-sm"
                  >
                    <Mail className="h-3.5 w-3.5" aria-hidden="true" />
                    <span>{profileData.email}</span>
                  </a>
                  <button
                    type="button"
                    onClick={handleCopy}
                    className="inline-flex h-full items-center gap-1 rounded-r-md border-l border-zinc-300 bg-zinc-200/80 px-2.5 text-xs font-medium text-zinc-800 hover:bg-white"
                  >
                    {copied ? (
                      <>
                        <Check className="h-3 w-3 text-emerald-700" />
                        <span className="text-emerald-700">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="h-3 w-3" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>

                {hasLinkedin && (
                  <a
                    href={profileData.links.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex h-9 items-center gap-1.5 rounded-md border border-zinc-800 bg-zinc-950 px-3 text-xs font-medium text-zinc-300 hover:border-zinc-600 hover:text-white"
                  >
                    <Linkedin className="h-3.5 w-3.5" />
                    <span>LinkedIn</span>
                    <ArrowUpRight className="h-3 w-3 text-zinc-400" />
                  </a>
                )}

                {hasGithub && (
                  <a
                    href={profileData.links.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex h-9 items-center gap-1.5 rounded-md border border-zinc-800 bg-zinc-950 px-3 text-xs font-medium text-zinc-300 hover:border-zinc-600 hover:text-white"
                  >
                    <Github className="h-3.5 w-3.5" />
                    <span>GitHub</span>
                    <ArrowUpRight className="h-3 w-3 text-zinc-400" />
                  </a>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-2 lg:justify-end">
                <ResumeMenu
                  variant="compact"
                  onPlaceholderSelect={(track) => setPendingTrack(track)}
                />

                <button
                  type="button"
                  onClick={() => setInquiryOpen((prev) => !prev)}
                  className="inline-flex h-9 items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-900 px-3 text-xs font-medium text-zinc-200 hover:border-zinc-500 hover:text-white"
                >
                  <MessageSquarePlus className="h-3.5 w-3.5" aria-hidden="true" />
                  <span>{inquiryOpen ? 'Hide Inquiry' : 'Draft OJT Inquiry'}</span>
                </button>
              </div>

              {pendingTrack && (
                <p className="text-xs text-zinc-400">
                  Request <strong>{pendingTrack.label}</strong> via {profileData.email}
                </p>
              )}
            </div>
          </div>

          {inquiryOpen && (
            <div className="mt-6 border-t border-zinc-800 pt-6">
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                <label className="block text-xs">
                  <span className="text-zinc-400">Target Track</span>
                  <select
                    value={roleTrack}
                    onChange={(e) => setRoleTrack(e.target.value)}
                    className="mt-1 w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-xs text-zinc-100"
                  >
                    <option value="Software Dev & QA Intern">Software Dev &amp; QA Intern</option>
                    <option value="IT Support & Network Intern">IT Support &amp; Network Intern</option>
                    <option value="Hardware & QA Validation Intern">Hardware &amp; QA Validation Intern</option>
                  </select>
                </label>

                <label className="block text-xs">
                  <span className="text-zinc-400">Company / Team</span>
                  <input
                    type="text"
                    placeholder="e.g. Microchip Alabang"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="mt-1 w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-xs text-zinc-100 placeholder:text-zinc-600"
                  />
                </label>

                <label className="block text-xs">
                  <span className="text-zinc-400">Schedule or Note (Optional)</span>
                  <input
                    type="text"
                    placeholder="e.g. Onsite interview window"
                    value={noteText}
                    onChange={(e) => setNoteText(e.target.value)}
                    className="mt-1 w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-xs text-zinc-100 placeholder:text-zinc-600"
                  />
                </label>
              </div>

              <div className="mt-3 flex flex-wrap items-center gap-2.5">
                <a
                  href={`mailto:${profileData.email}?subject=${encodeURIComponent(inquirySubject)}&body=${encodeURIComponent(inquiryBody)}`}
                  className="inline-flex items-center gap-1.5 rounded-md bg-zinc-100 px-3.5 py-2 text-xs font-semibold text-zinc-950 hover:bg-white"
                >
                  <Mail className="h-3.5 w-3.5" />
                  <span>Open in Email App</span>
                </a>
                <button
                  type="button"
                  onClick={handleCopyInquiry}
                  className="inline-flex items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-900 px-3.5 py-2 text-xs font-medium text-zinc-200 hover:border-zinc-500 hover:text-white"
                >
                  {copiedInquiry ? (
                    <>
                      <Check className="h-3.5 w-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied Draft</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3.5 w-3.5" />
                      <span>Copy Inquiry Message</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        <p className="mt-8 text-center text-xs text-zinc-500">
          © {new Date().getFullYear()} {profileData.fullName}
        </p>
      </div>
    </footer>
  );
}
