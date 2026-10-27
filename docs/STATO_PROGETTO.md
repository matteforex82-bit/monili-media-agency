# Stato progetto — Monili Media Agency

File di passaggio di consegne, condiviso con Hermes. Aggiornare a ogni sessione di lavoro.

**Ultimo aggiornamento:** 2026-10-27 · branch `master`

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

## Analisi Instagram (Insights ago-ott 2026, screenshot di Matteo)
- 25.989 visualizzazioni: Storie 62,4%, Reel 34%, post statici 3,7% → video-first confermato.
- 40% visualizzazioni da non follower (Reel). 1.071 follower. 298 interazioni (59% sui post, da follower fedeli).
- 627 visite profilo ma **1 tocco sull'indirizzo** → ogni contenuto chiude con invito al DM.
- Più visti: Reel in negozio con Anastasia (690, 661), bracciale su ardesia (716), poster orecchini (627).
- Problemi del feed: troppa AI generica (modelle diverse ogni volta), stili misti (scritte fumetto/neon),
  un difetto pubblicato (rettangolo nero sull'anello rubini), highlight ancora "Saldi/Vestiti estate".
- Anastasia costava 150 €/giorno: Matteo non ha budget → **Modella Monili AI ricorrente** + mani/negozio veri.
- Orari: il grafico indica le 18 come ora meno attiva, ma ha picchi alle 3 → da verificare (fuso orario?).

## Fatto il 2026-10-23 (seconda parte)
- Memoria brand aggiornata con l'identità reale (colorata, artigianale, boho-etnica) in `CLAUDE.md` e `main.BRAND`;
  Insights salvati in `memory/performance_log.json` (li leggono gli agenti).
- Reel Studio: 6 ricette (`/libera`, `/modella-monili`, `/mani-bancone`, `/pietra-settimana`, `/tre-modi`,
  `/colori-ravenna`), Modella Monili persistente, copertina poster serif/crema, controllo qualità AI
  fotogramma vs foto reale con 1 rigenerazione. Testato con AI simulata.

## Fatto il 2026-10-24
- Ricerca su immagini OpenAI (GPT-Image-2.5 Flare/Sunburst), video Higgsfield e Instagram 2026:
  `knowledge/ricerca_marketing_ai_2026.md`.
- **Skill modificabili** in `skills/*.md` (8 ricette + 4 basi comuni), pagina **Skill** nell'app per modificarle,
  modifiche salvate nello storage con "Ripristina originale".
- **Coerenza 100% prodotto/scena** (richiesta di Matteo): scena unica per tutto il video, fotogramma guida in
  sequenza, controllo severo 8/10 con 3 tentativi, sostituzione con la foto reale se l'AI non è fedele,
  chiusura delle scene sulla foto vera via Higgsfield.

## Fatto il 2026-10-24 (lavoro in autonomia, 2 ore)
- **Pagina Risultati** (`/risultati`): numeri di ogni contenuto pubblicato, riepilogo per skill/formato/giorno/ora,
  dati affidabili (≥2 contenuti) passati a regista e copywriter.
- **Skill di Natale**: `/idea-regalo`, `/countdown-natale` + `docs/piano-natale-2026.md` (calendario fino al 6 gennaio,
  Black Friday ven 27/11, Immacolata mar 8/12, brief pronti).
- **Motore OpenAI diretto** GPT-Image-2.5 Flare (fotogrammi) / Sunburst (copertine) via `/v1/images/edits`,
  attivo solo con `OPENAI_API_KEY`; parametri verificati sulla reference ufficiale OpenAI.
- **Test automatici** in `tests/` (27 test, senza rete né chiavi): `python -m pytest tests`.

## Fatto il 2026-10-27
- **Scheda vetrina corretta**: il riassunto viene dalla sezione "DESCRIZIONE AI" dell'analisi, e tra i materiali restano solo quelli certi (niente "argento" se è metallo argentato).
- **Missione snellita in "Scheda pezzo"** (scelta di Matteo: il sito serve a farsi trovare su Google e dalle AI, a dare un link da girare su WhatsApp e a portare la gente in via Cavour).
  Il flusso è: analisi → piano (styling + prompt) → 2 foto AI (catalogo, indossato) + foto reale ritagliata gratis → testi (SEO, WhatsApp, Google Business, caption, 3+2 hashtag).
  Si passa **da 7 a 3 chiamate di testo e da 5 a 2 immagini**; niente più post, story e carosello statici (Instagram passa dal Reel Studio). `main.py` scende da circa 1980 a circa 830 righe.
  Le missioni vecchie si aprono ancora, con la scheda "Instagram (vecchio kit)". Test: 33.

## Prossimi passi
0. Prima missione "Scheda pezzo" vera con un gioiello: controllare foto e testi, e quanto costa davvero.
1. Matteo crea l'account e la API key Higgsfield (guida in `docs/reel-studio.md`) e la mette nel `.env` locale / su Render.
2. Primo Reel vero con un prodotto reale: verificare fedeltà del gioiello e costo effettivo vs stima.
3. Tarare le stime (`HF_FALLBACK_USD_PER_SEC_*`) con i costi reali.
4. Matteo: verificare il fuso orario del grafico "Periodi di maggiore attività" dall'app e aggiornare le storie in evidenza (ferme all'estate).
5. Raccogliere da Matteo 2-3 comandi ChatGPT che usa (/poster, /carouselart) e trasformarli in skill.
5b. Matteo: se vuole GPT-Image-2.5, creare `OPENAI_API_KEY` su platform.openai.com (il codice è pronto).
6. Usare la pagina Risultati dopo ogni pubblicazione; più avanti lettura automatica dei numeri con l'API Meta.

## Aperti / da sapere
- **Sito vetrina non online**: l'URL nel codice (`web-five-theta-58.vercel.app`) ora ospita un'altra app ("Alfred");
  `/admin/review` → 404. `SHOWCASE_INGEST_URL` va impostata quando il sito vetrina sarà pubblicato.
  Il codice del sito vetrina non è in nessun repo GitHub collegato.
- Render free: ok per provare, per i video meglio la modalità locale (storage persistente, CPU).
- Le variabili in `render.yaml` valgono solo con il sync del Blueprint: verificare l'Environment sul dashboard Render.
