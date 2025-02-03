from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional
import uvicorn
from code_review_swarm import CodeReviewSwarm
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Code Review Swarm API",
    description="AI-powered code review system using swarm intelligence",
    version="1.0.0"
)

# Initialize code review swarm
code_review_swarm = CodeReviewSwarm()

class CodeReviewRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Source code to review")
    file_path: str = Field(..., min_length=1, regex=r"^[\w\-./]+$", description="Path to the file being reviewed")
    context: Optional[Dict] = Field(None, description="Additional context for the review")
    
    @validator("code")
    def validate_code(cls, v):
        if not v.strip():
            raise ValueError("Code cannot be empty or whitespace only")
        return v
    
    @validator("file_path")
    def validate_file_path(cls, v):
        if not any(v.endswith(ext) for ext in [".py", ".js", ".ts", ".java", ".cpp", ".go"]):
            raise ValueError("Unsupported file type. Must be one of: .py, .js, .ts, .java, .cpp, .go")
        return v

class CodeReviewResponse(BaseModel):
    high_priority: List[Dict] = Field(
        default_factory=list,
        description="High priority issues that need immediate attention"
    )
    medium_priority: List[Dict] = Field(
        default_factory=list,
        description="Medium priority issues to be addressed"
    )
    low_priority: List[Dict] = Field(
        default_factory=list,
        description="Low priority issues and suggestions"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="General improvement suggestions"
    )

@app.post("/review", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest):
    """
    Perform a comprehensive code review using the swarm of specialized agents.
    
    Args:
        request (CodeReviewRequest): The code review request containing the code and metadata
        
    Returns:
        CodeReviewResponse: Aggregated review results from all agents
        
    Raises:
        HTTPException: If there's an error processing the review
    """
    try:
        # Log review request
        logger.info(f"Processing code review for file: {request.file_path}")
        
        # Perform code review
        review_results = await code_review_swarm.review_code(
            code_content=request.code,
            file_path=request.file_path
        )
        
        # Log review completion
        logger.info(f"Completed code review for file: {request.file_path}")
        
        return CodeReviewResponse(**review_results)
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error processing code review request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing code review: {str(e)}"
        )

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 