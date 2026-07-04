FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# CRITICAL: without this, Python buffers stdout — agar container crash/OOM
# ho jaaye, crash se pehle ke log lines (asli error/traceback) kabhi
# Render tak pahunchte hi nahi. Isse har log line turant flush hogi.
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "-u", "-m", "devgagan"]
