# ArgosArt — Handoff (15 maggio 2026)

## Stato sessione

Sessione di lavoro: pulizia Mac + avvio locale ArgosArt su HD_esterno via OrbStack.

---

## Completato oggi

### Pulizia Mac (~4.5 GB liberati)
- Rimosso `/Users/mariocurcio/elysia/` (427 MB — venv Python 3.12 + app Desktop)
- Rimosso Docker Desktop + dati (~57 MB)
- Rimosso Windsurf.app (877 MB)
- Rimosso `~/.codeium` (3.0 GB — modelli AI Windsurf)
- Rimosso `~/.windsurf` + support files (162 MB)
- Disco interno: ~9.3 GB liberi (era ~4.8 GB)

### OrbStack
- Installato via Homebrew in sostituzione di Docker Desktop
- CLI `docker` funzionante su arm64 nativo
- Avvio in 2-3s vs 30-60s di Docker Desktop

### Servizi Docker (su HD_esterno)
- `argos-qdrant` → Up, risponde su `localhost:6333` (`all shards are ready`)
- `argos-redis` → Up, healthy, risponde su `localhost:6379`
- Fix docker-compose: rimosso healthcheck Qdrant (immagine senza curl/wget/nc)
- Volumi: `deploy_qdrant_data`, `deploy_redis_data`

### Dockerfile fix
- `libgl1-mesa-glx` → `libgl1` (rimosso da Debian Trixie)
- Rimossa modalità `-e` (editable) — incompatibile con hatchling in container
- `COPY . .` spostato prima del `pip install` (README.md richiesto da pyproject.toml)
- Aggiunto `pip install --upgrade pip hatchling` prima delle dipendenze

### Modelli Ollama
- Verificato: blob su HD_esterno (`/Volumes/HD_esterno/ollama/models/blobs`, 9.7 GB)
- Manifesti in `~/.ollama` (1.8 MB) — configurazione corretta, nessuna azione necessaria
- Modelli presenti: `glm4`, `nomic-embed-text`, `qwen2.5`

---

## In corso al momento dell'handoff

### Build Docker ArgosArt — BLOCCATA su pip install

**Errore attuale:**
```
OSError: Readme file does not exist: README.md
AttributeError: module 'hatchling.build' has no attribute 'prepare_metadata_for_build_editable'
```

**Causa:** Docker sta usando la cache del layer precedente (step 5/7) — ignora il nuovo Dockerfile.

**Fix applicato ma non ancora eseguito:**
```zsh
cd /Volumes/HD_esterno/OpenClaw_Workspace/ArgosArt && \
docker build --no-cache -f deploy/Dockerfile -t argosart:local . 2>&1 | \
grep -E "Collecting|Installing|Successfully built|error|Error|ERROR" | head -50
```

Il `--no-cache` forza il rebuild dall'inizio ignorando tutti i layer cached.

**Dockerfile attuale** (`deploy/Dockerfile`):
```dockerfile
FROM python:3.12-slim
# ... apt-get con libgl1 (non libgl1-mesa-glx) ...
WORKDIR /app
COPY . .   # PRIMA del pip install
RUN pip install --no-cache-dir --upgrade pip hatchling && \
    pip install --no-cache-dir ".[dev]" && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN mkdir -p /app/data/files /app/data/logs
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## Prossimi step (in ordine)

1. **Eseguire build con `--no-cache`** (comando sopra) — attesa ~15 min
2. **Se build OK** → avviare il container:
   ```zsh
   docker run -d --name argosart \
     -p 8000:8000 \
     -e QDRANT_URL=http://host.docker.internal:6333 \
     -e REDIS_URL=redis://host.docker.internal:6379/0 \
     -v /Volumes/HD_esterno/OpenClaw_Workspace/ArgosArt/data:/app/data \
     --env-file /Volumes/HD_esterno/OpenClaw_Workspace/ArgosArt/.env \
     argosart:local
   ```
3. **Health check:**
   ```zsh
   curl http://localhost:8000/api/health
   ```
4. **Test upload CV PDF** via UI su `http://localhost:8000`
5. **Test matching semantico** → query artista

---

## File di riferimento

| File | Percorso |
|---|---|
| Dockerfile | `deploy/Dockerfile` |
| docker-compose | `deploy/docker-compose.yml` |
| .env | `.env` (già configurato per CPU, SQLite, storage locale) |
| Stato avanzamento | `ArgosArt_stato_avanzamento.md` |
| Questo file | `Handoff.md` |

---

## Note tecniche

- **Python nel container**: 3.12 (da immagine base `python:3.12-slim`)
- **Python su Mac**: 3.14.3 (Homebrew) — non usare per ArgosArt, usare il container
- **Embedding device**: `cpu` (configurato in `.env`)
- **Storage**: locale (`./data/files`), SQLite (`./data/argos.db`)
- **OrbStack**: attivo, icona in menu bar. Qdrant e Redis partono automaticamente con `docker compose -f deploy/docker-compose.yml up -d qdrant redis`
- **HD_esterno**: 478 GB liberi, tutti i dati ArgosArt qui

---

_Aggiornato: 15 maggio 2026_
