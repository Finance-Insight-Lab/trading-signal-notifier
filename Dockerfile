# Stage 1; Builder
FROM python:3.9-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2; Final clean image
FROM python:3.9-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY ./app ./app


COPY ./app /code/app

CMD ["python", "-u",  "app/main.py"]
