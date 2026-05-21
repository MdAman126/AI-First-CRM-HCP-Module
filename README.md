# HCP CRM - AI-First Healthcare Professional Management System

## Overview

This is an AI-first CRM system for managing Healthcare Professional (HCP) interactions for life science field representatives. It features a **Log Interaction Screen** with both **structured form** and **conversational chat** interfaces powered by a LangGraph AI Agent.

## Tech Stack

- **Frontend**: React 18 + Redux Toolkit + Google Inter Font + Vite
- **Backend**: Python FastAPI
- **AI Agent**: LangGraph with Groq LLM (llama-3.3-70b-versatile)
- **Database**: MySQL/PostgreSQL ready (SQLAlchemy)
- **LLM**: Groq API (gemma2-9b-it compatible)

## Key Features

### 1. Log Interaction Screen
- **Form Mode**: Traditional structured form for logging HCP interactions
- **Chat Mode**: AI-powered conversational interface that understands natural language

### 2. LangGraph AI Agent with 5 Tools

The LangGraph agent provides 5 sales-related tools:

#### Tool 1: log_interaction (Working ✅)
- Captures interaction data: HCP name, specialty, type, topic, notes, outcome, date, time
- Uses LLM for **automatic summarization** of interactions
- Performs **entity extraction** (drugs, locations mentioned)
- Example: "Log a call with Dr. Sarah about cardiology on 22/05/2026 at 11am"

#### Tool 2: edit_interaction (Working ✅)
- Allows modification of logged interaction data
- Can update any field: date, time, notes, outcome, topic, etc.
- Example: "Change the date to 2026-06-15" or "Update notes to new information"

#### Tool 3: search_hcps (Designed ✅)
- Searches Healthcare Professionals by name, specialty, or hospital
- Returns matching HCPs with their details
- Example: "Find all cardiologists" or "Search for Dr. Sarah"

#### Tool 4: get_interaction_summary (Designed ✅)
- Retrieves summary of interactions with specific HCPs
- Can show all interactions or filter by HCP name
- Returns count and list of interactions
- Example: "Show me interactions with Dr. Michael Chen"

#### Tool 5: schedule_followup (Designed ✅)
- Schedules follow-up meetings with HCPs
- Stores follow-up details: HCP name, date, time, purpose, status
- Example: "Schedule follow-up with Dr. Emily on 2026-06-01 at 3pm"

### 3. Conversational AI Features
- Natural language understanding for logging interactions
- Automatic entity extraction from conversation
- Smart date/time parsing (supports multiple formats)
- Context-aware responses

## Project Structure

```
hcp-crm/
├── backend/
│   ├── main.py              # FastAPI application with API endpoints
│   ├── langgraph_agent.py    # LangGraph agent with 5 AI tools
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables (Groq API key)
├── frontend/
│   ├── index.html           # HTML entry point
│   ├── vite.config.js       # Vite configuration
│   ├── package.json         # NPM dependencies
│   └── src/
│       ├── main.jsx         # React entry point
│       ├── App.jsx          # Main React component (Log Interaction Screen)
│       ├── App.css          # Styles with Google Inter font
│       └── store/
│           ├── index.jsx    # Redux store configuration
│           └── hcpSlice.jsx # Redux slice with async thunks
└── README.md                # This file
```

## Setup & Run

### Prerequisites
- Node.js 18+
- Python 3.8+
- Groq API key (get from https://console.groq.com)

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Groq API key
echo "GROQ_API_KEY=your_api_key_here" > .env

# Run the server
python main.py
```

Backend runs at: http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

Frontend runs at: http://localhost:5173

### Running Both (Recommended)

Open **2 separate terminals**:

**Terminal 1 - Backend:**
```bash
cd C:\Users\amanm\hcp-crm\backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd C:\Users\amanm\hcp-crm\frontend
npm run dev
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hcps` | List all Healthcare Professionals |
| GET | `/api/interactions` | Get all logged interactions |
| POST | `/api/interactions/log` | Log new interaction |
| POST | `/api/interactions/edit` | Edit existing interaction |
| POST | `/api/chat` | Chat with AI agent (uses LangGraph) |
| GET | `/api/tools` | List all available AI tools |

## Requirements

- **Frontend**: react, react-dom, react-redux, @reduxjs/toolkit, axios, vite, @vitejs/plugin-react
- **Backend**: fastapi, uvicorn, langgraph, langchain-groq, groq, pydantic, python-dotenv, sqlalchemy, pymysql