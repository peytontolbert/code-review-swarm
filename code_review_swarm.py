from swarms import Agent, MultiAgentRouter
import logging
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import asyncio

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define specialized code review agents
code_review_agents = [
    Agent(
        agent_name="StyleAnalysisAgent",
        description="Analyzes code style and formatting issues",
        system_prompt="""You are a code style analysis expert. Review code for:
        - PEP 8 compliance (Python)
        - Consistent formatting
        - Naming conventions
        - Code organization
        Provide specific suggestions for improving code readability.""",
        model_name="gpt-4-turbo",
        openai_api_key=OPENAI_API_KEY
    ),
    Agent(
        agent_name="SecurityAgent",
        description="Identifies security vulnerabilities and best practices",
        system_prompt="""You are a security code review specialist. Analyze code for:
        - Security vulnerabilities
        - Authentication/authorization issues
        - Input validation
        - Secure coding practices
        - Dependency vulnerabilities
        Provide detailed explanations of security risks and remediation steps.""",
        model_name="gpt-4-turbo",
        openai_api_key=OPENAI_API_KEY
    ),
    Agent(
        agent_name="PerformanceAgent",
        description="Analyzes code performance and optimization opportunities",
        system_prompt="""You are a performance optimization expert. Review code for:
        - Algorithmic efficiency
        - Resource usage
        - Memory management
        - Database query optimization
        - Caching opportunities
        Suggest specific optimizations with expected impact.""",
        model_name="gpt-4-turbo",
        openai_api_key=OPENAI_API_KEY
    ),
    Agent(
        agent_name="TestingAgent",
        description="Reviews test coverage and testing practices",
        system_prompt="""You are a testing and quality assurance specialist. Analyze code for:
        - Test coverage
        - Test quality and effectiveness
        - Edge cases
        - Integration test opportunities
        - Mocking strategies
        Provide suggestions for improving test coverage and quality.""",
        model_name="gpt-4-turbo",
        openai_api_key=OPENAI_API_KEY
    ),
    Agent(
        agent_name="ArchitectureAgent",
        description="Reviews architectural patterns and code organization",
        system_prompt="""You are a software architecture expert. Review code for:
        - Design patterns
        - Code modularity
        - Dependency management
        - Interface design
        - Architectural best practices
        Suggest improvements to overall code structure and organization.""",
        model_name="gpt-4-turbo",
        openai_api_key=OPENAI_API_KEY
    )
]

class CodeReviewSwarm:
    def __init__(self):
        self.agents = code_review_agents
        
    async def _get_agent_review(self, agent: Agent, code: str, file_path: str) -> Dict:
        """Get review from a single agent"""
        try:
            review_task = f"""Review the following code from {file_path}:

{code}

Provide specific, actionable feedback focusing on your area of expertise.
Format your response as a JSON with:
- issues: list of identified issues
- suggestions: list of improvement suggestions
- severity: high/medium/low for each issue
"""
            response = await agent.achat(review_task)
            return response
        except Exception as e:
            logger.error(f"Error from agent {agent.agent_name}: {str(e)}")
            return {"review": {"issues": [], "suggestions": []}}
        
    async def review_code(self, code_content: str, file_path: str) -> Dict[str, Any]:
        """
        Perform a comprehensive code review using the swarm of agents.
        
        Args:
            code_content (str): The source code to review
            file_path (str): Path to the file being reviewed
            
        Returns:
            dict: Aggregated review results from all agents
        """
        try:
            # Create tasks for all agents
            tasks = [
                self._get_agent_review(agent, code_content, file_path)
                for agent in self.agents
            ]
            
            # Run all reviews concurrently
            review_results = await asyncio.gather(*tasks)
            
            # Aggregate and prioritize results
            aggregated_review = self._aggregate_reviews(review_results)
            
            return aggregated_review
            
        except Exception as e:
            logger.error(f"Error during code review: {str(e)}")
            raise
            
    def _aggregate_reviews(self, review_results: List[str]) -> Dict[str, Any]:
        """
        Aggregate and prioritize review results from multiple agents.
        
        Args:
            review_results (list): List of review results from agents
            
        Returns:
            dict: Aggregated and prioritized review feedback
        """
        aggregated = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "suggestions": []
        }
        
        for result in review_results:
            try:
                # Try to parse the result as JSON-like string if it's not already a dict
                if isinstance(result, str):
                    import json
                    try:
                        result = json.loads(result)
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try to extract structured data from the text
                        if "issues" in result.lower():
                            issues_start = result.lower().find("issues")
                            suggestions_start = result.lower().find("suggestions")
                            if suggestions_start == -1:
                                suggestions_start = len(result)
                            
                            issues_text = result[issues_start:suggestions_start]
                            suggestions_text = result[suggestions_start:] if suggestions_start < len(result) else ""
                            
                            # Create a simple structure
                            result = {
                                "issues": [{"description": issue.strip(), "severity": "medium"} 
                                         for issue in issues_text.split("\n") if issue.strip()],
                                "suggestions": [s.strip() for s in suggestions_text.split("\n") if s.strip()]
                            }
                
                # Process the structured data
                if isinstance(result, dict):
                    review_data = result.get("review", result)
                    
                    # Process issues
                    for issue in review_data.get("issues", []):
                        if isinstance(issue, dict):
                            severity = issue.get("severity", "low").lower()
                            if severity == "high":
                                aggregated["high_priority"].append(issue)
                            elif severity == "medium":
                                aggregated["medium_priority"].append(issue)
                            else:
                                aggregated["low_priority"].append(issue)
                    
                    # Process suggestions
                    suggestions = review_data.get("suggestions", [])
                    if isinstance(suggestions, list):
                        aggregated["suggestions"].extend([str(s) for s in suggestions if s])
                
            except Exception as e:
                logger.warning(f"Error aggregating review result: {str(e)}")
                continue
        
        # Remove duplicates while preserving order
        for key in aggregated:
            if key == "suggestions":
                aggregated[key] = list(dict.fromkeys(aggregated[key]))
            else:
                seen = set()
                aggregated[key] = [
                    x for x in aggregated[key]
                    if not (tuple(sorted(x.items())) in seen or seen.add(tuple(sorted(x.items()))))
                ]
        
        return aggregated

# Example usage
async def main():
    # Initialize the code review swarm
    swarm = CodeReviewSwarm()
    
    # Example code to review
    code = """
    def calculate_total(items):
        total = 0
        for item in items:
            total += item.price
        return total
    """
    
    # Perform code review
    review_results = await swarm.review_code(code, "example.py")
    
    # Print results
    print("Code Review Results:")
    for priority in ["high_priority", "medium_priority", "low_priority"]:
        print(f"\n{priority.upper()} ISSUES:")
        for issue in review_results[priority]:
            print(f"- {issue}")
    
    print("\nSUGGESTIONS:")
    for suggestion in review_results["suggestions"]:
        print(f"- {suggestion}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 