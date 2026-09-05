FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend application code, config, and ML artifacts
COPY backend /app/backend
COPY config /app/config
COPY ml /app/ml

# Environment variables
ENV PYTHONPATH=/app/backend
ENV ML_MODE=REAL
ENV MODEL_PATH=ml/artifacts/tomato_v1.pt

EXPOSE 8000

# Initialize DB and run uvicorn server
CMD ["sh", "-c", "python -m app.database.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
