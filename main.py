from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import httpx
import sympy as sp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"message": "NovaMind API is running"}

@app.post("/chat")
async def chat(request: ChatRequest):
    x = sp.symbols('x')
    msg = request.message

    try:
        if "اشتقاق" in msg or "مشتقة" in msg:
            expr = sp.sympify(msg.replace("اشتقاق", "").replace("مشتقة", "").strip())
            result = sp.diff(expr, x)
            return {"success": True, "engine": "sympy", "response": str(result)}
        elif "تكامل" in msg:
            expr = sp.sympify(msg.replace("تكامل", "").strip())
            result = sp.integrate(expr, x)
            return {"success": True, "engine": "sympy", "response": str(result) + " + C"}
        else:
            expr = sp.sympify(msg)
            result = sp.solve(expr, x)
            return {"success": True, "engine": "sympy", "response": str(result)}
    except:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"success": False, "error": "API Key is missing"}

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": msg}]}]}

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]

        return {"success": True, "engine": "gemini", "response": text}
