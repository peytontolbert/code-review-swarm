import pytest
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from api import app, CodeReviewRequest
import json

# Test data
SAMPLE_CODE = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
"""

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_review_endpoint_success(client, mocker):
    """Test successful code review request"""
    # Mock the code review swarm
    mock_review_result = {
        "high_priority": [
            {"description": "Security issue", "severity": "high", "line": 1}
        ],
        "medium_priority": [
            {"description": "Performance issue", "severity": "medium", "line": 2}
        ],
        "low_priority": [
            {"description": "Style issue", "severity": "low", "line": 3}
        ],
        "suggestions": [
            "Add input validation",
            "Improve error handling"
        ]
    }
    
    mocker.patch(
        "api.code_review_swarm.review_code",
        return_value=mock_review_result
    )
    
    # Make request
    response = client.post(
        "/review",
        json={
            "code": SAMPLE_CODE,
            "file_path": "test.py"
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    
    # Verify response structure
    assert "high_priority" in result
    assert "medium_priority" in result
    assert "low_priority" in result
    assert "suggestions" in result
    
    # Verify content
    assert len(result["high_priority"]) == 1
    assert len(result["medium_priority"]) == 1
    assert len(result["low_priority"]) == 1
    assert len(result["suggestions"]) == 2

def test_review_endpoint_invalid_request(client):
    """Test code review request with invalid data"""
    # Test missing required fields
    response = client.post(
        "/review",
        json={"code": SAMPLE_CODE}  # Missing file_path
    )
    assert response.status_code == 422
    
    # Test empty code
    response = client.post(
        "/review",
        json={
            "code": "",
            "file_path": "test.py"
        }
    )
    assert response.status_code == 422
    
    # Test invalid JSON
    response = client.post(
        "/review",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_review_endpoint_error_handling(client, mocker):
    """Test error handling in review endpoint"""
    # Mock the code review swarm to raise an exception
    mocker.patch(
        "api.code_review_swarm.review_code",
        side_effect=Exception("Test error")
    )
    
    response = client.post(
        "/review",
        json={
            "code": SAMPLE_CODE,
            "file_path": "test.py"
        }
    )
    
    assert response.status_code == 500
    assert "error" in response.json()["detail"].lower()

def test_review_endpoint_with_context(client, mocker):
    """Test code review request with additional context"""
    mock_review_result = {
        "high_priority": [],
        "medium_priority": [],
        "low_priority": [],
        "suggestions": []
    }
    
    mocker.patch(
        "api.code_review_swarm.review_code",
        return_value=mock_review_result
    )
    
    # Test with context
    response = client.post(
        "/review",
        json={
            "code": SAMPLE_CODE,
            "file_path": "test.py",
            "context": {
                "repository": "test-repo",
                "branch": "main",
                "author": "test-user"
            }
        }
    )
    
    assert response.status_code == 200
    
def test_request_validation():
    """Test request model validation"""
    # Valid request
    request = CodeReviewRequest(
        code=SAMPLE_CODE,
        file_path="test.py"
    )
    assert request.code == SAMPLE_CODE
    assert request.file_path == "test.py"
    
    # Valid request with context
    request = CodeReviewRequest(
        code=SAMPLE_CODE,
        file_path="test.py",
        context={"test": "data"}
    )
    assert request.context == {"test": "data"}
    
    # Test invalid request
    with pytest.raises(ValueError):
        CodeReviewRequest(
            code="",  # Empty code should raise error
            file_path="test.py"
        ) 