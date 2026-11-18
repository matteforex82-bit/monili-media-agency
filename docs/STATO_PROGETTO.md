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
- J08 (testi): `docs/messaggi-ordine-pronti.md` (disponibilità, riserva 48 h, promemoria, scadenza, pagato, ritiro, spedito, cambio). I testi «paga al ritiro» e «cambio 14 gg» sono marcati da non usare finché le condizioni di vendita non li dichiarano (J12).
- **4/11, online (sito commit ac15a12):** codice breve del pezzo `M-XXXXX` (`piece_code.py`, `pieceCode` nel sito; stesso calcolo dal `run_id`, valori di prova condivisi) in scheda sito, WhatsApp, caption e invito della Scheda, caption dei Reel nati da una Scheda; bozza delle nuove condizioni di vendita nel sito (riserva 48 h, pagamento al ritiro, ritiro come contratto a distanza, partenza 2–3 giorni, scatolina, cambio 14 giorni). Condizioni da far rivedere a un consulente; il Studio va riavviato.
- Non fatto: J06 (Calendly sul tuo account), J07 (mettere il link reale nella variabile su Vercel dopo averlo provato) e il resto di J09–J14 (registro privato, SumUp/bonifico, procedura pacchetti, buoni, condizioni).

## Prima Scheda pezzo vera (7/11/2026): anello in acciaio ambra (M-4T49F)
- **Sede forzata al 17:** causa nel sito, non nello Studio (che aveva inviato il 21): `publish-readiness.ts` bloccava bijoux/gioielli senza via Cavour 17 e Matteo ha dovuto spuntare anche il 17 in `/admin/review`. Regola tolta nel repo del sito (`Ecosistema Monili/apps/web`, test aggiunto, 42 verdi, tsc e eslint puliti). **Locale, non pubblicata**: serve push; poi si toglie il 17 dal pezzo (oggi ha entrambe le sedi).
- **Foto indossata mancante:** `openai/gpt-5.4-image-2` su OpenRouter rispondeva 200 con errore del fornitore («Complexity 'none' is not supported for this image model»); lo Studio lo nascondeva come «nessuna immagine». Ora `generate_image_with_openrouter` mostra l'errore vero e `generate_showcase_images` prova gli altri modelli supportati (Gemini 3.1 Flash/Pro Image) se il scelto fallisce. Test: 131.
- **Inquadratura anelli/bracciali** (`categorie.RING_FRAMING`): solo il dito e le nocche, mano tagliata a metà, sfondo bello ma sfocato (richiesta di Matteo). Per l'anello M-4T49F la foto indossata è stata rifatta con Gemini 3 Pro Image (la più fedele: pietre con riflessi aventurina) e aggiunta al pezzo (`site_02_worn.jpg`, manifest con copia di sicurezza). **Da inviare di nuovo al sito** dallo Studio (sede 21, 3 foto); è una foto IA: il sito la marca da solo.
- **Modelli immagine aggiornati (7/11/2026, controllati sul catalogo OpenRouter):** i più recenti sono **GPT Image 2.6** (Sunburst = precisione, Flare = velocità, 4/11) e **Nano Banana 2.1** (ottobre); Imagen 3 non è più in elenco. Predefinito ora `google/gemini-nano-banana-2.1` (`.env`, `main.py`, `api/server.py`, menu dello Studio); ordine di riserva: GPT Image 2.6 Sunburst, Gemini 3 Pro, Gemini 3.1 Flash. `openai/gpt-5.4-image-2` e il preview Gemini 3.1 sono «ritirati» (si sostituiscono da soli con il predefinito, anche se salvati nel browser). I GPT Image su OpenRouter non passano da chat/completions ma dall'**API immagini** (`POST /api/v1/images`, foto vera in `input_references`, niente 4:5: si usa 3:4 e si ritaglia): `main.generate_image_with_image_api`, usata anche dal Reel Studio. Prova sull'anello M-4T49F: Nano Banana 2.1 tiene bene pietre e riflessi, GPT Image 2.6 Sunburst la struttura (il gambo dell'anello); costo reale per immagine **non misurato** (stime: Sunburst 0,20 $, Flare 0,12 $).
- **Foto varianti di colore (facoltativa, 7/11/2026):** nuovo campo «Foto delle varianti» in Nuovo pezzo (`varianti`, `--varianti`). La foto vera si ripulisce sul PC come le altre (`site_06_variants.jpg`, pezzo più grande nel riquadro). Se è lunga e stretta (rapporto > 2,2, come un rotolo di anelli) non viene suggerita e l'AI ne propone una messa in ordine (`site_07_variants_ai.jpg`, stesso pezzo su fondo avorio, senza cartellini): **mai spuntata da sola**, con avviso di controllare ogni variante, e marcata «AI» all'invio. Provata sul rotolo di 12 anelli: entrambe le AI sono belle ma **nessuna identica al vero** (il primo anello cambia; Nano Banana trasforma anche l'azzurro in turchese), quindi serve il controllo di Matteo. Il taglio in colonne della foto vera è stato provato e scartato (spezza gli anelli). Test: 139.
- **Anello M-4T49F aggiornato online (7/11, 12:40):** solo via Cavour 21, 4 foto (vera, indossata IA, dettaglio, varianti IA con GPT Image 2.6 Sunburst), badge «AI» solo su indossata e varianti, ancora pubblicato. Il sito rifiutava il reinvio di un pezzo esistente (409; «invia di nuovo» non funzionava): ora `PATCH /api/products/[id]` salva le foto nuove su Blob con nome nuovo (sito, commit 215b477) e lo Studio, su 409, **aggiorna** foto, sedi, prezzo, taglia, categoria e stato, **non** i testi (`_update_existing_showcase_product`). Il file delle varianti AI si allarga ai lati (`export_ratio_jpeg(mode="extend")`) invece di tagliare gli anelli. Test Studio: 140.
- **Video «Chi siamo» (7/11):** `Civico-21-Chi-siamo-V2 mirca` (girato in negozio, **non IA**, 8 s, 9:16, senza audio) nella testata di `/chi-siamo` al posto della foto della vetrina: `chi-siamo-negozio.mp4` (1,5 MB, 576×1024) e copertina; pulsante pausa, parte da solo ma non con «riduci movimento», si ferma fuori schermo (`ChiSiamoVideo`). Se un video è fatto con l'IA va aggiunta l'etichetta «AI» (`AiWearBadge`).
- Lo Studio va riavviato per avere le correzioni.

## Prossimi passi
- **Journey cliente:** decisioni e implementazioni richieste raccolte nel PRD alla radice [brainstorming marketing strategie.md](../brainstorming%20marketing%20strategie.md). WhatsApp centrale del 21, acquisti anche nei DM, quattro videoconsulenze gratuite da negozio, riserve/pagamenti entro 48 ore con due promemoria, cambi commerciali 14 giorni, buoni per sede con registro privato. Stato di questo aggiornamento: documentazione completata; sito, account, registro buoni e collaudi restano da eseguire. La bozza precedente del funnel contiene un rinvio al nuovo riferimento.
- **Tag pietra (17/11/2026):** campo `stoneTags` nella Scheda pezzo (scelto da chi pubblica nello Studio, inviato al sito) per rendere cliccabile la fascia delle pietre in home. Specifica completa in [PLAN_VETRINA.md](../PLAN_VETRINA.md) §2.1, riga J15 del PRD Journey. Da realizzare; serve prima la scelta tra foto vere e immagini AI per le pietre.
- **Studio v2** (restyling, pagina del pezzo, Instagram, motori, movimenti, carosello): piano in `docs/PIANO_STUDIO_V2.md`, Fase A fatta; B–F dopo la prova del weekend e con l'ok di Matteo (prima le decisioni della sezione 0).
0. Prima missione "Scheda pezzo" vera con un gioiello: controllare foto e testi, e quanto costa davvero.
1. Matteo crea l'account e la API key Higgsfield (guida in `docs/reel-studio.md`) e la mette nel `.env` del PC.
2. Primo Reel vero con un prodotto reale: verificare fedeltà del gioiello e costo effettivo vs stima.
3. Tarare le stime (`HF_FALLBACK_USD_PER_SEC_*`) con i costi reali.
4. Matteo: verificare il fuso orario del grafico "Periodi di maggiore attività" dall'app e aggiornare le storie in evidenza (ferme all'estate).
5. Raccogliere da Matteo 2-3 comandi ChatGPT che usa (/poster, /carouselart) e trasformarli in skill.
5b. Matteo: se vuole GPT-Image-2.5, creare `OPENAI_API_KEY` su platform.openai.com (il codice è pronto).
6. Usare la pagina Risultati dopo ogni pubblicazione; più avanti lettura automatica dei numeri con l'API Meta.

## Piano editoriale nello Studio (4/11/2026, pushato su `master`, commit d8e6db7)
- Pagina **Piano** (menu in basso/a sinistra): 2 proposte a settimana con skill, pezzo (foto, prezzo, sede, codice `M-XXXXX`), motivo e brief già pronto; settimana corrente salvata, due successive come anteprima provvisoria. Pulsanti: **Crea** (apre il Reel Studio con skill, pezzo e brief già compilati e segna il contenuto come «creato» quando il Reel parte), **Un'altra idea**, **Salta** (con motivo facoltativo), **Segna pubblicato** (a mano).
- Codice: `piano.py` (regole), `skills/_base/calendario-eventi.json` (calendario modificabile: temi, skill preferite, fascia di prezzo, nessuna promozione), rotte `/piano` in `api/server.py`, `frontend/src/app/piano`. Stato in `memory/piano.json` (nessun dato di clienti). Perimetro e regole: `docs/piano-editoriale-studio.md`.
- Pezzi proposti: solo quelli inviati al sito dallo Studio e risultati pubblicati, con prezzo e foto, non venduti. Prezzo e sede arrivano dal sito (`/api/products/<id>`) e, se non risponde, dall'istantanea salvata al momento dell'invio (`snapshot` nel registro `showcase-drafts`; i pezzi inviati prima di oggi hanno quindi bisogno che il sito risponda).
- Senza chiave AI funziona con brief standard; con la chiave l'AI rifinisce il brief solo se il testo passa gli stessi controlli (chiusura, prezzo, codice, nessuna parola promozionale, nessun giorno promesso).
- Provato: `python -m pytest tests` (130 verdi), build del frontend, pagina nel browser con dati di prova (proposte, «Un'altra idea», «Salta», «Segna pubblicato», «Crea» verso il Reel Studio, console e rete senza errori). Non provato: la creazione di un Reel vero da «Crea» (richiede chiavi e costa), l'aspetto a schermo (il pannello del browser non era visibile) e il collegamento al sito vero con pezzi reali.
- Da fare dopo: versione 2 con i dati della pagina Risultati; il Studio va riavviato per vedere la pagina.

## Sessione del 5/11/2026 (sera): cosa è stato fatto
**Elenco unico di ciò che serve da Matteo:** `docs/interventi-richiesti-matteo.md` (numerato, con le condizioni di sblocco). Da lì si riprende.

**Fatto e online (sito, repo `monili-vetrina`):**
- **Privacy:** richieste senza ordine conservate **un mese** dalla fine del contatto, poi cancellate; documenti fiscali 10 anni (commit 8d1cf2b, con test). Resta da scegliere **chi cancella e come ricordarlo** (Calendly compreso).
- **Immagini IA:** tutte e 6 le immagini dei 2 pezzi online (giacca boho, anello argento 925) marcate `aiGenerated` da Matteo con `scripts/marca_immagini_ia.py`; verificato online (catalogo e badge nelle schede). Le foto reali dei pezzi futuri **non** vanno marcate: lo Studio marca solo quelle IA all'invio.
- **Etichetta IA ridisegnata** (commit 8d4ccb7 e af6bebd): sigla **«AI»** bianca in grassetto 11 px, senza contorno, con ombreggiatura morbida; su tutte le foto/video IA; la frase completa di legge resta per screen reader e tooltip. Tolta la vecchia nota «Video realizzato con l'AI» dell'apertura (duplicava il badge).
- **Reel:** nuovo campo `aiGenerated` per Reel, sigla «AI» in alto a sinistra, interruttore «Creato con l'IA» in `/admin/reels` (commit af6bebd). Matteo ha riferito di aver messo la spunta su «Eleganza Autentica», «Il bomber ricamato sotto i portici», «Dettagli che Parlano di Te» (non ricontrollato dall'AI); «Tempo di Shopping» e «Innamorati del tuo Nuovo Look» non sono IA.
- Controlli prima di ogni push del sito: 41 test, `tsc`, `eslint` verdi.

**Perché «AI» (AI Act art. 50(4), letto il 5/11 su pagina Commissione e riassunti di studi legali, non sul PDF ufficiale):** dal 2/8/2026 vale l'obbligo di dichiarare i deepfake; le linee guida finali includono anche il ritratto fotorealistico di una persona inventata e le immagini commerciali che abbelliscono il prodotto; il Codice di condotta (volontario, giudicato adeguato) indica l'icona UE o una equivalente con la sigla «AI» maiuscola, visibile senza interazioni, anche in un angolo, «chiara e distinguibile»; per il video all'inizio e dopo le interruzioni (visualizzazione continua incoraggiata). **Non è un parere legale:** la forma finale va confermata dal consulente (voce 6 della lista).

**Nello Studio (repo `monili-deploy-temp`):** pushati 63eed2e, 80f5b3b, e13962f (lista interventi, decisioni, script `verifica_consulenza.py` per J07 e `marca_immagini_ia.py`). **Non pushato:** commit 7fec792 e le modifiche successive a questi documenti. Il file `prd per GDPR e AI act.md` resta non tracciato per scelta di Matteo (aggiornato in locale con la sezione del 5/11).

**Decisioni di Matteo del 5/11:** conservazione un mese; hosting **Hobby per ora, poi Pro** (le regole Vercel limitano Hobby all'uso non commerciale: da fare prima di vendere con regolarità); tutte le immagini online marcate IA; etichetta «AI» leggibile; Reel IA indicati uno per uno.

**Controlli sul sito online del 5/11:** 2 pezzi pubblicati (il Piano editoriale e le idee regalo del 16/11 ne hanno bisogno di **8–10**); `/consulenza` 404 per scelta finché non c'è il link Calendly; Calendly Free = un evento, un calendario, 1 a 1, niente automazioni (domande personalizzate, preavviso 3 ore e preparazione 5 minuti da verificare nell'account).

**Prossimi passi per chi riprende:**
1. Matteo: J05 (WhatsApp del 21 su telefono e PC), J06 (Calendly), poi mandare il link → l'AI lancia `python scripts/verifica_consulenza.py` e verifica il sito (J07).
2. Matteo: scegliere chi cancella le conversazioni dopo un mese; pubblicare più pezzi con lo Studio; revisione consulente (condizioni, privacy, forma dell'etichetta IA); J09, J10, J14 e il resto della lista.
3. AI (quando serve): ~~far inviare `aiGenerated: true` dallo Studio~~ **fatto il 6/11 in locale, non pushato** (`_prepare_reel_for_showcase`; `importa_reel.py` con file `nome.ia`; 131 test verdi; Studio da riavviare); ricontrollare online i Reel marcati; pushare i documenti dello Studio solo con l'ok di Matteo.
4. Regole: ogni push del sito va online subito → chiedere conferma; mai dati di clienti nello Studio; nessun widget di terzi.

## Dominio e e-mail (6/11/2026)
- **Dominio `imoniliravenna.it` (Aruba) collegato al progetto Vercel `monili-vetrina` ed è quello principale** (scelta delegata dal titolare). DNS su Aruba: A `@` → 76.76.21.21, CNAME `www` → cname.vercel-dns.com (MX e record `posta` intatti; `ftp` punta a `www`, irrilevante). `www.imoniliravenna.it` reindirizza (308) a `imoniliravenna.it`. `NEXT_PUBLIC_SITE_URL` (Production) = `https://imoniliravenna.it`, redeploy fatto: canonical e og:url verificati online, `/`, `/privacy`, `/cookie`, `/condizioni-vendita` 200 con HTTPS valido. `monili-vetrina.vercel.app` risponde ancora (il `.env` dello Studio lo usa per l'invio: invariato). Il profilo Google resta su `moniliravenna.shop` fino a 10–15 pezzi.
- **Consulenza accesa (6/11):** evento Calendly Free da **15 minuti** (non 10), link `https://calendly.com/moniliravenna/15min`; variabile `NEXT_PUBLIC_CONSULTATION_BOOKING_URL` su Vercel (Production), testi del sito a «quindici minuti» (commit 2bdac71 del sito), `verifica_consulenza.py` TUTTO OK (corretto il controllo di `/cookie`, che non cita «Calendly» ma «il calendario di prenotazione»). Le prove di prenotazione le ha fatte Matteo (riferite). Calendly tiene i dati di prenotazione: vanno cancellati con la regola di un mese (voce 8). Il PRD e il brainstorming citano ancora 10 minuti: da allineare.
- **E-mail ufficiale: `info@imoniliravenna.it`** al posto di `moniliravenna@gmail.com` (sito commit a24f060; verificato online su privacy, condizioni e home; 41 test, tsc, eslint verdi). La casella su Aruba va creata e provata da Matteo (non verificata dall'AI); finché non esiste, le richieste privacy/recesso scritte lì non arrivano. Messaggi pronti in `docs/impegni-legali.md` aggiornati.

## Fatto il 2026-11-17 (Salva per dopo, in negozio)
- **Nuovo modo di lavorare nello Studio**: la pagina «Nuovo pezzo» ha due modi. **Salva per dopo** (il predefinito): in negozio si fanno
  le foto (fino a 8, anche dal rullino) e si scrivono due righe («anello ametista 159 euro, misura 13»); si salva senza AI e senza costi,
  e si può passare subito al pezzo dopo. **Crea subito** è il flusso di prima (foto, scheda, attesa).
- Le bozze stanno in `MoniliStorageozze\<id>\` (foto + `bozza.json`), codice in `bozze.py`, rotte `/bozze` in `api/server.py`.
  Dalla lista «Da lavorare» si apre una bozza, si sceglie la foto **Principale** e il **Dettaglio**, si corregge la nota e si preme
  «Crea la scheda»: parte la Scheda pezzo di sempre (la nota diventa il brief); a fine lavoro la bozza diventa «scheda pronta» con il
  link. Prezzo, misura e pietra si riconoscono dalla nota e si mostrano come etichette (solo in vista: la nota resta com'è).
- Il telefono carica foto ridotte a 2400 px (upload veloce anche in 4G). Eliminare una bozza la sposta in `cestino\`.
- Nessun costo e nessuna chiamata AI finché non si preme «Crea la scheda». Se lo Studio si riavvia mentre una scheda è «in corso»,
  la bozza torna da lavorare con un avviso.
- Sistemata anche la barra in basso sul telefono (cinque voci in quattro colonne: «Altro» andava a capo).
- Test: `tests/test_bozze.py` (6); in totale 146 test verdi.
- **Da fare**: le altre foto oltre Principale e Dettaglio per ora restano nella bozza (non vanno alla scheda); «Pezzi» non elenca ancora le bozze.

## Aperti / da sapere
- **Sito vetrina online dal 30/10/2026**: https://monili-vetrina.vercel.app (repo `monili-vetrina`, progetto Vercel
  `monili-vetrina`, piano Hobby per ora, database e foto nuovi e vuoti). Il `.env` dello Studio sul PC punta già lì.
  Dettagli e prossimi passi in `PLAN_VETRINA.md`, Fase 5.

## Fucina dei prompt (18/11/2026)
- **Cos'è:** nel pezzo salvato ("Salva per dopo") la sezione **Fucina dei prompt**. Si sceglie il modello con cui si creerà la foto (Seedream, Nano Banana, GPT Image), lo Studio analizza la foto e scrive il prompt giusto per quel modello e **si ferma**. La foto si crea a mano su Higgsfield, si ricarica accanto alla foto vera, **Codex** (programma installato sul PC, abbonamento ChatGPT, nessun costo OpenRouter) la confronta con una lista di controllo e propone voto e prompt corretto; il voto finale è di Matteo.
- **Abbigliamento, due passi:** 1) capo addosso alla donna (foto indossata); 2) scelta della foto da animare e **scene video Seedance 2.5** (3 scene, 4-5 s, primo fotogramma = la foto scelta). Il risultato di una scena è un video: Codex lo giudica da 3 fotogrammi.
- **Impara:** voto 4-5 = esempio per i pezzi dello stesso modello; voto 1-2 con nota = errore da non ripetere. Libreria: `MoniliStorage/memory/prompt_lab.json`. Gli esempi sono separati per modello; il flusso automatico vede solo Nano Banana / GPT Image.
- **Conoscenza:** `knowledge/fucina/` (modelli + ricette per categoria + `AGENTS.md` per Codex), con etichette `[verificato]`, `[fonte]`, `[ipotesi]`. Primo seme: da completare con le guide ufficiali di Seedream/Seedance e con le prove vere.
- **Codex:** vedi l'aggiornamento più sotto (Codex 0.170.0, predefinito `gpt-6.1-terra`, scrive anche i prompt).
- Prima versione (poi superata dall'aggiornamento più sotto).

## Obiettivo a regime per le foto del sito (decisione di Matteo, 18/11/2026)
- **Anelli:** 2 foto statiche, il **prodotto pulito e ben illuminato** e l'**anello indossato su una mano realistica**.
- **Abbigliamento:** il **capo indossato** e il **capo pulito da studio, ben illuminato**.
- Il giudizio di Codex nella Fucina valuta ogni foto contro questo obiettivo (`prompt_lab.GOALS`, nel prompt di valutazione); le ricette in `knowledge/fucina/` lo riportano. Da affinare con le prove vere.

## Fucina dei prompt: aggiornamento del 18/11/2026 (sera), PR 13
Ramo `studio-workspace-ux`, PR https://github.com/matteforex82-bit/monili-media-agency/pull/13 (ultimo commit `fde686c`, **non ancora unita a master**). Il PC di Matteo gira già su questo ramo; ogni modifica al backend richiede di riavviare lo Studio (`scripts/start-local.ps1`).
- **Motore dei prompt:** Codex locale (abbonamento ChatGPT di Matteo, niente costi a token), predefinito **`gpt-6.1-terra`** (`fucina_codex.DEFAULT_MODEL`, env `FUCINA_CODEX_MODEL`). Provato con Codex 0.170.0: `gpt-6.2-sol`, `gpt-6.2-astra`, `gpt-6.1-sol` funzionano (con il vecchio 0.144.1 i gpt-6.x davano errore). Analisi e prompt passano da `main.generate_text_with_openrouter` con il prefisso `codex:` (errori sollevati, non nascosti); menu per tornare a OpenRouter. Costi API di riferimento (per milione di token, ingresso/uscita): Luna 0,10/0,50, Terra 1/5, Sol 2/10, Astra 8/40 (Terra e Luna da una pagina vecchia, meno sicuri).
- **Codex guarda tutte le foto del pezzo** (fino a 4: principale, dettaglio, altre) con OpenRouter solo la prima. Il giudizio sul risultato confronta con la sola Principale.
- **Donna nel prompt = `@MODELLA`** (default): la sceglie Matteo a mano (Aurora / `@Modella-Monili-Denti` / altra). Opzione "descritta dall'AI". La missione automatica "Scheda pezzo" continua a inventare una donna per pezzo. Il prompt corretto da Codex mantiene sempre i riferimenti `@...` del prompt usato (`prompt_lab.keep_mentions`).
- **Conoscenza per modello** in `knowledge/fucina/` (seedream, nano-banana, gpt-image, seedance, kling, genjutsu, flux + ricette per categoria + `modella-aurora.md`), costruita da `Learn Higgsfield` (report rivisto il 13/11, prove, costi). Etichette verificato/fonte/ipotesi. Lezioni nuove: la descrizione nel prompt vince sulle foto di riferimento (prova 18/11: giacca verde disegnata al posto della giacca a quadri); il testo nell'immagine esce solo se richiesto, senza "No text" (la Lite non documentata).
- **Interfaccia (idee A, B, C, D, I dell'anteprima https://claude.ai/artifact/Mh3qMZ5khN1pTKxrfV3JVU):** elenco con "prossimo passo" e filtri (`prompt_lab.progress`); il pezzo si apre come spazio di lavoro a passi Foto / Prompt / Generare / Valutare (+ Scene per l'abbigliamento) con una sola azione in una barra fissa in basso (`PieceWorkspace.tsx`, `PromptLab.tsx`, `DraftList.tsx`); impostazioni in una riga ricordate (localStorage `monili_lab_prefs`); miniature di tutte le foto sempre visibili; tasto Copia vicino al prompt. Fix: `overflow-x: clip` su html/body (con `hidden` la barra sticky non restava in basso).
- **Foto fatta altrove:** nel passo Valutare si può caricare e valutare una foto creata con un altro prompt o strumento (attempt `external`, prompt usato facoltativo).
- **Valutazione per tipo di pezzo:** lista di controllo diversa per gioielli (pietre, metallo), abbigliamento (motivo, forma, collo/chiusura, mani) e accessori; nessun punto "mani e corpo" per la foto catalogo; ogni foto è giudicata contro il suo obiettivo (`prompt_lab.GOALS`).
- **Obiettivo a regime per il sito (decisione di Matteo):** anelli = 2 foto statiche (prodotto pulito ben illuminato + anello indossato su mano realistica); abbigliamento = capo indossato + capo pulito da studio ben illuminato.
- **Idee scelte ma non fatte:** F (confronto con zoom al 100%), G (elenco + pezzo affiancati su computer; sconsigliata da me, proposte al suo posto frecce precedente/successivo e "Prossimo da fare"), J completa (un blocco per passo). Non scelte: E (voto con frasi pronte), H (apri Higgsfield).
- **Automazione futura:** a Unlimited finito la generazione si può fare via MCP/CLI/API Higgsfield (consuma crediti, ~0,5 a foto; l'Unlimited vale solo sul sito). Chiavi Higgsfield assenti nel `.env`; non verificato se il tag `@Modella-...` funzioni via MCP/API. Matteo non ha ancora autorizzato la prova (1 foto, ~0,5-2 crediti).
- Test: `python -m pytest tests/test_prompt_lab.py tests/test_bozze.py` (21 passati); suite intera non rilanciata dopo le ultime modifiche. Non provato: tutte le schermate a occhio con il backend nuovo, un'analisi vera con 3 foto, il giudizio di Codex su foto vere dopo il cambio di checklist.

## Fucina: idee F e J (18/11/2026, sera)
- **F, confronto al 100%:** nel passo Valutare il pulsante «Zoom al 100%, una accanto all'altra» apre foto vera e risultato a grandezza reale, in due riquadri che scorrono insieme (si chiude con Esc o «Chiudi»). Solo per le foto, non per i video (`ZoomCompare` in `PromptLab.tsx`).
- **J, un blocco per passo:** nel passo Valutare ogni prova ha tre blocchi numerati: 1 Confronta, 2 Codex, 3 Il tuo voto.
- Verificato: `npx tsc --noEmit` pulito. **Non provato a schermo** (zoom e scorrimento sincronizzato da vedere con lo Studio riavviato).

## Riprogettazione del percorso Studio: Fase 1 in corso (18-19/11/2026, ramo `studio-percorso-unico`)
Piano completo approvato in `C:\Users\matte\.claude\plans\dopo-questo-vorrei-insieme-glistening-hummingbird.md` (scelte: un solo percorso per pezzo, Aurora testimonial fissa, due foto base studio+indossata, libreria di clip proprie per Genjutsu, fonte unica in `knowledge/`, costi con stima+OK+tetto).
Fatto finora:
- **Bug categoria:** una foto fatta altrove su un pezzo mai analizzato veniva giudicata con i criteri dei gioielli; ora riceve la categoria (modulo + nota). Giudizio con ordine di importanza (fedeltà all'originale per prima).
- **Valutazione per tipo di pezzo:** `knowledge/valutazione/valutazione-<tipo>.md` (anello, orecchini, collana, bracciale, capo, borsa, foulard), letti da `prompt_lab.goal_for`; tipo riconosciuto da `categorie.subtype_from`. `knowledge/come-si-indossa.md` (solo documento).
- **Fonte unica del brand:** `knowledge/brand.md` (letto da `main.BRAND`), niente giorni fissi, hashtag Scheda 3+2 e Reel 3+5 (il 5 è una scelta da verificare con i Risultati), chiave `sessions` corretta.
- **Aurora testimonial fissa** (`skills/_base/donne.md`, sezione Testimonial) in Scheda pezzo e Reel; `CLAUDE.md` allineato. La quota «un contenuto su tre senza volto» è solo scritta, non applicata dal codice.
- **Foto per canale:** `channels.py` + `knowledge/formati-canali.md`, `GET /canali` e `/bozze/{id}/prove/{id}/canale/{canale}`, link «Scarica per canale» nel passo Valutare. Le misure di Google e Tripadvisor sono `[fonte]` (siti di terzi), da verificare sulle pagine ufficiali.
- **Testi per piattaforma:** `knowledge/testi/*.md` (stile umano da skill humanizer, sito, WhatsApp, Google Business, Instagram, Tripadvisor) iniettati nel prompt dei testi; nuovo campo `tripadvisor_text` nella Scheda. Non passa ancora da un secondo giro di riscrittura con la skill: solo regole nel prompt.
- Test: 167 passati, `tsc` pulito. Non provato a schermo né con generazioni vere.
- **Vai al sito (19/11):** pulsante nel passo Valutare, indipendente dal voto: la foto (catalogo o indossata) diventa foto del sito 4:5 del pezzo (`POST /bozze/{id}/prove/{id}/sito`), nella stessa scheda del pezzo (creata se non c'è); la foto catalogo AI porta ora l'etichetta «AI». Il pezzo creato così non ha ancora i testi (Fase 2).
Fase 1 completata. Da fare: Fase 2 (percorso unico bozze+pezzi) e Fase 3 (automazione MCP).

## Fucina: «Impara dai miei voti» (19/11/2026)
- Nel passo Prompt, pannello **«Cosa ha imparato lo Studio»** (`LearnPanel.tsx`). «Impara dai miei voti» (servono 3 foto votate) manda a Codex (o OpenRouter) i voti, le note e i prompt della libreria e raccoglie da 1 a 5 **regole proposte**. Matteo le corregge, **approva o scarta**; solo le approvate entrano nei prompt (`prompt_lab.approved_rules`, dentro `hints`), per il modello e il tipo di pezzo indicati (vuoto = tutti). Archivio: `MoniliStorage/memory/regole_fucina.json`. Rotte: `/fucina/regole` (GET, `/proponi`, PUT e DELETE per id).
- Il voto di Codex resta un suggerimento: contano i voti e le note di Matteo. I prompt votati 4-5 portano ora anche la nota («perché è piaciuto»); quelli senza prompt sono ignorati. Tolto «Scarica per canale» dal passo Valutare (l'export `/bozze/.../canale/...` resta nel backend).
- Test 170 passati. Non provato a schermo (serve riavviare lo Studio).
