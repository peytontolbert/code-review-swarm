from setuptools import setup, find_packages

setup(
    name="code-review-swarm",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "swarms>=0.3.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.4.2",
        "sqlalchemy>=2.0.23",
        "psycopg2-binary>=2.9.9",
        "alembic>=1.12.1",
        "asyncpg>=0.29.0",
    ],
    python_requires=">=3.9",
) 