# Code Review Swarm 🐝

An AI-powered code review system that leverages swarm intelligence to analyze and improve code quality dynamically.

## Features

### 🔍 Multi-Agent Code Analysis
- Static analysis (linting, type checking)
- Code complexity assessment
- Security vulnerability scanning
- Best practices & style guide enforcement

### 🧠 Adaptive Learning Agents
- Agents analyze past reviews and improve suggestions over time
- Store insights in a knowledge base for recurring issues

### 🛠️ Automated Fix Suggestions
- Generates inline comments with explanations
- Provides code fixes when possible

### 🔄 Continuous Integration Support
- Works as a GitHub action or pre-commit hook
- Runs on PRs and commits to enforce quality

### 👥 Collaborative Swarm Decision-Making
- Agents vote on the best improvements
- Prioritizes actionable and high-impact suggestions

## Tech Stack
- Backend: FastAPI + swarms
- Code Analysis: pylint, mypy, bandit, flake8, radon
- Machine Learning: GPT-4-turbo
- Storage: PostgreSQL (for storing review data & insights)
- CI/CD Integration: GitHub Actions

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/peytontolbert/code-review-swarm.git
cd code-review-swarm
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API server:
```bash
python api.py
```

4. Make a code review request:
```bash
curl -X POST "http://localhost:8000/review" \
     -H "Content-Type: application/json" \
     -d '{
       "code": "def example():\n    pass",
       "file_path": "example.py"
     }'
```

## GitHub Action Integration

The code review swarm automatically runs on pull requests and pushes to main/develop branches. It will:

1. Analyze changed files
2. Generate comprehensive review comments
3. Post results as PR comments
4. Block merging if critical issues are found

## API Documentation

Once the server is running, visit:
- API docs: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 