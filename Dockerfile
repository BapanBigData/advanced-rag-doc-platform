FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered mode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y build-essential poppler-utils && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (caching layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose app port
EXPOSE 8080

# Default command (development)
CMD ["uvicorn", "src.app.api.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# For production, override CMD in docker-compose or deployment
# CMD ["uvicorn", "src.app.api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
