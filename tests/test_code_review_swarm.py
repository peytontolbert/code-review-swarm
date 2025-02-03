import pytest
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code_review_swarm import CodeReviewSwarm, code_review_agents
import logging
from unittest.mock import Mock, patch

# Test data
SAMPLE_CODE = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
"""

SAMPLE_REVIEW_RESPONSE = {
    "review": {
        "issues": [
            {
                "description": "Missing type hints",
                "severity": "medium",
                "line": 1
            },
            {
                "description": "No input validation",
                "severity": "high",
                "line": 3
            }
        ],
        "suggestions": [
            "Add type hints to function parameters and return value",
            "Add input validation for items parameter"
        ]
    }
}

@pytest.fixture
def code_review_swarm():
    return CodeReviewSwarm()

@pytest.mark.asyncio
async def test_review_code_success(code_review_swarm, mocker):
    """Test successful code review process"""
    # Mock the router's concurrent_batch_route
    mocker.patch.object(
        code_review_swarm.router,
        'concurrent_batch_route',
        return_value=[SAMPLE_REVIEW_RESPONSE]
    )
    
    result = await code_review_swarm.review_code(SAMPLE_CODE, "test.py")
    
    assert isinstance(result, dict)
    assert "high_priority" in result
    assert "medium_priority" in result
    assert "low_priority" in result
    assert "suggestions" in result
    
    # Verify high priority issues
    assert len(result["high_priority"]) == 1
    assert result["high_priority"][0]["description"] == "No input validation"
    
    # Verify medium priority issues
    assert len(result["medium_priority"]) == 1
    assert result["medium_priority"][0]["description"] == "Missing type hints"
    
    # Verify suggestions
    assert len(result["suggestions"]) == 2

@pytest.mark.asyncio
async def test_review_code_error_handling(code_review_swarm, mocker):
    """Test error handling in code review process"""
    # Mock the router to raise an exception
    mocker.patch.object(
        code_review_swarm.router,
        'concurrent_batch_route',
        side_effect=Exception("Test error")
    )
    
    with pytest.raises(Exception) as exc_info:
        await code_review_swarm.review_code(SAMPLE_CODE, "test.py")
    
    assert str(exc_info.value) == "Test error"

def test_aggregate_reviews_empty():
    """Test aggregating empty review results"""
    swarm = CodeReviewSwarm()
    result = swarm._aggregate_reviews([])
    
    assert result["high_priority"] == []
    assert result["medium_priority"] == []
    assert result["low_priority"] == []
    assert result["suggestions"] == []

def test_aggregate_reviews_invalid_data():
    """Test aggregating invalid review data"""
    swarm = CodeReviewSwarm()
    result = swarm._aggregate_reviews([{"invalid": "data"}])
    
    assert result["high_priority"] == []
    assert result["medium_priority"] == []
    assert result["low_priority"] == []
    assert result["suggestions"] == []

def test_code_review_agents_configuration():
    """Test the configuration of code review agents"""
    assert len(code_review_agents) == 5
    
    agent_names = {agent.agent_name for agent in code_review_agents}
    expected_names = {
        "StyleAnalysisAgent",
        "SecurityAgent",
        "PerformanceAgent",
        "TestingAgent",
        "ArchitectureAgent"
    }
    
    assert agent_names == expected_names
    
    for agent in code_review_agents:
        assert agent.model_name == "gpt-4-turbo"
        assert isinstance(agent.description, str)
        assert isinstance(agent.system_prompt, str)

@pytest.mark.asyncio
async def test_review_code_with_context(code_review_swarm, mocker):
    """Test code review with additional context"""
    # Mock the router's concurrent_batch_route
    mocker.patch.object(
        code_review_swarm.router,
        'concurrent_batch_route',
        return_value=[SAMPLE_REVIEW_RESPONSE]
    )
    
    # Test with Python file
    result = await code_review_swarm.review_code(SAMPLE_CODE, "test.py")
    assert result["file_type"] if hasattr(result, "file_type") else None == "py"
    
    # Test with JavaScript file
    result = await code_review_swarm.review_code("function test() {}", "test.js")
    assert result["file_type"] if hasattr(result, "file_type") else None == "js"

@pytest.mark.asyncio
async def test_concurrent_review_processing(code_review_swarm, mocker):
    """Test concurrent processing of multiple reviews"""
    multiple_responses = [
        SAMPLE_REVIEW_RESPONSE,
        SAMPLE_REVIEW_RESPONSE,
        SAMPLE_REVIEW_RESPONSE
    ]
    
    mocker.patch.object(
        code_review_swarm.router,
        'concurrent_batch_route',
        return_value=multiple_responses
    )
    
    result = await code_review_swarm.review_code(SAMPLE_CODE, "test.py")
    
    # Verify that all responses were processed
    assert len(result["high_priority"]) == 3  # One from each response
    assert len(result["medium_priority"]) == 3
    assert len(result["suggestions"]) == 6  # Two from each response 