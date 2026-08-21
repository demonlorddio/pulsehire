import { useEffect, useState } from 'react'
import { listSources } from '../api'
import DarkSelect from './DarkSelect'

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
      <DarkSelect
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
      <DarkSelect
        label="Source"
        value={source || ''}
        onChange={(v, el) => {
          onSourceChange(v || null)
          window.dispatchEvent(new CustomEvent('pulsehire:spawn-particles', {
            detail: { type: 'source', value: v || 'all', element: el }
          }))
        }}
        options={[
          { value: '', label: '🌐 All' },
          ...sources.map((s) => ({ value: s.slug, label: s.name })),
        ]}
      />
      <DarkSelect
        label="Skill"
        value={skill || ''}
        onChange={(v, el) => {
          onSkillChange(v || null)
          if (v) {
            window.dispatchEvent(new CustomEvent('pulsehire:spawn-particles', {
              detail: { type: 'skill', value: v, element: el }
            }))
          }
        }}
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
