export default function FilterPanel({
  days,
  onDaysChange,
  source,
  onSourceChange,
  skill,
  onSkillChange,
  skills,
}) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <label className="block">
        <span className="text-xs uppercase tracking-wide text-slate-400">Time window</span>
        <select
          className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          value={days}
          onChange={(e) => onDaysChange(Number(e.target.value))}
        >
          <option value={7}>Last 7 days</option>
          <option value={14}>Last 14 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </label>

      <label className="block">
        <span className="text-xs uppercase tracking-wide text-slate-400">Source</span>
        <select
          className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          value={source || ''}
          onChange={(e) => onSourceChange(e.target.value || null)}
        >
          <option value="">All sources</option>
          <option value="indeed">Indeed</option>
          <option value="naukri">Naukri</option>
        </select>
      </label>

      <label className="block">
        <span className="text-xs uppercase tracking-wide text-slate-400">Skill (for trend)</span>
        <select
          className="mt-1 w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          value={skill || ''}
          onChange={(e) => onSkillChange(e.target.value || null)}
        >
          <option value="">Select a skill…</option>
          {skills.map((s) => (
            <option key={s.id} value={s.slug}>
              {s.name}{s.is_emerging ? '  ✨' : ''}
            </option>
          ))}
        </select>
      </label>
    </div>
  )
}
