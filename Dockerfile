FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd --gid 1000 homeintegrator \
    && useradd \
        --uid 1000 \
        --gid 1000 \
        --create-home \
        homeintegrator \
    && mkdir -p /data \
    && chown -R 1000:1000 /app /data

COPY requirements.txt /tmp/requirements.txt

RUN pip install \
    --no-cache-dir \
    --prefer-binary \
    -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

USER 1000:1000

CMD ["python", "-m", "app.main"]
