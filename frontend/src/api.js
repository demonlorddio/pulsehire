import axios from 'axios'

// Vite proxy forwards /api/* to http://localhost:8000 (see vite.config.js).
// Use relative URLs so the proxy works in dev and prod without code changes.
const client = axios.create({
  baseURL: '/',
  timeout: 10_000,
})

export async function getTopSkills({ limit = 10, days = 30, source } = {}) {
  const { data } = await client.get('/api/skills/top', {
    params: { limit, days, source },
  })
  return data
}

export async function getSkillTrend({ skill, days = 30 }) {
  const { data } = await client.get('/api/skills/trend', {
    params: { skill, days },
  })
  return data
}

export async function listSkills(category) {
  const { data } = await client.get('/api/skills/list', {
    params: category ? { category } : {},
  })
  return data
}

export async function listJobs({ skill, location, source, limit = 20 } = {}) {
  const { data } = await client.get('/api/jobs', {
    params: { skill, location, source, limit },
  })
  return data
}

export async function listLocations() {
  const { data } = await client.get('/api/locations')
  return data
}

export async function getStats() {
  const { data } = await client.get('/api/stats')
  return data
}

export async function triggerRefresh({ source = 'indeed', query } = {}) {
  const { data } = await client.post('/api/refresh', null, {
    params: { source, query },
  })
  return data
}
