# HCP CRM - Deployment Guide

## Project Structure
```
hcp-crm/
├── frontend/          # Vite + React (deployed on Vercel)
├── backend/           # FastAPI + LangGraph (deployed on Render)
├── Procfile           # Render start command
└── .gitignore
```

## Live URLs
- **Frontend:** https://frontend-phi-ruddy-97.vercel.app
- **Backend:** https://ai-first-crm-hcp-module-6r3o.onrender.com

## Environment Variables

### Vercel (Frontend)
| Variable | Value |
|----------|-------|
| VITE_API_URL | https://ai-first-crm-hcp-module-6r3o.onrender.com/api |

### Render (Backend)
| Variable | Value |
|----------|-------|
| GROQ_API_KEY | (your Groq API key from .env) |

## Deploy Commands

### Frontend (Vercel)
```bash
cd frontend
vercel deploy --prod --yes
```

### Backend (Render)
- Auto-deploys from GitHub main branch
- Build Command: `cd backend && pip install -r requirements.txt`
- Start Command: Handled by Procfile

## Key Files
- `frontend/src/store/hcpSlice.jsx:4` — Backend API URL
- `backend/main.py` — FastAPI server
- `backend/langgraph_agent.py` — AI agent logic
- `backend/.env` — GROQ_API_KEY (not committed to git)

## Notes
- Render free tier sleeps after ~15 min idle (30-60 sec wake-up)
- Vercel auto-deploys on git push to main
- Favicon: `frontend/public/favicon.svg`
