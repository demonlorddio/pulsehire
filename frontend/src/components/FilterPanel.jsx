import { useEffect, useState } from 'react'
import { listSources } from '../api'

export default function FilterPanel({
  days,
  onDaysChange,
  source,
  onSourceChange,
  skill,
  onSkillChange,
  skills,
}) {
  const [sources, setSources] = useState([])
  useEffect(() => {
    listSources().then(setSources).catch(() => {})
  }, [])

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <SelectField
        icon="📅"
        label="Time Window"
        value={days}
        onChange={(v) => onDaysChange(Number(v))}
        options={[
          { value: 7, label: 'Last 7 days' },
          { value: 14, label: 'Last 14 days' },
          { value: 30, label: 'Last 30 days' },
          { value: 90, label: 'Last 90 days' },
        ]}
      />
      <SelectField
        icon="🌐"
        label="Source"
        value={source || ''}
        onChange={(v) => onSourceChange(v || null)}
        options={[
          { value: '', label: 'All sources' },
          ...sources.map((s) => ({ value: s.slug, label: s.name })),
        ]}
      />
      <SelectField
        icon="🎯"
        label="Skill (for trend)"
        value={skill || ''}
        onChange={(v) => onSkillChange(v || null)}
        options={[
          { value: '', label: 'Select a skill…' },
          ...skills.map((s) => ({
            value: s.slug,
            label: `${s.name}${s.is_emerging ? '  ✨' : ''}`,
          })),
        ]}
      />
    </div>
  )
}

function SelectField({ icon, label, value, onChange, options }) {
  return (
    <label className="block group">
      <span className="flex items-center gap-1.5 text-[11px] uppercase tracking-widest text-slate-500 font-medium mb-1.5">
        <span className="text-xs">{icon}</span>
        {label}
      </span>
      <select
        className="w-full rounded-xl bg-slate-800/80 border border-slate-700/50 px-3 py-2.5 text-sm text-slate-200 
                   focus:outline-none focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500/40
                   hover:border-slate-600 transition-colors duration-200
                   appearance-none cursor-pointer
                   bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2012%2012%22%3E%3Cpath%20fill%3D%22%2364748b%22%20d%3D%22M6%208L1%203h10z%22%2F%3E%3C%2Fsvg%3E')]
                   bg-[length:12px] bg-[right_12px_center] bg-no-repeat pr-8"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </label>
  )
}
