# Use slim Python 3.10 image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# 1. Install COMPILER TOOLS FIRST (critical for scikit-surprise)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy FastAPI backend code
COPY app/backend/main.py ./main.py

# Copy model files from root-level 'models/' into container's /app/models/
COPY models/ ./models/

# 3. Install Python packages DIRECTLY (no requirements.txt)
RUN pip install \
    fastapi \
    uvicorn \
    pandas \
    numpy==1.21.6 \
    scikit-learn==1.0.2 \
    scikit-surprise \
    joblib \
    gdown

# 4. Verify models are accessible
RUN ls -la models/

# 5. Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]