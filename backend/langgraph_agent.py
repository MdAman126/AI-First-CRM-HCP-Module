from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from typing import TypedDict, Annotated, List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import json

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[List, "messages"]
    tool_calls: Annotated[List, "tool_calls"]
    tool_results: Annotated[List, "tool_results"]
    final_response: Annotated[Optional[str], "final_response"]

class HCPAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY", "gsk_your_key_here"),
            temperature=0.7
        )
        self.interactions_db = []
        self.interaction_id_counter = 1
        self.hcps_db = [
            {"id": 1, "name": "Dr. Sarah Johnson", "specialty": "Cardiology", "hospital": "City Hospital", "phone": "555-0101", "email": "sarah.johnson@hospital.com"},
            {"id": 2, "name": "Dr. Michael Chen", "specialty": "Oncology", "hospital": "General Medical Center", "phone": "555-0102", "email": "michael.chen@hospital.com"},
            {"id": 3, "name": "Dr. Emily Williams", "specialty": "Neurology", "hospital": "Brain Institute", "phone": "555-0103", "email": "emily.williams@hospital.com"},
            {"id": 4, "name": "Dr. James Brown", "specialty": "Pediatrics", "hospital": "Children's Hospital", "phone": "555-0104", "email": "james.brown@hospital.com"},
            {"id": 5, "name": "Dr. Lisa Anderson", "specialty": "Dermatology", "hospital": "Skin Care Center", "phone": "555-0105", "email": "lisa.anderson@hospital.com"}
        ]
        self.followups = []
        
        self.graph = StateGraph(AgentState)
        self.graph.add_node("llm_node", self.llm_node)
        self.graph.add_node("tool_executor", self.tool_executor)
        self.graph.set_entry_point("llm_node")
        self.graph.add_edge("llm_node", "tool_executor")
        self.graph.add_edge("tool_executor", END)
        
        self.compiled_graph = self.graph.compile()

    async def llm_node(self, state: AgentState) -> AgentState:
        messages = state["messages"]
        
        system_prompt = """You are an AI assistant for a Healthcare CRM system. You help field representatives manage Healthcare Professional (HCP) interactions.

You MUST return a JSON object with two keys: "tool_calls" and "response". 
- If you call a tool, put it in "tool_calls" array and a confirmation message in "response"
- If no tool needed, leave "tool_calls" empty and put your response in "response"

YOUR 5 TOOLS:

1. log_interaction - Use when user wants to RECORD/LOG/SAVE an interaction with a doctor
   Required: hcp_name, date, time
   Optional: hcp_specialty, interaction_type, topic, notes, outcome
   AUTO-FILL: If user provides at least hcp_name + date + time, call this tool. 
   The form will auto-fill with what they provided. For missing optional fields, 
   use reasonable defaults: interaction_type="Call", outcome="Positive", 
   topic="General Discussion", notes="Discussed healthcare topics"
   
2. edit_interaction - Use when user wants to CHANGE/UPDATE/MODIFY a logged interaction
   Parameters: interaction_id, field, value
   
3. search_hcps - Use when user wants to FIND/SEARCH/LOOK UP doctors/HCPs
   
4. get_interaction_summary - Use when user wants to SEE/VIEW/SHOW interaction history
   
5. schedule_followup - Use when user wants to SCHEDULE/SET UP a follow-up meeting

CRITICAL RULES:
- Greetings: "hi", "hello", "hey", "how are you" → NO tool, just respond
- log_interaction: ONLY requires hcp_name, date, and time. If all 3 are present, call the tool!
- Missing optional fields: Use defaults, do NOT ask. The form will auto-fill with defaults.
- Auto-fill principle: If user provides enough to identify the interaction (at least name+date+time), 
  call log_interaction immediately. The form will handle missing fields with defaults.

DATE FORMAT: YYYY-MM-DD (convert from "25/05/2026" → "2026-05-25")
TIME FORMAT: HH:MM (convert "5pm" → "17:00", "11am" → "11:00")

EXAMPLES:

User: "I want to meet with Dr. Lisa Anderson on date 25/05/2026 at 5pm"
→ Call log_interaction with:
  hcp_name="Dr. Lisa Anderson"
  date="2026-05-25"
  time="17:00"
  hcp_specialty="Dermatology" (default)
  interaction_type="Visit" (default)
  topic="General Discussion" (default)
  notes="Discussed healthcare topics" (default)
  outcome="Positive" (default)
→ Response: "I've logged a visit with Dr. Lisa Anderson on May 25th at 5:00 PM. 
   The form has been auto-filled. You can adjust any fields before submitting!"

User: "Log a call with Dr. Sarah on 22/05/2026 at 11am"
→ Call log_interaction immediately with all fields
→ Response: "Logged! I've recorded a call with Dr. Sarah on May 22nd at 11:00 AM."

User: "Schedule meeting with Dr. Michael on June 10"
→ Call log_interaction with: hcp_name="Dr. Michael Chen", date="2026-06-10", time="10:00"
→ Response: "I've logged a meeting with Dr. Michael Chen on June 10th at 10:00 AM."

User: "Find all cardiologists"
→ {"tool_calls": [{"name": "search_hcps", "parameters": {"query": "cardiology"}}], "response": "Searching for cardiologists..."}

User: "Show me interactions with Dr. Sarah"
→ {"tool_calls": [{"name": "get_interaction_summary", "parameters": {"hcp_name": "Dr. Sarah Johnson"}}], "response": "Looking up interactions with Dr. Sarah Johnson..."}

User: "Schedule follow-up with Dr. Sarah on 2026-06-01 at 3pm"
→ {"tool_calls": [{"name": "schedule_followup", "parameters": {"hcp_name": "Dr. Sarah Johnson", "date": "2026-06-01", "time": "15:00", "purpose": "Follow-up meeting"}}], "response": "Scheduled! Follow-up with Dr. Sarah Johnson on June 1st, 2026 at 3:00 PM."}

User: "Change the date to 2026-06-15"
→ {"tool_calls": [{"name": "edit_interaction", "parameters": {"field": "date", "value": "2026-06-15"}}], "response": "Updated! I've changed the date to June 15th, 2026."}

User: "Hello"
→ {"tool_calls": [], "response": "Hello! I can help you log HCP interactions, search doctors, or schedule follow-ups. What would you like to do?"}"""

        all_messages = [("system", system_prompt)] + [(m["role"], m["content"]) for m in messages]
        
        response = self.llm.invoke(all_messages)
        
        try:
            result = json.loads(response.content)
            tool_calls = result.get("tool_calls", [])
            final_response = result.get("response", "")
        except:
            tool_calls = []
            final_response = response.content
        
        return {
            "messages": state["messages"],
            "tool_calls": tool_calls,
            "tool_results": [],
            "final_response": final_response
        }

    async def tool_executor(self, state: AgentState) -> AgentState:
        tool_results = []
        
        for tool_call in state.get("tool_calls", []):
            tool_name = tool_call.get("name")
            params = tool_call.get("parameters", {})
            
            if tool_name == "log_interaction":
                result = await self.tool_log_interaction(params)
            elif tool_name == "edit_interaction":
                result = await self.tool_edit_interaction(params)
            elif tool_name == "search_hcps":
                result = self.tool_search_hcps(params)
            elif tool_name == "get_interaction_summary":
                result = self.tool_get_interaction_summary(params)
            elif tool_name == "schedule_followup":
                result = await self.tool_schedule_followup(params)
            else:
                result = {"error": f"Unknown tool: {tool_name}", "success": False}
            
            tool_results.append({"tool": tool_name, "result": result})
        
        return {
            "messages": state["messages"],
            "tool_calls": state["tool_calls"],
            "tool_results": tool_results,
            "final_response": state["final_response"]
        }

    async def tool_log_interaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        hcp_name = params.get("hcp_name", "Unknown")
        hcp_specialty = params.get("hcp_specialty", "General")
        interaction_type = params.get("interaction_type", "Call")
        topic = params.get("topic", "General Discussion")
        notes = params.get("notes", "")
        outcome = params.get("outcome", "Pending")
        date = params.get("date", "")
        time = params.get("time", "")
        
        if not date or not time:
            return {
                "success": False,
                "error": "Date and time are required"
            }
        
        summary = await self.summarize_interaction(notes, topic)
        
        interaction = {
            "id": self.interaction_id_counter,
            "hcp_name": hcp_name,
            "hcp_specialty": hcp_specialty,
            "interaction_type": interaction_type,
            "topic": topic,
            "notes": notes,
            "outcome": outcome,
            "date": date,
            "time": time,
            "summary": summary,
            "entities": self.extract_entities(notes)
        }
        
        self.interactions_db.append(interaction)
        self.interaction_id_counter += 1
        
        return {
            "success": True,
            "message": f"Interaction logged successfully",
            "interaction_id": interaction["id"],
            "summary": summary,
            "hcp_name": hcp_name,
            "hcp_specialty": hcp_specialty,
            "interaction_type": interaction_type,
            "topic": topic,
            "notes": notes,
            "outcome": outcome,
            "date": date,
            "time": time
        }

    async def tool_edit_interaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        interaction_id = params.get("interaction_id")
        field = params.get("field")
        value = params.get("value")
        
        if not interaction_id and self.interactions_db:
            interaction_id = self.interactions_db[-1]["id"]
        
        if not interaction_id:
            return {
                "success": False,
                "error": "No interactions found to edit"
            }
        
        for interaction in self.interactions_db:
            if interaction["id"] == interaction_id:
                interaction[field] = value
                return {
                    "success": True,
                    "message": f"Updated interaction #{interaction_id}",
                    "field": field,
                    "value": value,
                    "updated_field": field,
                    "new_value": value
                }
        
        return {
            "success": False,
            "error": f"Interaction #{interaction_id} not found"
        }

    def tool_search_hcps(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "").lower()
        
        if not query:
            return {
                "success": True,
                "count": 0,
                "hcps": [],
                "message": "Please provide a search query"
            }
        
        results = [
            hcp for hcp in self.hcps_db
            if query in hcp["name"].lower()
            or query in hcp["specialty"].lower()
            or query in hcp["hospital"].lower()
        ]
        
        return {
            "success": True,
            "count": len(results),
            "hcps": results,
            "message": f"Found {len(results)} HCP(s)" if results else "No HCPs found matching your search"
        }

    def tool_get_interaction_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        hcp_name = params.get("hcp_name")
        
        if hcp_name:
            interactions = [i for i in self.interactions_db if hcp_name.lower() in i["hcp_name"].lower()]
        else:
            interactions = self.interactions_db
        
        return {
            "success": True,
            "count": len(interactions),
            "interactions": interactions,
            "message": f"Found {len(interactions)} interaction(s)" if interactions else "No interactions found"
        }

    async def tool_schedule_followup(self, params: Dict[str, Any]) -> Dict[str, Any]:
        hcp_name = params.get("hcp_name", "")
        date = params.get("date", "")
        time = params.get("time", "10:00")
        purpose = params.get("purpose", "Follow-up meeting")
        
        if not hcp_name:
            return {
                "success": False,
                "error": "HCP name is required for scheduling follow-up"
            }
        
        if not date:
            return {
                "success": False,
                "error": "Date is required for scheduling follow-up"
            }
        
        followup_id = len(self.followups) + 1
        followup = {
            "id": followup_id,
            "hcp_name": hcp_name,
            "date": date,
            "time": time,
            "purpose": purpose,
            "status": "Scheduled"
        }
        
        self.followups.append(followup)
        
        return {
            "success": True,
            "message": f"Follow-up scheduled with {hcp_name} on {date} at {time}",
            "followup_id": followup_id,
            "hcp_name": hcp_name,
            "date": date,
            "time": time,
            "purpose": purpose
        }

    async def summarize_interaction(self, notes: str, topic: str) -> str:
        prompt = f"Summarize this interaction in 2-3 sentences:\n\nTopic: {topic}\nNotes: {notes}"
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        import re
        
        drugs = re.findall(r'(?:drug|medicine|product|treatment)\s+([A-Z][a-z]+)', text, re.IGNORECASE)
        hospitals = re.findall(r'hospital|clinic|center', text, re.IGNORECASE)
        
        return {
            "drugs_mentioned": drugs if drugs else [],
            "locations": hospitals if hospitals else []
        }

    async def log_interaction(self, hcp_name: str = None, hcp_specialty: str = None,
                               interaction_type: str = None, topic: str = None,
                               notes: str = None, outcome: str = None, date: str = None,
                               time: str = None) -> Dict[str, Any]:
        return await self.tool_log_interaction({
            "hcp_name": hcp_name,
            "hcp_specialty": hcp_specialty,
            "interaction_type": interaction_type,
            "topic": topic,
            "notes": notes,
            "outcome": outcome,
            "date": date,
            "time": time
        })

    async def edit_interaction(self, interaction_id: int, field: str, value: str) -> Dict[str, Any]:
        return await self.tool_edit_interaction({
            "interaction_id": interaction_id,
            "field": field,
            "value": value
        })

    async def chat(self, message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        messages = history + [{"role": "user", "content": message}]
        
        result = await self.compiled_graph.ainvoke({
            "messages": [{"role": m["role"], "content": m["content"]} for m in messages]
        })
        
        tool_results = result.get("tool_results", [])
        
        response_text = result.get("final_response", "")
        
        if tool_results:
            for tr in tool_results:
                tool = tr.get("tool")
                res = tr.get("result", {})
                if res.get("success"):
                    response_text += f"\n\n[{tool} result]: {res.get('message', 'Completed')}"
        
        return {
            "response": response_text,
            "tool_results": tool_results
        }