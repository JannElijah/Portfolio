import { ExternalLink } from 'lucide-react';
import { credentialsColumns } from '../data/portfolioData';

function CredentialCard({ column, twoColItems = false }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-[#121215] p-6">
      <h3 className="border-b border-zinc-800 pb-4 text-base font-semibold text-white">
        {column.title}
      </h3>

      <div className={twoColItems ? 'mt-5 grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-2' : 'mt-5 space-y-4'}>
        {column.items.map((item) => (
          <div key={item.heading} className="space-y-0.5">
            <div className="flex items-start justify-between gap-2">
              <h4 className="text-sm font-medium leading-snug text-zinc-100">
                {item.heading}
              </h4>
              {item.certificateUrl && (
                <a
                  href={item.certificateUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  title={`Open ${item.heading}`}
                  className="inline-flex shrink-0 items-center gap-1 rounded border border-zinc-700 bg-zinc-900 px-1.5 py-0.5 text-[10px] font-medium text-zinc-200 transition-colors hover:border-zinc-500 hover:text-white"
                >
                  <span>View</span>
                  <ExternalLink className="h-2.5 w-2.5" aria-hidden="true" />
                </a>
              )}
            </div>
            <p className="text-xs text-zinc-400">{item.meta}</p>
            {item.detail && (
              <p className="pt-0.5 text-xs leading-relaxed text-zinc-400">{item.detail}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Balanced asymmetric Credentials & Education layout avoiding vertical empty voids.
 */
export default function Credentials() {
  const certColumn = credentialsColumns.find((c) => c.id === 'certification');
  const sideColumns = credentialsColumns.filter((c) => c.id !== 'certification');

  return (
    <section id="credentials" className="border-b border-zinc-800/80 bg-[#0D0D10] py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-5 sm:px-8">
        <div className="max-w-xl">
          <h2 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
            Credentials &amp; Education
          </h2>
          <p className="mt-2 text-sm text-zinc-400 sm:text-base">
            Verified technical certifications, seminars, and academic standing.
          </p>
        </div>

        <div className="mt-10 grid grid-cols-1 gap-6 lg:grid-cols-12 lg:items-start">
          {certColumn && (
            <div className="lg:col-span-6">
              <CredentialCard column={certColumn} />
            </div>
          )}

          <div className="space-y-6 lg:col-span-6">
            {sideColumns.map((column) => (
              <CredentialCard key={column.id} column={column} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
