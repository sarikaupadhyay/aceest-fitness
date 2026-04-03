# ── Stage 1: Base image ──────────────────────
# Use official lightweight Python image
FROM python:3.11-slim

# ── Metadata ─────────────────────────────────
LABEL maintainer="ACEest DevOps Assignment"
LABEL description="ACEest Fitness & Gym Flask Web Application"

# ── Environment variables ─────────────────────
# Stops Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Stops Python from buffering stdout/stderr (logs show immediately)
ENV PYTHONUNBUFFERED=1

# ── Set working directory ─────────────────────
WORKDIR /app

# ── Install dependencies ──────────────────────
# Copy requirements first (Docker layer caching — only reinstalls if requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ─────────────────────
COPY app.py .

# ── Expose port ───────────────────────────────
EXPOSE 5000

# ── Run the application ───────────────────────
CMD ["python", "app.py"]
