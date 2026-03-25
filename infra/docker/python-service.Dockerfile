FROM python:3.12-slim

WORKDIR /workspace

RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    sqlalchemy \
    "psycopg[binary]" \
    pydantic \
    pydantic-settings \
    httpx \
    python-dotenv

ENV PYTHONUNBUFFERED=1
