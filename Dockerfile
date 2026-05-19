FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpython3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -m appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY authelia-manager.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

RUN mkdir -p instance && chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]
