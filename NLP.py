import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from groq import Groq

# --- 1. SETUP ---
app = FastAPI(title="Malaria AI Assistant API")

# Get API Key from Environment Variable
GROQ_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_KEY:
    print("⚠️ WARNING: GROQ_API_KEY not found. API calls will fail.")
    client = None
else:
    client = Groq(api_key=GROQ_KEY)

# --- 2. DATA MODELS (Request Bodies) ---
class DiagnosisRequest(BaseModel):
    species: str
    confidence: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

# --- 3. ENDPOINTS ---

@app.get("/")
def health_check():
    return {"status": "active", "service": "Malaria AI Assistant"}

@app.post("/explain")
def explain_diagnosis(request: DiagnosisRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Server missing API Key")
    
    prompt = (
        f"You are a Senior Pathologist. The CNN detected **{request.species}** ({request.confidence}). "
        "Briefly explain the visual morphological characteristics (ring stage, chromatin dots, gametocyte shape, etc.) "
        "that justify this diagnosis in a Giemsa smear."
    )
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=350
        )
        return {"explanation": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def llama_chat(request: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Server missing API Key")

    # Build the conversation history
    messages = [{"role": "system", "content": "You are a Malaria Expert."}]
    
    # Add history from request
    for m in request.history:
        messages.append({"role": m.role, "content": m.content})
    
    # Add current user message
    messages.append({"role": "user", "content": request.message})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=messages, 
            temperature=0.7, 
            max_tokens=512
        )
        return {"reply": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
