# PulseHire — Dev Server Run Doc

## Prerequisites
- Node.js installed
- `frontend/node_modules` already installed (if not: `cd frontend && npm install`)
- Backend running on port 8000 (if not: `cd backend && ../venv/Scripts/python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`)

## Start Frontend Dev Server
```bash
cd "C:\Users\dell\Documents\scraper project\frontend"
npm run dev
```
Default port: 5173 (Vite). Vite proxies `/api/*` to `http://localhost:8000`.

## Detached (Windows)
```powershell
powershell -NoProfile -Command "(Start-Process -FilePath 'npm.cmd' -ArgumentList 'run','dev' -WorkingDirectory 'C:\Users\dell\Documents\scraper project\frontend' -RedirectStandardOutput '<log>' -RedirectStandardError '<log>.err' -WindowStyle Hidden -PassThru).Id"
```

## URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
