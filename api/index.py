"""
FastAPI application for Trip Agent - Travel and Trip Information API

This module provides REST API endpoints to interact with the LLM agents
for trip planning, travel information, and attraction details.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import logging
import os
import sys

# Add the parent directory to sys.path so we can import llm_agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_agent import TravelResearchAgent, AdditionalInfoAgent, OrchestrateAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
# Note: In Vercel, the app instance must be named 'app'
app = FastAPI(
    title="Trip Agent API",
    description="API for trip analysis and additional information using LLM agents",
    version="1.0.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response Models ---

class FinalResponseRequest(BaseModel):
    content: Optional[str] = Field(default="", description="The gathered information/content to synthesize into a final response")
    user_query: Optional[str] = Field(default="", description="The original user query")

class FinalResponseResponse(BaseModel):
    success: bool = Field(..., description="Whether the request was successful")
    response: str = Field(..., description="The generated final response")
    message: Optional[str] = Field(default=None, description="Additional message")

class AdditionalInfoRequest(BaseModel):
    query: str = Field(..., description="The travel/trip-related query", min_length=1)

class AdditionalInfoResponse(BaseModel):
    success: bool = Field(..., description="Whether the request was successful")
    info: str = Field(..., description="The comprehensive information gathered")
    query: str = Field(..., description="The original query")
    message: Optional[str] = Field(default=None, description="Additional message")


# --- API Endpoints ---

@app.get("/", tags=["General"])
async def root():
    return {
        "message": "Trip Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "final_response": "/api/v1/final-response",
            "additional_info": "/api/v1/additional-info"
        }
    }

@app.get("/health", tags=["General"])
async def health_check():
    groq_key = os.getenv("GROQ_API_KEY")
    qdrant_url = os.getenv("QDRANT_URL")
    google_key = os.getenv("GOOGLE_API_KEY")
    hf_key = os.getenv("HUGGINGFACE_API_KEY")
    
    missing = []
    if not groq_key: missing.append("GROQ_API_KEY")
    if not qdrant_url: missing.append("QDRANT_URL")
    
    has_cloud_embeddings = bool(google_key or hf_key)
    if not has_cloud_embeddings:
        missing.append("GOOGLE_API_KEY or HUGGINGFACE_API_KEY")
    
    mode = "cloud" if (groq_key and qdrant_url and has_cloud_embeddings) else "local_fallback"
    
    return {
        "status": "healthy",
        "mode": mode,
        "missing_keys": missing,
        "version": "1.0.0"
    }

@app.post("/v1/final-response", response_model=FinalResponseResponse, tags=["Agents"])
async def generate_final_response(request: FinalResponseRequest):
    try:
        if not request.user_query:
            raise HTTPException(status_code=400, detail="User query is required")
        
        final_response = OrchestrateAgent(query=request.user_query)
        
        return FinalResponseResponse(
            success=True,
            response=final_response,
            message="Final response generated successfully"
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/additional-info", response_model=AdditionalInfoResponse, tags=["Agents"])
async def gather_additional_info(request: AdditionalInfoRequest):
    try:
        gathered_info = AdditionalInfoAgent(query=request.query)
        return AdditionalInfoResponse(
            success=True,
            info=gathered_info,
            query=request.query,
            message="Additional information gathered successfully"
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Vercel doesn't need the if __name__ == "__main__" block, 
# but we keep it for local testing.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
