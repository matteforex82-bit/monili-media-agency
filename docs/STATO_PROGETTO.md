# Stato progetto — Monili Media Agency

File di passaggio di consegne, condiviso con Hermes. Aggiornare a ogni sessione di lavoro.

**Ultimo aggiornamento:** 2026-10-23 · branch `claude/determined-knuth-zp63a6`

## Cos'è
App per creare contenuti social de I Monili Ravenna a partire dalle foto prodotto.
Backend FastAPI (`api/server.py`, `main.py`, `reel_studio.py`) + frontend Next.js (`frontend/`).
Gira su Render (`monili-backend`, `monili-frontend`, piano free) o in locale sul portatile (`scripts/start-local.ps1`).

## Decisione strategica (ott 2026)
Matteo: **le foto statiche su Instagram non rendono più → priorità a Reel e Story video.**
Motore video: **Higgsfield via API REST** (non MCP), mantenendo il flusso intelligente già esistente
(analisi prodotto, regia, prompt, testi, hashtag).

## Fatto il 2026-10-23
- **Test di salute** su Render con foto reale: missione statica completata in ~13 min, chiave OpenRouter valida,
  immagini buone. Nota fedeltà: nella foto indossata la goccia blu è diventata ovale.
- **Modelli riallineati**: rimossi i modelli non più disponibili su OpenRouter (flux.2-klein-4b, seedream-4.5,
  claude-3.7-sonnet). Default ovunque: testo `openai/gpt-5.5`, immagini `openai/gpt-5.4-image-2`.
- **Stagione dinamica** nei prompt (`main.SEASON`, ora Autunno/Inverno 2026/27) al posto di "P/E 2026" fisso.
- **Reel Studio** (`/reel`): storyboard approvabile, stima costi per reel, fotogrammi chiave fedeli,
  video Higgsfield (Kling 3.0 / Seedance 2.5), clip reali opzionali, montaggio 9:16, testi. Dettagli in `docs/reel-studio.md`.
  Testato con AI simulata (API + browser iPhone); **non ancora testato con Higgsfield reale** (manca la key).

## Prossimi passi
1. Matteo crea l'account e la API key Higgsfield (guida in `docs/reel-studio.md`) e la mette nel `.env` locale / su Render.
2. Primo Reel vero con un prodotto reale: verificare fedeltà del gioiello e costo effettivo vs stima.
3. Tarare le stime (`HF_FALLBACK_USD_PER_SEC_*`) con i costi reali.
4. Chiudere il ciclo performance: `memory/performance_log.json` è ancora vuoto → schermata per inserire reach/visite dopo la pubblicazione.

## Aperti / da sapere
- **Sito vetrina non online**: l'URL nel codice (`web-five-theta-58.vercel.app`) ora ospita un'altra app ("Alfred");
  `/admin/review` → 404. `SHOWCASE_INGEST_URL` va impostata quando il sito vetrina sarà pubblicato.
  Il codice del sito vetrina non è in nessun repo GitHub collegato.
- Render free: ok per provare, per i video meglio la modalità locale (storage persistente, CPU).
- Le variabili in `render.yaml` valgono solo con il sync del Blueprint: verificare l'Environment sul dashboard Render.
