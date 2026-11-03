# Stato progetto — Monili Media Agency

File di passaggio di consegne, condiviso con Hermes. Aggiornare a ogni sessione di lavoro.

**Ultimo aggiornamento:** 2026-11-03 · branch `master`

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

- **Studio v2, Fase A** (30/10): "Invia bozza / Pubblica subito" sotto i campi; foto etichettate per tipo ("Catalogo (AI)", "Indossata (AI)", "Foto vera ripulita"), 2 per riga sul telefono; Reel dalla scheda usa la foto della scheda senza ricaricarla (backend copia `source_photo`); cronologia con nome del pezzo e data; testi e accenti sistemati. Test: 63. Non provato: invio vero al sito e Reel vero dalla scheda.

- **Studio v2, Fase B** (30/10): font e colori del sito (Cormorant + Outfit, avorio, terracotta); barra in basso su telefono / colonna a sinistra su computer (Nuovo pezzo · Pezzi · Reel · Altro); pagina **Pezzi** con le 4 tessere di stato (Scheda, Sito, Reel, Instagram) colorate dalla foto del pezzo; pagina **del pezzo** (`/pezzi/<id>`: foto, sito, testi da copiare, Reel); Nuovo pezzo semplificato (passaggi Analisi, Foto, Testi; a fine lavoro si apre il pezzo); motore delle foto in Altro → Impostazioni; Reel Studio con lo stesso riquadro di caricamento. Backend: `/pieces`, `/pieces/{id}`; il sito conta come "fatto" solo se l'invio è riuscito. Test: 65. Non provato: una missione vera dall'app nuova e l'invio vero al sito.

- **Studio v2, Fase C1** (30/10): pulsante "Condividi su Instagram" nel risultato del Reel e nella pagina del pezzo (Reel pronto, altrimenti le foto come post): apre il menu di condivisione dell'iPhone coi file e copia la caption; promemoria "Info sull'AI" se c'è una donna AI. **Limite**: Safari dà il menu coi file solo su https; sull'indirizzo Tailscale http copia la caption e mostra i file da salvare. Per l'https: `tailscale serve` (docs/local-mode.md, da provare). Non provato su iPhone.

## Analisi Google Business Profile (30/10/2026, statistiche mag-ott 2026 di Matteo)
- Profilo unico per via Cavour 17 e 21: 4,7 stelle, 29 recensioni, 133 foto, apertura 14/03/1996 (trent'anni di negozio: da usare in descrizione e post).
- 14.782 visualizzazioni (93% da telefono). 900 interazioni: **358 richieste di indicazioni** (circa 60 al mese, contro 1 tocco sull'indirizzo su Instagram), 435 clic sul sito, 107 chiamate. Google è il canale che porta in negozio.
- Ricerche: "monili" 1.436, "negozio" 1.389, "via cavour ravenna negozi" 297. Ci trova chi già ci conosce; nessuna ricerca generica ("gioielli Ravenna") nelle prime 5.
- Calo da settembre (probabile stagione turistica + profilo fermo; ottobre non ancora completo). Da rivedere a metà novembre.
- Da sistemare a mano (nessun codice): orari speciali di Natale (8/12, 24-25/12, 31/12, 1/1, 6/1); **orari** (Matteo, 30/10, uguali nei due negozi): lun-sab 9:30-13:00 e 14:00-19:30 fino al 30/11, continuato 9:30-19:30 dal 1/12; domenica 10:00-13:00 e 15:00-19:00. Sito: fatto nel repo `monili-vetrina` (commit `83f3473`, `shop-hours.ts`, cambio automatico al 1/12), già pubblicato (verificato il 03/11: il commit è su `master` e coincide con `origin/master`). Su Google vanno corretti a mano; categoria secondaria "Gioielleria"; descrizione con "dal 1996"; un post a settimana (copia da "Testi pronti"); risposte alle recensioni e QR per recensire.
- Il sito nel profilo è ancora `moniliravenna.shop`: passare alla vetrina solo quando ci sono 10-15 pezzi pubblicati.
- Pubblicazione automatica via API (Fase C3): **rimandata**. Servono approvazione di Google (profilo verificato da 60+ giorni, sito, modulo; 14 giorni o più) e non è certo che i post via API funzionino ancora; a mano costa un minuto a settimana. Dati salvati in `memory/performance_log.json` (chiave `google_business`).

## Fatto il 2026-10-31 (giorno del test in negozio)
- **Ricerca Higgsfield** in `knowledge/higgsfield_video_guida.md`: modelli davvero disponibili via API (Kling 3.0 Std/Pro, Seedance 2.5; Kling 4.0 c'è solo sul sito), costi reali per clip, regole per i gioielli, valutazione delle 7 funzioni del video di Gaito, protocollo del test. Reddit non raggiungibile da qui: fonti ufficiali e blog.
- Client Higgsfield verificato sulla documentazione: campi giusti, audio spento. Da decidere prima del test: modifiche A-D della sezione 4 della guida (soprattutto "Finisci sulla foto vera" solo dopo un primo piano del gioiello).
- **Kling 4.0 collegato** come motore video `kling-4` (Image to Video, 720p, fotogramma finale); stime di riserva aggiornate al listino della console (Kling 3.0 0,071, Kling 4.0 0,134, Seedance 2.5 0,175 $/s). Predefinito resta Kling 3.0 Standard. Test: 65.
- Decisi con Matteo: solo crediti API (console.higgsfield.ai, 10 $), immagini restano nello Studio (Unlimited solo a mano sul sito), niente OpenArt né abbonamento. Chiave Higgsfield ancora assente nel `.env`.
- **Primo Reel vero** fatto da Matteo con Gemini (Veo) in 9:16: bomber ricamato sotto i portici. Aggiunta la chiusura crema, pubblicato nella sala Reel del sito (non collegato a una scheda: il bomber sul sito non c'è ancora). Da verificare che il bomber sia quello vero del negozio.
- **"Carica un video esterno"** nel Reel Studio (`POST /reel/import`, `reel_studio.import_external_video`): video verticale di Gemini o del telefono → 1080×1920 con chiusura "Ti piace? Scrivici, ti diciamo se è disponibile." (frase cambiata il 03/11, prima era "te lo mettiamo da parte"), copertina e testi AI, poi Instagram e sito come gli altri Reel. Provato con il video del bomber (12,2 s, testi AI ok). Test: 70. **Serve riavviare lo Studio** per avere l'endpoint nuovo.
- Sito vetrina (repo `monili-vetrina`, tutto online): hero della Home col video Veo del gilet da tablet in su (foto sul telefono), foto vera del civico 17 in Negozi, Laboratorio e riquadro Bijoux, barra in alto del colore dello sfondo.

## Fatto il 2026-11-03 (allineamento del PRD Journey cliente)
- Confronto PRD con sito, Studio e documenti: incongruenze e regole proposte in `brainstorming marketing strategie.md` §16.
- **Frase di chiusura** «Scrivici, ti diciamo se è disponibile» al posto di «te lo mettiamo da parte»: chiusura dei Reel (`reel_studio.make_closing_card`), prompt, skill, doc, FAQ e schede del sito. I Reel già pubblicati hanno la frase vecchia dentro il video.
- **Sede del pezzo** scelta sempre da chi pubblica: tolto `SHOP_FOR_CATEGORY`, il Studio non precompila più il negozio. Test Studio: 102, tutti verdi.
- **Sito (repo `monili-vetrina`), solo in locale, NON pubblicato:** WhatsApp unico sul numero del 21 (messaggio col negozio del pezzo e link alla scheda), CTA «Chiedi disponibilità», FAQ, fallback sede senza parole chiave, condizioni (numero per il recesso). Test sito: 33 verdi, typecheck e lint puliti. **Non pubblicare finché Matteo non ha verificato l'accesso al WhatsApp del 21 su telefono e PC (J05).**
- Condizioni di vendita e privacy per le promesse nuove (pagamento al ritiro, riserva 48 h, cambio 14 giorni, scatolina, buoni, Calendly): elencate in `docs/impegni-legali.md` §3bis, da pubblicare solo insieme ai servizi.
- **J02/J03 nel sito (repo `monili-vetrina`, commit locale, NON pubblicato):** hero a 3 slide (6 s, precedente/successiva, punti, pausa, si ferma col mouse/tastiera e con «riduci movimento»; la slide 1 ha ancora il video Veo da tablet in su), pagina **Idee regalo** (`/idee-regalo`, pezzi pubblicati per fascia di prezzo, voce nel menu) e pagina **Consulenza** (`/consulenza`). La Consulenza, la slide 2, la voce di menu, la riga nella sitemap e i paragrafi su Calendly in privacy e cookie **compaiono solo se** `NEXT_PUBLIC_CONSULTATION_BOOKING_URL` contiene un vero link https di Calendly (senza, `/consulenza` dà 404 e nulla la cita). Nessun widget di terzi. Provato nel browser (desktop e telefono, con e senza il link); 37 test, typecheck, lint e build ok.
- Non fatto: codice breve del pezzo come riferimento (§16.3); J06 (Calendly sul tuo account), J07 (mettere il link reale nella variabile su Vercel dopo averlo provato) e il resto di J08–J14.

## Prossimi passi
- **Journey cliente:** decisioni e implementazioni richieste raccolte nel PRD alla radice [brainstorming marketing strategie.md](../brainstorming%20marketing%20strategie.md). WhatsApp centrale del 21, acquisti anche nei DM, quattro videoconsulenze gratuite da negozio, riserve/pagamenti entro 48 ore con due promemoria, cambi commerciali 14 giorni, buoni per sede con registro privato. Stato di questo aggiornamento: documentazione completata; sito, account, registro buoni e collaudi restano da eseguire. La bozza precedente del funnel contiene un rinvio al nuovo riferimento.
- **Studio v2** (restyling, pagina del pezzo, Instagram, motori, movimenti, carosello): piano in `docs/PIANO_STUDIO_V2.md`, Fase A fatta; B–F dopo la prova del weekend e con l'ok di Matteo (prima le decisioni della sezione 0).
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
