# Stato progetto — Monili Media Agency

File di passaggio di consegne, condiviso con Hermes. Aggiornare a ogni sessione di lavoro.

**Ultimo aggiornamento:** 2026-10-29 · branch `master`

## Cos'è
App per creare contenuti social de I Monili Ravenna a partire dalle foto prodotto.
Backend FastAPI (`api/server.py`, `main.py`, `reel_studio.py`) + frontend Next.js (`frontend/`).
Gira solo sul PC (`scripts/start-local.ps1`), usato anche dal telefono con Tailscale. Render è stato dismesso il 30/10/2026: `render.yaml` tolto, servizi `monili-media-agency`, `monili-backend` e `monili-frontend` sospesi (si riaccendono da Render con "Resume").

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
- Problemi del feed: troppa AI generica (modelle diverse ogni volta, troppo perfette), stili misti (scritte fumetto/neon),
  un difetto pubblicato (rettangolo nero sull'anello rubini), highlight ancora "Saldi/Vestiti estate".
- Anastasia costava 150 €/giorno: Matteo non ha budget → donne AI + mani/negozio veri. Prima idea: una Modella Monili fissa; il 29/10 Matteo ha scelto invece donne diverse ma reali.
- Orari: il grafico indica le 18 come ora meno attiva, ma ha picchi alle 3 → da verificare (fuso orario?).

## Fatto il 2026-10-23 (seconda parte)
- Memoria brand aggiornata con l'identità reale (colorata, artigianale, boho-etnica) in `CLAUDE.md` e `main.BRAND`;
  Insights salvati in `memory/performance_log.json` (li leggono gli agenti).
- Reel Studio: 6 ricette (`/libera`, `/modella-monili` (oggi `/indossato`), `/mani-bancone`, `/pietra-settimana`, `/tre-modi`,
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

## Fatto il 2026-10-29
- **Foto del sito decise** (`docs/foto-prodotti.md`): 2 o 3 per pezzo, sempre 4:5 su fondo avorio. Pulita AI (copertina), indossata da una donna AI, foto vera ripulita solo se viene bene.
- **Foto vera ripulita senza AI sul pezzo** (`photo_cleanup.py`): scontorno BiRefNet sul PC, fondo avorio, luce e colore. Lo Studio la spunta solo se lo scontorno è pulito, altrimenti scrive il motivo. Provata su 4 foto vere: 3 buone, 1 scartata giustamente (scopa attaccata alla giacca). Test: 52.
- **Niente modella fissa, una donna per pezzo** (scelta di Matteo, precisata il 30/10): la Scheda pezzo sceglie la donna e il Reel fatto con "Fai il Reel di questo pezzo" usa la stessa (descrizione + foto indossata come riferimento del viso); da un pezzo all'altro cambia. Belle ed eleganti ma reali; la donna la **inventa l'AI** (linea guida in `skills/_base/donne.md`), dentro un Reel resta la stessa. Tolti il pannello "Modella Monili" e la foto di riferimento; la skill `/modella-monili` ora si chiama `/indossato` (il vecchio nome funziona ancora).
- **Libertà creativa + divieti** (30/10, scelta di Matteo: niente elenchi che rendono tutto uguale): l'AI inventa luoghi, donne e pose adatti allo stile del negozio e riceve donne e scene recenti da non ripetere. Unico limite: `skills/_base/divieti.md` (pagina Skill → "Mai nei contenuti"), in tutti i prompt di foto e Reel. Test: 59.
- **"Pubblica subito"** nello Studio (30/10): casella spenta di default; accesa, il pezzo va online senza passare da `/admin/review`. Test: 60.

## Prossimi passi
- **Studio v2** (restyling, pagina del pezzo, Instagram, motori, movimenti, carosello): piano in `docs/PIANO_STUDIO_V2.md`, da approvare; Fase A prima della prova del weekend.
0. Prima missione "Scheda pezzo" vera con un gioiello: controllare foto e testi, e quanto costa davvero.
1. Matteo crea l'account e la API key Higgsfield (guida in `docs/reel-studio.md`) e la mette nel `.env` del PC.
2. Primo Reel vero con un prodotto reale: verificare fedeltà del gioiello e costo effettivo vs stima.
3. Tarare le stime (`HF_FALLBACK_USD_PER_SEC_*`) con i costi reali.
4. Matteo: verificare il fuso orario del grafico "Periodi di maggiore attività" dall'app e aggiornare le storie in evidenza (ferme all'estate).
5. Raccogliere da Matteo 2-3 comandi ChatGPT che usa (/poster, /carouselart) e trasformarli in skill.
5b. Matteo: se vuole GPT-Image-2.5, creare `OPENAI_API_KEY` su platform.openai.com (il codice è pronto).
6. Usare la pagina Risultati dopo ogni pubblicazione; più avanti lettura automatica dei numeri con l'API Meta.

## Aperti / da sapere
- **Sito vetrina online dal 30/10/2026**: https://monili-vetrina.vercel.app (repo `monili-vetrina`, progetto Vercel
  `monili-vetrina`, piano Hobby per ora, database e foto nuovi e vuoti). Il `.env` dello Studio sul PC punta già lì.
  Dettagli e prossimi passi in `PLAN_VETRINA.md`, Fase 5.
