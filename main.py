import asyncio
from code_review_swarm import CodeReviewSwarm
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Example code snippets to review
EXAMPLE_CODES = {
    "simple_function.py": """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
    """,
    
    "api_endpoint.py": """
@app.post("/users")
def create_user(username: str, password: str):
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    return {"message": "User created"}
    """,
    
    "database_query.py": """
def get_user_orders(user_id):
    orders = []
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM orders WHERE user_id = {user_id}")
    for row in cursor.fetchall():
        orders.append(row)
    return orders
    """
}

async def review_code_example():
    try:
        # Initialize the code review swarm
        swarm = CodeReviewSwarm()
        logger.info("Initialized Code Review Swarm")
        
        # Review each code snippet
        for file_name, code in EXAMPLE_CODES.items():
            logger.info(f"\n{'='*50}\nReviewing {file_name}\n{'='*50}")
            
            # Perform code review
            results = await swarm.review_code(code, file_name)
            
            # Print results in a formatted way
            print(f"\n📝 Code Review Results for {file_name}:")
            
            # High Priority Issues
            if results["high_priority"]:
                print("\n🔴 High Priority Issues:")
                for issue in results["high_priority"]:
                    print(f"  • {issue['description']}")
                    if 'line' in issue:
                        print(f"    Line: {issue['line']}")
            
            # Medium Priority Issues
            if results["medium_priority"]:
                print("\n🟡 Medium Priority Issues:")
                for issue in results["medium_priority"]:
                    print(f"  • {issue['description']}")
                    if 'line' in issue:
                        print(f"    Line: {issue['line']}")
            
            # Low Priority Issues
            if results["low_priority"]:
                print("\n🟢 Low Priority Issues:")
                for issue in results["low_priority"]:
                    print(f"  • {issue['description']}")
                    if 'line' in issue:
                        print(f"    Line: {issue['line']}")
            
            # Suggestions
            if results["suggestions"]:
                print("\n💡 Suggestions:")
                for suggestion in results["suggestions"]:
                    print(f"  • {suggestion}")
            
            print("\n")  # Add spacing between files
            
    except Exception as e:
        logger.error(f"Error during code review: {str(e)}")
        raise

def main():
    """Run the code review example"""
    print("\n🤖 Starting Code Review Swarm Example\n")
    
    try:
        asyncio.run(review_code_example())
        print("\n✅ Code Review Complete!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Code review interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 