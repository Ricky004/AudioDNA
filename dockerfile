# Stage 1: Build stage with dependencies
FROM python:3.13-slim AS builder

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


#Stage 2: Final production image
FROM python:3.13-slim

# Create a non-root user for security
RUN useradd --create-home appuser
WORKDIR /home/appuser/app

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python wheels from the builder stage
COPY --from=builder /wheels /wheels

# Copy project source
COPY . .

# Install the Python dependencies from wheels
RUN pip install --no-cache-dir /wheels/*

# Install the local audiodna package
RUN pip install .

# Change ownership to the non-root user
RUN chown -R appuser:appuser /home/appuser

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 5000

# Run the FastAPI server
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "5000"]