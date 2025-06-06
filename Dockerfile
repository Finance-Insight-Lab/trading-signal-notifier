# ---- Base build image ----
FROM python:3.9-alpine AS builder

# Optional: faster builds
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Add dependencies required for building Python packages
RUN apk add --no-cache gcc musl-dev libffi-dev

WORKDIR /app

COPY requirements.txt .

# Use a virtualenv to isolate build
RUN python -m venv /venv && \
    . /venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- Final runtime image ----
FROM python:3.9-alpine

# Create a new user and switch to it
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Optional: faster, isolated venv
ENV PATH="/venv/bin:$PATH"

WORKDIR /app

# Copy venv and app from builder
COPY --from=builder /venv /venv
COPY ./app /app

USER appuser

CMD ["python", "-u", "main.py"]
