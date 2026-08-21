import { useState, useEffect, useCallback } from 'react'

// Real SVG logo data for tech skills
const SKILL_SVGS = {
  python: '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 6.74 4.64 6.74 4.64l.02 2.5h5.38v.76H5.5S2 7.32 2 12.18c0 4.86 3.12 4.7 3.12 4.7h1.86v-2.24s-.1-3.12 3.08-3.12h5.28s2.98.05 2.98-2.88V5.14S18.36 2 12 2zm-3.12 1.38a1.12 1.12 0 110 2.24 1.12 1.12 0 010-2.24z" fill="#3776AB"/><path d="M12 22c5.52 0 5.26-2.64 5.26-2.64l-.02-2.5h-5.38v-.76H18.5S22 16.68 22 11.82c0-4.86-3.12-4.7-3.12-4.7h-1.86v2.24s.1 3.12-3.08 3.12H8.66s-2.98-.05-2.98 2.88v3.64S5.64 22 12 22z" fill="#FFD43B"/></svg>',
  javascript: '<svg viewBox="0 0 24 24"><rect width="24" height="24" rx="2" fill="#F7DF1E"/><path d="M6.33 17.67c.47.84 1.1 1.48 2.22 1.48.94 0 1.54-.47 1.54-2.18V8.94h2.68v8.07c0 2.73-1.6 3.98-3.92 3.98-2.09 0-3.32-1.09-3.92-2.32l2.4-1zm9.47-.22c.33.74.94 1.3 2.02 1.3 1.04 0 1.7-.52 1.7-2.47v-1.32h-.04c-.38.62-1.1 1.13-2.04 1.13-1.62 0-3.09-1.35-3.09-4.12 0-2.68 1.38-4.3 3.02-4.3.9 0 1.6.44 2.04 1.12h.04V8.94h2.64v8.03c0 2.8-1.66 4.04-3.96 4.04-1.8 0-2.98-.92-3.52-2.12l2.18-.93z" fill="#323330"/></svg>',
  react: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="2.05" fill="#61DAFB"/><ellipse cx="12" cy="12" rx="10" ry="4" stroke="#61DAFB" stroke-width="1" fill="none"/><ellipse cx="12" cy="12" rx="10" ry="4" stroke="#61DAFB" stroke-width="1" fill="none" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4" stroke="#61DAFB" stroke-width="1" fill="none" transform="rotate(120 12 12)"/></svg>',
  java: '<svg viewBox="0 0 24 24"><text x="5" y="18" font-family="serif" font-size="16" font-weight="bold" fill="#E76F00">J</text></svg>',
  typescript: '<svg viewBox="0 0 24 24"><rect width="24" height="24" rx="2" fill="#3178C6"/><path d="M13.65 11.45h-3.3v4.53H8.48V11.45H5.18V9.83h8.47v1.62zm3.73-1.62h3.52v1.55h-3.52v1.7h3.4v1.55h-3.4v2.18h-1.62V8.21h5.02v1.62z" fill="white"/></svg>',
  aws: '<svg viewBox="0 0 24 24"><text x="1" y="17" font-family="Arial" font-size="10" font-weight="bold" fill="#FF9900">AWS</text></svg>',
  docker: '<svg viewBox="0 0 24 24"><rect width="24" height="24" rx="4" fill="#2496ED"/><text x="3" y="17" font-family="Arial" font-size="9" font-weight="bold" fill="white">Dk</text></svg>',
  go: '<svg viewBox="0 0 24 24"><text x="3" y="18" font-family="Arial" font-size="14" font-weight="bold" fill="#00ADD8">Go</text></svg>',
  'c++': '<svg viewBox="0 0 24 24"><rect width="24" height="24" rx="2" fill="#00599C"/><text x="2" y="17" font-family="Arial" font-size="10" font-weight="bold" fill="white">C++</text></svg>',
  rust: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#000" stroke="#DEA584" stroke-width="1.5"/><text x="12" y="16" text-anchor="middle" font-family="Arial" font-size="9" font-weight="bold" fill="#DEA584">Rs</text></svg>',
  sql: '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" fill="#336791"/><text x="12" y="16" text-anchor="middle" font-family="Arial" font-size="8" font-weight="bold" fill="white">SQL</text></svg>',
  'ci/cd': '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#40C463"/><path d="M8 12l3 3 5-6" stroke="white" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}

const SOURCE_COLORS = {
  indeed: '#2164F3',
  linkedin: '#0A66C2',
  glassdoor: '#0CAA41',
}

// Positions across the ENTIRE page (sidebar + main content)
const FULL_PAGE_POSITIONS = [
  // Sidebar
  { x: 5, y: 15, area: 'sidebar', size: 80, rotation: -12 },
  { x: 65, y: 25, area: 'sidebar', size: 70, rotation: 10 },
  { x: 10, y: 55, area: 'sidebar', size: 75, rotation: -5 },
  { x: 70, y: 70, area: 'sidebar', size: 65, rotation: 15 },
  // Main content - scattered
  { x: 20, y: 10, area: 'main', size: 90, rotation: -8 },
  { x: 55, y: 15, area: 'main', size: 85, rotation: 12 },
  { x: 80, y: 8, area: 'main', size: 75, rotation: -15 },
  { x: 15, y: 40, area: 'main', size: 95, rotation: 5 },
  { x: 45, y: 50, area: 'main', size: 80, rotation: -10 },
  { x: 75, y: 35, area: 'main', size: 88, rotation: 8 },
  { x: 30, y: 70, area: 'main', size: 70, rotation: -18 },
  { x: 60, y: 75, area: 'main', size: 82, rotation: 14 },
  { x: 85, y: 60, area: 'main', size: 78, rotation: -6 },
  { x: 10, y: 85, area: 'main', size: 85, rotation: 10 },
  { x: 50, y: 90, area: 'main', size: 72, rotation: -12 },
  { x: 90, y: 85, area: 'main', size: 76, rotation: 7 },
]

let iconId = 0

function SkillLogo({ name, size }) {
  const svg = SKILL_SVGS[name]
  if (!svg) return null
  return (
    <span className="bg-logo" style={{ width: size, height: size }}
      dangerouslySetInnerHTML={{ __html: svg }} />
  )
}

function SourceBadge({ name, size }) {
  const color = SOURCE_COLORS[name]
  if (!color) return null
  const labels = { indeed: 'IN', linkedin: 'in', glassdoor: 'G' }
  return (
    <span className="bg-source-badge" style={{ width: size, height: size, backgroundColor: color }}>
      {labels[name] || name[0].toUpperCase()}
    </span>
  )
}

export default function FloatingParticles() {
  const [skillIcons, setSkillIcons] = useState([])
  const [sourceIcons, setSourceIcons] = useState([])

  const spawnIcons = useCallback((type, key) => {
    const count = 6 + Math.floor(Math.random() * 3)
    // Source icons use offset positions so they don't overlap skill icons
    const offsetPositions = FULL_PAGE_POSITIONS.map(p => ({
      ...p,
      x: (p.x + 12) % 95,
      y: (p.y + 8) % 92,
    }))
    const positions = type === 'source' ? offsetPositions : FULL_PAGE_POSITIONS
    const shuffled = [...positions].sort(() => Math.random() - 0.5).slice(0, count)

    const newIcons = shuffled.map((pos, i) => ({
      id: ++iconId,
      type, key,
      x: pos.x + (Math.random() - 0.5) * 8,
      y: pos.y + (Math.random() - 0.5) * 5,
      size: pos.size + Math.floor(Math.random() * 20 - 10),
      rotation: pos.rotation + Math.floor(Math.random() * 15 - 7),
      opacity: 0.06 + Math.random() * 0.05,  // 6-11% — visible but not hiding content
      delay: i * 100,
    }))

    if (type === 'skill') setSkillIcons(newIcons)
    else setSourceIcons(newIcons)
  }, [])

  useEffect(() => {
    const handler = (e) => {
      const { type, value } = e.detail
      if (type === 'skill' && value) {
        spawnIcons('skill', value)
      } else if (type === 'source' && value && value !== 'all') {
        spawnIcons('source', value)
      }
    }
    window.addEventListener('pulsehire:spawn-particles', handler)
    return () => window.removeEventListener('pulsehire:spawn-particles', handler)
  }, [spawnIcons])

  const allIcons = [...skillIcons, ...sourceIcons]
  if (!allIcons.length) return null

  return (
    <>
      {allIcons.map(icon => (
        <div key={icon.id} className="bg-icon bg-icon-float" style={{
          left: icon.x + '%',
          top: icon.y + '%',
          opacity: icon.opacity,
          transform: 'rotate(' + icon.rotation + 'deg)',
          animationDelay: icon.delay + 'ms',
          position: 'fixed',
          pointerEvents: 'none',
          zIndex: 0,
        }}>
          {icon.type === 'skill'
            ? <SkillLogo name={icon.key} size={icon.size} />
            : <SourceBadge name={icon.key} size={icon.size} />}
        </div>
      ))}
    </>
  )
}
