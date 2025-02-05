from fastapi import FastAPI, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
import os
import pandas as pd
from PyPDF2 import PdfReader
from io import BytesIO
import webbrowser
import threading
import time

app = FastAPI()

# Setup Jinja2 templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Replace with your actual API key
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Root Endpoint to Render the Chat Interface
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Add HEAD request handler for root endpoint
@app.head("/")
async def read_root_head():
    return Response(status_code=200, headers={"Content-Type": "text/html"})

# Favicon handler
@app.get("/favicon.ico")
async def favicon():
    if os.path.exists("static/favicon.ico"):
        return FileResponse("static/favicon.ico")
    return Response(content="", media_type="image/x-icon")

# Chat Endpoint for Processing Messages
@app.post("/chat")
def chat(message: str = Form(...)):
    if not message.strip():
        return {"response": "Please enter a message."}

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

    try:
        response = requests.post(GROQ_API_URL, json=data, headers=headers)
        response.raise_for_status()
        return {"response": response.json()["choices"][0]["message"]["content"]}
    except requests.exceptions.RequestException as e:
        return {"response": f"Error: {str(e)}"}

# 📌 New Endpoint: File Upload & Analysis
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1].lower()

    try:
        if file_ext == "pdf":
            pdf_reader = PdfReader(BytesIO(await file.read()))
            text = "\n".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

            # Summarize the extracted text (AI-powered)
            summary = summarize_text(text)
            return {"file_content": summary}

        elif file_ext in ["csv", "xlsx"]:
            df = pd.read_csv(file.file) if file_ext == "csv" else pd.read_excel(file.file)
            
            # Analyze data trends
            summary = analyze_csv_excel(df)
            return {"file_content": summary}

        else:
            return {"error": "Unsupported file type! Upload PDF, CSV, or Excel."}

    except Exception as e:
        return {"error": f"Failed to process file: {str(e)}"}

# 📌 Summarization Function (AI-powered)
def summarize_text(text):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": f"Summarize this document:\n{text[:5000]}"}],
        "temperature": 0.5,
        "max_completion_tokens": 1024,
        "top_p": 1,
        "stream": False,
    }

    try:
        response = requests.post(GROQ_API_URL, json=data, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException:
        return "Error: Unable to summarize the document."

# 📌 Analyze CSV/Excel Data
def analyze_csv_excel(df):
    try:
        num_rows, num_cols = df.shape
        column_names = ", ".join(df.columns[:5])  # Show up to 5 columns
        summary = f"The file contains {num_rows} rows and {num_cols} columns. Sample columns: {column_names}."
        return summary
    except Exception:
        return "Error: Could not analyze the file."

# Open Browser Automatically
def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8001/")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
