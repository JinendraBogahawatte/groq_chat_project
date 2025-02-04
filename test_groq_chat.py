from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests

app = FastAPI()

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Serve static files (e.g., CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Replace with your actual API key
GROQ_API_KEY = "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"

# Correct API Endpoint
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ChatRequest Model
class ChatRequest(BaseModel):
    message: str

# Root Endpoint to Render the Chat Interface
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Chat Endpoint for Processing Messages
@app.post("/chat")
def chat(message: str = Form(...)):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.5,
        "max_completion_tokens": 1024,
        "top_p": 1,
        "stream": False,
    }

    response = requests.post(GROQ_API_URL, json=data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    # Return the assistant's reply
    return {"response": response.json()["choices"][0]["message"]["content"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
