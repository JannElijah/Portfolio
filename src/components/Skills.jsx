import { skillColumns } from '../data/portfolioData';

/**
 * Clean editorial 2-column Technical Capabilities overview.
 */
export default function Skills() {
  return (
    <section id="skills" className="border-b border-zinc-800/80 bg-[#09090B] py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-5 sm:px-8">
        <div className="max-w-xl">
          <h2 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
            Technical Capabilities
          </h2>
          <p className="mt-2 text-sm text-zinc-400 sm:text-base">
            Core stacks across full-stack software development and IT systems administration.
          </p>
        </div>

        <div className="mt-10 grid grid-cols-1 gap-8 md:grid-cols-2">
          {skillColumns.map((column) => (
            <div
              key={column.id}
              className="rounded-xl border border-zinc-800 bg-[#111114] p-6 sm:p-7"
            >
              <h3 className="border-b border-zinc-800 pb-4 text-lg font-semibold text-white">
                {column.title}
              </h3>

              <div className="mt-6 space-y-5">
                {column.groups.map((group) => (
                  <div key={group.label}>
                    <h4 className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                      {group.label}
                    </h4>
                    <div className="mt-2.5 flex flex-wrap gap-1.5">
                      {group.items.map((skill) => (
                        <span
                          key={skill}
                          className="rounded border border-zinc-800 bg-zinc-950 px-2.5 py-1 text-xs font-medium text-zinc-200"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
