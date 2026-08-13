FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd --system homeintegrator \
    && useradd --system --gid homeintegrator --home /app homeintegrator \
    && mkdir -p /data \
    && chown -R homeintegrator:homeintegrator /app /data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

USER homeintegrator

CMD ["python", "-m", "app.main"]
