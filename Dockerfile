FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
# Defaults for the compose stack. GEMINI_API_KEY is NOT baked in — pass
# it at runtime (docker-compose env_file .env, or -e on docker run).
ENV STORE=postgres \
    DATABASE_URL=postgresql://rolefit:rolefit@db:5432/rolefit \
    GEMINI_MODEL=gemini-3.6-flash \
    GEMINI_EMBED_MODEL=gemini-embedding-001 \
    EMBEDDING_DIM=3072
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
