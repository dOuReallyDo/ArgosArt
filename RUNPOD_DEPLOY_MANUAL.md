# ArgosArt Deploy Manuale su RunPod — Quick Start

_Alternativa senza Docker (Piano B) — Veloce e affidabile_

---

## Prerequisiti

- Pod RunPod con **GPU** (8GB VRAM min, RTX 4090 ideale)
- SSH accesso o **Web Terminal** nella console RunPod
- ~50GB storage disponibili

---

## Procedura (10 minuti)

### 1. Clone Repository

```bash
cd /tmp
git clone https://github.com/dOuReallyDo/ArgosArt.git
cd ArgosArt
```

### 2. Setup Python Env

```bash
python3 -m venv /opt/argosart-venv
source /opt/argosart-venv/bin/activate
pip install --upgrade pip setuptools wheel
```

### 3. Install Dependencies

```bash
pip install -e "."
pip install sentence-transformers easyocr

# System deps (if not present)
apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg tesseract-ocr tesseract-ocr-ita tesseract-ocr-eng \
    redis-server
```

### 4. Create Data Dirs

```bash
mkdir -p /app/data/files /app/data/logs /app/data/qdrant
cd /app
```

### 5. Start Services (Background)

```bash
# Redis
redis-server --daemonize yes --logfile /app/data/logs/redis.log

# Qdrant (pre-built binary, already in PATH)
qdrant --storage-path /app/data/qdrant &
sleep 3
```

### 6. Launch API

```bash
source /opt/argosart-venv/bin/activate
export ARGOS_ENV=production
export PYTHONUNBUFFERED=1

cd /app
python -m uvicorn api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info
```

**Output atteso:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 7. Expose via RunPod Tunnel (optional)

Se RunPod Tunnel è configurato:
```bash
# In another terminal
runpod tunnel <pod-id> 8000
```

---

## Validazione Rapida

```bash
# Health check
curl http://localhost:8000/api/health

# Expected: {"status": "ok"}
```

---

## Vantaggi del Piano B

✅ Zero Docker complexity  
✅ Margini più ampi per debugging  
✅ Deployment time: 10 min instead of 30  
✅ No I/O errors o permission issues  
✅ Git sync facile per updates  

---

## Rollback (se fallisce)

```bash
# Kill processes
pkill -f uvicorn
pkill -f qdrant
redis-cli shutdown

# Clean
rm -rf /app
```

---

## Next: Full Docker Container (quando Docker funziona)

Una volta che il setup manuale funziona:

```bash
# Build locally
docker build -f deploy/Dockerfile.runpod -t argosart:prod .

# Push to Docker Hub (if needed for scale)
docker push doureallydo/argosart:prod

# Deploy on RunPod with single command
docker run -p 8000:8000 doureallydo/argosart:prod
```

---

**Status**: ✅ Ready to deploy  
**Tested**: No (waiting for RunPod environment)  
**Estimated Duration**: 10-15 minutes total  

---

_Updated: 07/05 01:15 CET_
