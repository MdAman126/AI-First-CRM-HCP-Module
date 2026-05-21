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

## Demo Video Instructions

Record a 10-15 minute video demonstrating:

1. **Frontend Walkthrough** (3-4 min)
   - Show the Log Interaction Screen
   - Demonstrate Form Mode: filling and submitting
   - Demonstrate Chat Mode: conversational interaction

2. **All 5 LangGraph Tools Demo** (4-5 min)
   - Tool 1 (log_interaction): "Log a call with Dr. Sarah about cardiology on 22/05/2026 at 11am"
   - Tool 2 (edit_interaction): "Change the date to 2026-06-15"
   - Tool 3 (search_hcps): "Find all cardiologists"
   - Tool 4 (get_interaction_summary): "Show me interactions with Dr. Sarah"
   - Tool 5 (schedule_followup): "Schedule follow-up with Dr. Sarah on 2026-06-01 at 3pm"

3. **Code Structure Explanation** (3-4 min)
   - Show project structure
   - Explain LangGraph agent architecture
   - Show how tools are defined and executed
   - Explain the AI flow (LLM → Tool Executor → Response)

4. **Task Understanding Summary** (1-2 min)
   - Explain what you understood about the AI-first CRM concept
   - Explain the role of LangGraph in managing HCP interactions

## Environment Variables

Create a `.env` file in the backend folder:

```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/hcp_crm
```

## Requirements

- **Frontend**: react, react-dom, react-redux, @reduxjs/toolkit, axios, vite, @vitejs/plugin-react
- **Backend**: fastapi, uvicorn, langgraph, langchain-groq, groq, pydantic, python-dotenv, sqlalchemy, pymysql

## Task Understanding Summary

This project implements an AI-first CRM for Healthcare Professionals with the following key concepts:

1. **Dual Interface**: Users can log interactions via traditional form OR conversational chat
2. **LangGraph Agent**: Orchestrates AI interactions using tools for sales-related activities
3. **LLM Integration**: Uses Groq's LLM for natural language understanding, summarization, and entity extraction
4. **5 Specialized Tools**: log_interaction, edit_interaction, search_hcps, get_interaction_summary, schedule_followup
5. **Field Rep Focus**: Designed to help life science field representatives efficiently manage HCP relationships

The LangGraph agent acts as an intelligent intermediary that:
- Understands natural language from field reps
- Calls appropriate tools based on user intent
- Extracts structured data from conversations
- Provides intelligent responses and confirmations

---

**GitHub Repository**: Upload this code to GitHub and share the link as per your submission requirements.