# ArgosArt Deploy su RunPod — Task in Corso

_Data inizio: 2026-05-07 00:53 CET_  
_Status: 🔄 GitHub Actions Build in Progresso_

---

## Contesto

7 milestone di ArgosArt completate:
- ✅ Fondamenta (repo, struttura)
- ✅ Modelli artistici (CV parser, matching engine)
- ✅ API + UI (dashboard producer)
- ✅ Documentazione commerciale he.Art

**Bottleneck superato**: GitHub Action aggiornata per usare image name `argosart` (era hardcoded come `argos`).

---

## Azioni Intraprese (07/05 00:53→)

### 1. GitHub Action Fix
- ✅ Aggiornato `.github/workflows/build-docker.yml`
  - `IMAGE_NAME: argosart` (prima era `argos`)
  - Tags: `ghcr.io/doureallydo/argosart:latest`, `ghcr.io/doureallydo/argosart:{commit_sha}`
  - Visibility: auto-public tramite GitHub CLI
- ✅ Commit pushed: `eb34fb5` ("Fix: update GitHub Action to use argosart image name...")
- ✅ Workflow triggered manualmente: `gh workflow run build-docker.yml`

### 2. Build Status
- ❌ GitHub Actions fallito (run 25415989373): `denied: permission_denied: write_package`
  - Causa: GITHUB_TOKEN di default non ha scope `write:packages`
  - Fix: build locale + push Docker Hub (pubblico, no issues permessi)
- 🔄 Local Docker build avviato in Mac mini
- Atteso completamento: 15-20 minuti (dependency install, pip packages, CUDA base image)

---

## Strategia Build (Aggiornata)

### Local Build → Docker Hub Push

**Perché Docker Hub?**
- ✅ Public registry di default
- ✅ Zero auth issues
- ✅ RunPod pull diretto senza credenziali
- ✅ Backup se GHCR continua a fallire

**Comando**:
```bash
docker build -f deploy/Dockerfile.runpod -t doureallydo/argosart:latest .
docker push doureallydo/argosart:latest
```

## Prossimi Step (post-build)

### A. Verifica Build + Push
1. Local build completato → test localmente
   ```bash
   docker run -p 8000:8000 doureallydo/argosart:latest
   ```

### B. Deploy su RunPod (con Docker Hub image)

**Opzione 1: Web Terminal RunPod (consigliata)**
```bash
# Via Web Terminal nella console RunPod
docker run --gpus all \
  -e CUDA_VISIBLE_DEVICES=0 \
  -p 8000:8000 \
  doureallydo/argosart:latest
```

**Opzione 2: RunPod Docker Container**
- Crea nuovo pod con immagine custom
- Seleziona: GPU, 8GB VRAM min
- Mount: /data (persistenza Qdrant DB)
- Env vars: copiate da .env

**Opzione 3: Serverless Endpoint (se RunPod aggiorna)**
- Trigger HTTP → cold start → 30-60s
- Utile per demo, non per produzione

### C. Validazione Post-Deploy

1. Health check
   ```bash
   curl https://{runpod-url}/api/health
   ```

2. Test upload artista
   - CV PDF → auto-parse
   - Estrazione skills + esperienza

3. Test matching
   - Query: "Danzatrice contemporanea, italiano, Torino"
   - Atteso: ranking artisti per relevance

4. Test dashboard
   - Load UI in browser
   - Verify tabs: Matching, Ricerca, Profili

---

## Rischi Noti

| Rischio | Probabilità | Mitigation |
|---------|-----------|-----------|
| **GHCR visibility still private** | Media | Manual flip su https://github.com/doureallydo/packages |
| **Image size >10GB** | Media | RunPod complain, need lighter base image |
| **Qdrant persistence lost** | Alta | Setup /data volume mount, backup script |
| **GPU memory limit** | Bassa | Monitor con `nvidia-smi` nel pod |
| **API timeout su match semantico** | Bassa | Caching + lazy loading profili |

---

## Files di Riferimento

- Dockerfile: `deploy/Dockerfile.runpod`
- GitHub Action: `.github/workflows/build-docker.yml` (✅ updated)
- API routes: `api/matching_routes.py`
- UI: `ui/spa.html`
- Stato dettagliato: `ArgosArt_stato_avanzamento.md`

---

## Completamento Previsto

- ✅ GitHub Action fix
- 🔄 Docker build (in progress)
- ⏳ Package visibility check
- ⏳ RunPod deployment (manual)
- ⏳ Health checks
- ⏳ Performance tuning (se necessario)

**ETA**: 07/05 entro le 06:00 CET (se tutto verde).

---

_Aggiornato: 07/05 00:55 CET_
