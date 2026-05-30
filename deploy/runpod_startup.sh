#!/bin/bash
# ArgosArt RunPod Startup Script
# Alternative: no Docker, pure Python + services

set -e

echo "[$(date)] Starting ArgosArt on RunPod..."

# 1. System deps
apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg tesseract-ocr tesseract-ocr-ita tesseract-ocr-eng \
    libgl1-mesa-glx libglib2.0-0 curl ca-certificates git \
    redis-server

echo "[$(date)] System dependencies installed"

# 2. Clone repo (if not already present)
if [ ! -d "/app" ]; then
    cd /tmp && git clone https://github.com/dOuReallyDo/ArgosArt.git /app
    cd /app
fi

echo "[$(date)] Repository ready"

# 3. Python env
python3 -m venv /opt/argosart-venv
source /opt/argosart-venv/bin/activate

# 4. Install Python deps
pip install --upgrade pip setuptools wheel
pip install -e "/app"
pip install sentence-transformers easyocr

echo "[$(date)] Python dependencies installed"

# 5. Create data dirs
mkdir -p /app/data/files /app/data/logs /app/data/qdrant

# 6. Start services in background
echo "[$(date)] Starting Redis..."
redis-server --daemonize yes --logfile /app/data/logs/redis.log

echo "[$(date)] Starting Qdrant..."
/usr/local/bin/qdrant --storage-path /app/data/qdrant > /app/data/logs/qdrant.log 2>&1 &

sleep 3

# 7. Start API
echo "[$(date)] Starting ArgosArt API..."
cd /app
export ARGOS_ENV=production
export PYTHONUNBUFFERED=1

source /opt/argosart-venv/bin/activate
python -m uvicorn api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info

echo "[$(date)] ArgosArt is running!"
