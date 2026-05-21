from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from langgraph_agent import HCPAgent

app = FastAPI(title="HCP CRM API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

hcp_agent = HCPAgent()

class InteractionRequest(BaseModel):
    hcp_name: Optional[str] = None
    hcp_specialty: Optional[str] = None
    interaction_type: Optional[str] = None
    topic: Optional[str] = None
    notes: Optional[str] = None
    outcome: Optional[str] = None
    date: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

class UpdateInteractionRequest(BaseModel):
    interaction_id: int
    field: str
    value: str

@app.get("/")
async def root():
    return {"message": "HCP CRM API is running"}

@app.get("/api/hcps")
async def get_hcps():
    return {"hcps": [
        {"id": 1, "name": "Dr. Sarah Johnson", "specialty": "Cardiology", "hospital": "City Hospital"},
        {"id": 2, "name": "Dr. Michael Chen", "specialty": "Oncology", "hospital": "General Medical Center"},
        {"id": 3, "name": "Dr. Emily Williams", "specialty": "Neurology", "hospital": "Brain Institute"},
        {"id": 4, "name": "Dr. James Brown", "specialty": "Pediatrics", "hospital": "Children's Hospital"},
        {"id": 5, "name": "Dr. Lisa Anderson", "specialty": "Dermatology", "hospital": "Skin Care Center"}
    ]}

@app.post("/api/interactions/log")
async def log_interaction(request: InteractionRequest):
    print("\n" + "="*50)
    print("RECEIVED DATA FROM FRONTEND:")
    print("="*50)
    print(f"HCP Name: {request.hcp_name}")
    print(f"Specialty: {request.hcp_specialty}")
    print(f"Interaction Type: {request.interaction_type}")
    print(f"Topic: {request.topic}")
    print(f"Notes: {request.notes}")
    print(f"Outcome: {request.outcome}")
    print(f"Date: {request.date}")
    print("="*50 + "\n")
    
    try:
        result = await hcp_agent.log_interaction(
            hcp_name=request.hcp_name,
            hcp_specialty=request.hcp_specialty,
            interaction_type=request.interaction_type,
            topic=request.topic,
            notes=request.notes,
            outcome=request.outcome,
            date=request.date
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interactions")
async def get_interactions():
    return {"interactions": hcp_agent.interactions_db}

@app.post("/api/interactions/edit")
async def edit_interaction(request: UpdateInteractionRequest):
    try:
        result = await hcp_agent.edit_interaction(
            interaction_id=request.interaction_id,
            field=request.field,
            value=request.value
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    print("\n" + "="*50)
    print("CHAT MESSAGE RECEIVED:")
    print("="*50)
    print(f"User Message: {request.message}")
    print(f"History Length: {len(request.history)} messages")
    print("="*50 + "\n")
    
    try:
        result = await hcp_agent.chat(request.message, request.history)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tools")
async def get_tools():
    return {
        "tools": [
            {
                "name": "log_interaction",
                "description": "Log a new interaction with an HCP. Use for recording meeting details, call notes, visit summaries.",
                "parameters": ["hcp_name", "hcp_specialty", "interaction_type", "topic", "notes", "outcome", "date"]
            },
            {
                "name": "edit_interaction",
                "description": "Edit an existing interaction. Use for updating or correcting logged information.",
                "parameters": ["interaction_id", "field", "value"]
            },
            {
                "name": "search_hcps",
                "description": "Search for Healthcare Professionals by name, specialty, or hospital.",
                "parameters": ["query"]
            },
            {
                "name": "get_interaction_summary",
                "description": "Get a summary of interactions with a specific HCP or all HCPs.",
                "parameters": ["hcp_name"]
            },
            {
                "name": "schedule_followup",
                "description": "Schedule a follow-up meeting or call with an HCP.",
                "parameters": ["hcp_name", "date", "time", "purpose"]
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)