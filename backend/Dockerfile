# Backend image — FastAPI + Uvicorn. Build context is the backend/ directory.
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Apply migrations, then serve. All config comes from the environment — see
# .env.example (DATABASE_URL, ADMIN_PIN, ANTHROPIC_API_KEY, SMTP_*, CORS_ORIGINS).
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
