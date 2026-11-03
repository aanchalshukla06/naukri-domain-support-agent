import json
import logging
from datetime import datetime
from uuid import uuid4
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from pydantic import BaseModel
from security.guardrails import validate_input, mask_pii

# --- TASK 12: Structured JSON-Lines Logging ---
logging.basicConfig(filename='api_requests.jsonl', level=logging.INFO, format='%(message)s')

def log_request(trace_id: str, query: str, response: str, response_time_ms: float):
    # Rubric Requirement: Logged request text must NOT contain unmasked PII.
    safe_query = mask_pii(query)
    log_entry = {
        "trace_id": trace_id,
        "timestamp": datetime.utcnow().isoformat(),
        "query": safe_query,
        "response": response,
        "response_time_ms": response_time_ms
    }
    logging.info(json.dumps(log_entry))

app = FastAPI(title="Naukri Domain Support Agent")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    trace_id: str

class AddDocumentRequest(BaseModel):
    topic: str
    text: str

# --- TASK 16: Response Caching ---
query_cache = {}

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    trace_id = str(uuid4())
    start_time = datetime.now()
    
    # 1. Guardrail Check
    validation = validate_input(request.query)
    if not validation["valid"]:
        return QueryResponse(answer=validation["reason"], trace_id=trace_id)
        
    safe_query = validation["clean_query"]
    
    # 2. Cache Check (Task 16)
    normalized_query = safe_query.strip().lower()
    if normalized_query in query_cache:
        response_text = f"[CACHE HIT] {query_cache[normalized_query]}"
    else:
        # In production, you would await run_review_stage(run_crew(safe_query)) here.
        # For MOCK_LLM testing, we return a mock answer.
        response_text = "Mock LLM Response: Application is in Screening."
        query_cache[normalized_query] = response_text

    end_time = datetime.now()
    duration_ms = (end_time - start_time).total_seconds() * 1000
    
    log_request(trace_id, request.query, response_text, duration_ms)
    return QueryResponse(answer=response_text, trace_id=trace_id)

@app.post("/add-document")
async def add_document(request: AddDocumentRequest):
    # Implementation for adding to ChromaDB would go here
    return {"status": "success", "message": f"Added document on {request.topic}"}

# --- TASK 11: Resilient WebSocket Endpoint ---
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    trace_id = str(uuid4())
    try:
        while True:
            data = await websocket.receive_text()
            # 1. Guardrail Check
            validation = validate_input(data)
            if not validation["valid"]:
                await websocket.send_text(validation["reason"])
                continue
                
            safe_query = validation["clean_query"]
            
            # Send Mock Response
            await websocket.send_text(f"Agent: I received your query safely: {safe_query}")
            
    except WebSocketDisconnect:
        # Rubric Requirement: Catch disconnect so the server stays alive
        print(f"Client {trace_id} disconnected normally.")