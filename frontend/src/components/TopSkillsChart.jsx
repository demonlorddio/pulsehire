import { useEffect, useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { getTopSkills } from '../api'

// Emerging skills get an indigo highlight; mature ones stay neutral.
function colorFor(skill) {
  return skill.is_emerging ? '#818cf8' : '#64748b'
}

export default function TopSkillsChart({ days = 30, source }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    getTopSkills({ limit: 10, days, source })
      .then((rows) => {
        if (!cancelled) setData(rows)
      })
      .catch((e) => {
        if (!cancelled) setError(e.message || 'Failed to load')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [days, source])

  if (loading) {
    return <div className="h-80 flex items-center justify-center text-slate-400">Loading top skills…</div>
  }
  if (error) {
    return <div className="h-80 flex items-center justify-center text-rose-400">⚠ {error}</div>
  }
  if (!data.length) {
    return <div className="h-80 flex items-center justify-center text-slate-500">No data yet.</div>
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={data} layout="vertical" margin={{ top: 8, right: 24, left: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis type="number" stroke="#94a3b8" tick={{ fontSize: 12 }} />
        <YAxis
          type="category"
          dataKey="skill"
          stroke="#94a3b8"
          tick={{ fontSize: 12 }}
          width={110}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#0f172a',
            border: '1px solid #334155',
            borderRadius: 8,
            color: '#e2e8f0',
          }}
          formatter={(value) => [`${value} mentions`, 'Mentions']}
        />
        <Bar dataKey="count" radius={[0, 6, 6, 0]}>
          {data.map((entry) => (
            <Cell key={entry.skill_id} fill={colorFor(entry)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
