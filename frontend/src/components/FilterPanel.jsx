import { useEffect, useState } from 'react'
import { listSources } from '../api'

export default function FilterPanel({
  days, onDaysChange,
  source, onSourceChange,
  skill, onSkillChange,
  skills,
}) {
  const [sources, setSources] = useState([])
  useEffect(() => { listSources().then(setSources).catch(() => {}) }, [])

  return (
    <div className="flex flex-wrap gap-5">
      <SelectField
        label="Window"
        value={days}
        onChange={(v) => onDaysChange(Number(v))}
        options={[
          { value: 7, label: '7d' },
          { value: 14, label: '14d' },
          { value: 30, label: '30d' },
          { value: 90, label: '90d' },
        ]}
      />
      <SelectField
        label="Source"
        value={source || ''}
        onChange={(v) => onSourceChange(v || null)}
        options={[
          { value: '', label: 'All' },
          ...sources.map((s) => ({ value: s.slug, label: s.name })),
        ]}
      />
      <SelectField
        label="Skill"
        value={skill || ''}
        onChange={(v) => onSkillChange(v || null)}
        options={[
          { value: '', label: 'None' },
          ...skills.map((s) => ({
            value: s.slug,
            label: s.is_emerging ? `${s.name} *` : s.name,
          })),
        ]}
      />
    </div>
  )
}

function SelectField({ label, value, onChange, options }) {
  return (
    <label className="block">
      <span className="mono-label mb-1.5 block">{label}</span>
      <select
        className="glass-flat rounded-lg px-3 py-2 text-xs text-zinc-300 w-full
                   focus:outline-none focus:ring-1 focus:ring-indigo-400/30
                   hover:border-white/[0.08] transition-colors cursor-pointer
                   appearance-none pr-7
                   bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2210%22%20height%3D%2210%22%20viewBox%3D%220%200%2010%2010%22%3E%3Cpath%20fill%3D%22%2352525b%22%20d%3D%22M5%207L0%202h10z%22%2F%3E%3C%2Fsvg%3E')]
                   bg-[length:10px] bg-[right_10px_center] bg-no-repeat font-mono"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </label>
  )
}
