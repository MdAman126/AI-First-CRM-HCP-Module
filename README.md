# HCP CRM - AI-First Healthcare Professional Management System

## Overview

An AI-first CRM for life science field representatives to manage Healthcare Professional (HCP) interactions. Features a dual-mode **Log Interaction Screen** with both a structured form and an AI-powered conversational chat interface. The LangGraph agent processes natural language, auto-fills the form, executes tools (logging, editing, searching, summarizing, scheduling), and displays results in real-time.

## Tech Stack

- **Frontend**: React 18 + Redux Toolkit + Vite
- **Backend**: Python FastAPI + Uvicorn
- **AI Agent**: LangGraph (StateGraph) with Groq LLM (`llama-3.3-70b-versatile`)
- **Database**: MySQL/PostgreSQL via SQLAlchemy (schema-ready)
- **Styling**: Google Inter font, glass-morphism UI

## Architecture

### LangGraph Agent Flow

```
User Message → [llm_node] → JSON (tool_calls + response) → [tool_executor] → Result + Response
```

The agent uses a **2-node StateGraph**:
1. **llm_node**: Receives chat history + system prompt, invokes Groq LLM, and extracts tool calls and response text from JSON output
2. **tool_executor**: Iterates through requested tool calls, executes corresponding tools (`log_interaction`, `edit_interaction`, `search_hcps`, `get_interaction_summary`, `schedule_followup`), and attaches results

The graph is compiled with `llm_node → tool_executor → END`.

### Frontend Architecture (Redux)

```
App.jsx
├── dispatch(fetchHCPs) on mount → populates HCP dropdown
├── dispatch(fetchInteractions) → updates interactions list
├── dispatch(sendChat) → POST /api/chat → updates chatHistory + formData
├── dispatch(logInteraction) → POST /api/interactions/log
├── Local state: chatHistory, formData, searchResults, interactionSummary, followups
└── Scroll behavior: chat container scrolls internally, header is sticky
```

### AI Auto-Fill Mechanism

When a user provides at least **hcp_name + date + time** in chat, the agent automatically calls `log_interaction` and the frontend fills the form with the extracted data. Missing optional fields receive sensible defaults:
- `interaction_type` → "Call"
- `outcome` → "Positive"
- `topic` → "General Discussion"
- `notes` → "Discussed healthcare topics"

## UI Layout

- **Sticky header**: Glass-effect background (opacity 0.85 + blur), stays fixed on scroll
- **Left panel** (scrollable): Form, recent interactions, search results, interaction summaries, follow-ups
- **Right panel** (scrolls independently): Chat messages with auto-scroll to bottom
- Only the chat area scrolls internally — no full-page scrolling

## Key Features

### 1. Dual-Mode Interaction Screen
- **Form Mode**: Dropdowns for HCP name, interaction type, outcome; text inputs for specialty, topic, notes; date/time pickers
- **Chat Mode**: Free-text input, processed by LangGraph agent, results auto-fill the form below

### 2. 5 LangGraph AI Tools

| # | Tool | What It Does | Chat Example |
|---|------|-------------|--------------|
| 1 | `log_interaction` | Records HCP interaction with AI summarization + entity extraction | *"Log a call with Dr. Sarah about cardiology on 22/05/2026 at 11am"* |
| 2 | `edit_interaction` | Modifies any field of a logged interaction | *"Change the date to 2026-06-15"* |
| 3 | `search_hcps` | Searches HCPs by name, specialty, or hospital; results accumulate with dedup | *"Find all cardiologists"* |
| 4 | `get_interaction_summary` | Retrieves interaction history for an HCP; dedup on successive calls | *"Show me interactions with Dr. Sarah"* |
| 5 | `schedule_followup` | Schedules follow-up meetings; stored with status tracking | *"Schedule follow-up with Dr. Sarah on 2026-06-01 at 3pm"* |

### 3. Smart Date/Time Parsing
Handles multiple formats: `22/05/2026` → `2026-05-22`, `5pm` → `17:00`, `11am` → `11:00`. All dates normalized to ISO format.

## Project Structure

```
hcp-crm/
├── backend/
│   ├── main.py                # FastAPI server (routes: /api/hcps, /api/chat, etc.)
│   ├── langgraph_agent.py      # HCPAgent class: StateGraph, 5 tools, LLM summarization
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # GROQ_API_KEY (not committed)
├── frontend/
│   ├── index.html              # HTML entry
│   ├── vite.config.js          # Vite config with React plugin
│   ├── package.json            # NPM dependencies
│   └── src/
│       ├── main.jsx            # React DOM render entry
│       ├── App.jsx             # Main component: form + chat + results panels
│       ├── App.css             # All styles: glass header, scroll containers, form layout
│       └── store/
│           ├── index.jsx       # Redux store (configureStore)
│           └── hcpSlice.jsx    # Redux slice: fetchHCPs, fetchInteractions, logInteraction, sendChat
└── README.md
```

## Setup & Run

### Prerequisites
- Node.js 18+
- Python 3.8+
- Groq API key (sign up at https://console.groq.com)

### Backend

```bash
cd backend
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
python main.py
```

Backend → http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend → http://localhost:5173

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hcps` | List all 5 sample HCPs |
| GET | `/api/interactions` | Get all logged interactions |
| POST | `/api/interactions/log` | Log a new interaction |
| POST | `/api/interactions/edit` | Edit an interaction field |
| POST | `/api/chat` | Chat with LangGraph agent |
| GET | `/api/tools` | List available tools with parameters |

## Requirements

- **Frontend**: react, react-dom, react-redux, @reduxjs/toolkit, axios, vite, @vitejs/plugin-react
- **Backend**: fastapi, uvicorn, langgraph, langchain-groq, groq, pydantic, python-dotenv, sqlalchemy, pymysql