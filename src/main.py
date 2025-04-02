from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv
from typing import Dict, List
from integrations.openai_analyzer import OpenAIAnalyzer

# Load environment variables
load_dotenv()

app = FastAPI(
    title="API Integration Demo",
    description="OpenAI Integration Demo"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Initialize OpenAI analyzer
openai_analyzer = OpenAIAnalyzer(os.getenv("OPENAI_API_KEY"))

@app.get("/")
async def root():
    return FileResponse('src/static/index.html')

@app.post("/analyze")
async def analyze_data(metrics: Dict, alerts: List[Dict]):
    try:
        # Call OpenAI analyzer
        analysis = await openai_analyzer.analyze_metrics(metrics, alerts)
        return JSONResponse(content=analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
