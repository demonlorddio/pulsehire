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

// Color palette: emerging = indigo gradient, mature = slate gradient
const COLORS = {
  emerging: ['#818cf8', '#6366f1'],
  mature:   ['#475569', '#334155'],
}

function barFill(skill, index) {
  return skill.is_emerging ? COLORS.emerging[0] : COLORS.mature[index % 2 === 0 ? 0 : 1]
}

function SkeletonLoader() {
  return (
    <div className="space-y-3 py-4">
      {[...Array(8)].map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <div className="skeleton h-4 w-20 rounded" />
          <div className="skeleton h-6 flex-1 rounded-md" style={{ width: `${60 - i * 5}%` }} />
        </div>
      ))}
    </div>
  )
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const data = payload[0].payload
  return (
    <div className="rounded-lg bg-slate-800/95 border border-slate-700/50 backdrop-blur-sm px-3 py-2 shadow-xl">
      <p className="text-sm font-medium text-slate-100">{label}</p>
      <p className="text-xs text-slate-400 mt-0.5">
        <span className="text-indigo-400 font-semibold">{data.count}</span> mentions
        {data.is_emerging && <span className="ml-1.5 text-indigo-300">✨ emerging</span>}
      </p>
      <p className="text-[10px] text-slate-500 mt-0.5">{data.category}</p>
    </div>
  )
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
    return () => { cancelled = true }
  }, [days, source])

  if (loading) return <SkeletonLoader />

  if (error) {
    return (
      <div className="h-80 flex flex-col items-center justify-center gap-2">
        <span className="text-2xl">⚠️</span>
        <span className="text-sm text-rose-400">{error}</span>
      </div>
    )
  }

  if (!data.length) {
    return (
      <div className="h-80 flex flex-col items-center justify-center gap-2">
        <span className="text-2xl">📭</span>
        <span className="text-sm text-slate-500">No data yet. Try refreshing!</span>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={340}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 4, right: 24, left: 4, bottom: 4 }}
        barCategoryGap="20%"
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
        <XAxis
          type="number"
          stroke="#475569"
          tick={{ fontSize: 11, fill: '#94a3b8' }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="skill"
          stroke="#475569"
          tick={{ fontSize: 12, fill: '#cbd5e1' }}
          width={100}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(99, 102, 241, 0.05)' }} />
        <Bar
          dataKey="count"
          radius={[0, 8, 8, 0]}
          animationBegin={0}
          animationDuration={800}
          animationEasing="ease-out"
        >
          {data.map((entry, i) => (
            <Cell
              key={entry.skill_id}
              fill={barFill(entry, i)}
              className="transition-opacity duration-200 hover:opacity-80"
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
