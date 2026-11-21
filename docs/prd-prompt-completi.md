# Mini PRD — Prompt completi per tutti i prodotti

Stato: bozza rivista dopo controllo di un advisor (20/11/2026), da approvare. Branch: `studio-percorso-unico`.

## Obiettivo

Ogni generazione dello Studio (foto sito, fotogrammi per i video, post con testo, testi) legge la knowledge giusta ed è pronta per tutti i prodotti venduti: anelli, orecchini, collane, bracciali, cavigliere, borse, pochette, sciarpe, foulard, cinture, cappelli, occhiali, abbigliamento. Poi Matteo prova con contenuti veri e si corregge in corsa.

## Due percorsi

1. **Foto per il sito:** una foto base (fondo uguale per tutti) e una indossata (mano o modella secondo il prodotto) che compare al passaggio del mouse.
2. **Contenuti per Instagram:** (a) fotogrammi per i video (Genjutsu, Seedance, Kling); (b) post statici con testo italiano, fatti con GPT Image o Nano Banana.

## Fuori scope

- Storyboard a 6 o 12 riquadri come output (restano solo esempio).
- Prove reali su Higgsfield e voti: vengono dopo, con Matteo.
- Merge in master, push e deploy senza un sì esplicito. Il PRD non si committa se Matteo non lo chiede.

## Decisioni aperte (con il mio default)

| # | Domanda | Default proposto |
|---|---------|------------------|
| D1 | Prezzo sul post | Lo inserisce chi pubblica prima di generare; se vuoto, non compare |
| D2 | Logo ed etichette (nomi pezzi, prezzi) | Messi dal codice sull'immagine; il titolo lo disegna l'AI e il codice rilegge il testo per controllo |
| D3 | Le immagini 4-7 che hai allegato (anello + bracciale, "Look 1", "Look 2") sono un carosello? | Sì, un carosello da più immagini con stile coerente (rubrica "3 modi di indossarlo") |
| D4 | Fondo della foto base | Pezzo scontornato (già c'è: `photo_cleanup.py`) e incollato su uno sfondo fisso, non un fondo inventato dall'AI a ogni foto |
| D5 | Modello per i post con testo | GPT Image di default; scelta solo tra GPT Image e Nano Banana |

## Dati verificati nel repo (20/11)

- `categorie.subtype_from` e `prompt_lab.review_sheet` già usano `subtype` con 7 valori: anello, orecchini, collana, bracciale, capo, borsa, foulard. Oggi sciarpa, cintura, cappello e occhiali finiscono in "foulard" e la cavigliera in "bracciale".
- `photo_cleanup.py` scontorna con BiRefNet e compone su fondo avorio (`ivory_background`, `compose`).
- Il logo vero è `assets/logo-monili.png`.
- Le foto sito sono `site_01_product_clean.jpg` (base), `site_02_worn.jpg` (indossata), `site_04_worn_2.jpg`; fatte da `generate_image_with_fallback`, che prova in silenzio tutti i modelli e fissa il 4:5.
- In `knowledge/fucina/` c'è `modella-aurora.md` ma da controllare se ci sono foto di riferimento di Aurora da mandare ai modelli.

## Task

Ordine: T1 → T2 → T3 → T4 → T5a/b/c → T6 → T7 → T8. T1, T2 e T7 sono la rete di sicurezza e si fanno prima delle altre.

### T1 — Tipi di prodotto completi (riuso di `subtype`)
- **Cosa:** estendere `SUBTYPE_WORDS` in `categorie.py` e le chiavi di `review_sheet` invece di creare un campo parallelo. Nuovi tipi: cavigliera, pochette, sciarpa, cintura, cappello, occhiali (separati da foulard e bracciale).
- **Chi sceglie il tipo:** dedotto dall'analisi e dal nome; Matteo lo conferma o lo cambia nell'interfaccia (campo "Tipo di pezzo" nella scheda pezzo).
- **Pezzi già esistenti:** se non hanno il tipo, ricadono sulla categoria, come oggi.
- **Capo:** distinguere sopra, sotto e figura intera (cambia l'inquadratura indossata).
- **Dove:** `categorie.py`, `prompt_lab.py`, `api/server.py` (riga ~1857), `frontend/src/components/PieceView.tsx`.
- **Fatto quando:** per ogni tipo si sa quale ricetta, inquadratura (mano, polso, caviglia, collo, orecchio, spalla, vita) e scheda usa; nessun tipo cade nel valore generico per errore.
- **Verifica:** test T7; `tests/test_prompt_lab.py` resta verde.

### T2 — Knowledge mancante per tipo
- **Cosa:** schede in `knowledge/valutazione/` per cavigliera, pochette, sciarpa, cintura, cappello, occhiali; ricette in `knowledge/fucina/` con regole di inquadratura e scala per tipo (borsa: dimensione rispetto al corpo; sciarpa: come cade; cavigliera: caviglia nuda).
- **Fatto quando:** ogni tipo ha una scheda con sezioni `studio` e `indossata`; i test sulle intestazioni non si rompono.
- **Verifica:** `python -m pytest tests/test_prompt_lab.py`.

### T3 — Foto sito: base e indossata per tutti
- **Foto base uguale per tutti:** non basta un prompt, perché ogni foto uscirebbe con avorio, ombra e scala diversi. La base si fa dal pezzo scontornato (BiRefNet) incollato su uno sfondo fisso in codice, con margini e scala del pezzo fissi per tipo. Il percorso AI resta solo come ripiego se lo scontorno non è buono.
- **Indossata:** l'inquadratura (mano o modella) viene dal tipo di T1.
- **Stesso ritaglio 4:5** per base e indossata, perché il passaggio del mouse non deve "saltare". Controllare quale file il sito usa come principale e quale come hover, e che l'ordine di invio coincida.
- **Aurora:** nei prompt indossata mandare le foto di riferimento di Aurora (`generate_image_multi` in `reel_kit.py`), non solo la descrizione, altrimenti il volto non resta coerente.
- **Dove:** `main.py` (`agent_scheda_plan`, `controlled_site_prompt`, `SITE_IMAGE_SPECS`), `photo_cleanup.py`, `categorie.py`.
- **Fatto quando:** due pezzi diversi producono foto base con lo stesso sfondo e la stessa scala; per ogni tipo il prompt indossata contiene scheletro, ricetta e guida del tipo.
- **Verifica:** test T7; controllo a occhio di Matteo nei test reali.

### T4 — Fotogrammi per i video e storyboard collegati alla knowledge
- **Cosa:** far leggere a `agent_storyboard` (`reel_studio.py`) lo scheletro del prompt video, la regia per tipo, le schede Seedance e Kling e la lista difetti video; aggiungere le scene per gioielli (macro lenti, orbit leggero) e per borse e sciarpe (si apre, si porta, cade il tessuto).
- **Genjutsu:** è in `MODEL_FILES` ma non si può ancora scegliere; renderlo selezionabile come motore dei video.
- **Fotogramma chiave (immagine):** `keyframe_prompt_en` è un prompt immagine in 9:16, quindi deve leggere anche lo scheletro foto e la scheda del modello immagine, non solo la knowledge video.
- **Dove:** `reel_studio.py`, `prompt_lab.py` (`scenes_prompt`, `MODELS`), `knowledge/fucina/regia-reel.md`.
- **Fatto quando:** il prompt dello storyboard contiene le sezioni della knowledge e le regole del tipo; le regole scritte a mano che le duplicano sono tolte.
- **Verifica:** test T7; i test del Reel restano verdi.

### T5a — Post "Outfit con prezzi" (foto reale + etichette)
- **Cosa:** parte da una foto reale del flat-lay. Nomi dei pezzi e prezzi si disegnano in codice sulla foto (font serif corsivo, posizione scelta da chi pubblica). Nessuna rigenerazione AI: i prodotti non cambiano e l'immagine non è AI.
- **Dati:** più pezzi insieme, ognuno con prezzo, riferimento e sede (17 o 21); l'inserimento lo fa chi pubblica. Il WhatsApp è sempre il numero centrale del 21.
- **Fatto quando:** da una foto e un elenco di pezzi esce l'immagine con le etichette giuste, senza prezzi inventati.

### T5b — Post "Titolo editoriale" e "Look con la modella"
- **Cosa:** immagine fatta con GPT Image o Nano Banana a partire dalla foto reale; titolo in serif elegante su fondo caldo, mai fumetto o neon. Per il look con la modella si mandano le foto di riferimento di Aurora.
- **Testo e logo:** il logo vero (`assets/logo-monili.png`) si sovrappone in codice, perché l'AI inventa loghi diversi ogni volta. Matteo approva o corregge il testo proposto prima di generare. Dopo la generazione il modello visivo rilegge il testo sull'immagine e il codice lo confronta lettera per lettera (accenti è, à; "29€"; frase di chiusura "Scrivici, ti diciamo se è disponibile"); se non coincide, rigenera o scrive il testo in codice.
- **Regole:** `divieti.md` e `never_show`, identità visiva del `CLAUDE.md`; mai "te lo mettiamo da parte".
- **Etichette:** ogni immagine realistica generata dall'AI, anche il prodotto sulla pietra senza modella, è marcata `aiGenerated` e porta il promemoria "Info sull'AI" per Instagram.
- **Modello:** solo GPT Image o Nano Banana, con il modello usato mostrato a schermo; formato 1080×1350 per i post, 9:16 per le Storie. Si evita `generate_image_with_fallback` così com'è (prova tutti i modelli in silenzio e fissa il 4:5).

### T5c — Carosello (se D3 è sì)
- **Cosa:** `PublishHub` (tab Post) accetta più immagini, in ordine, con stile coerente tra le slide (stesso fondo, stessi caratteri). Pensato per "3 modi di indossarlo" e "Perché stanno bene insieme".
- **Fatto quando:** da un pezzo si ottiene un carosello di 3 slide con la didascalia unica e il copia-incolla funziona.

### T6 — Testi e copertina collegati alla knowledge
- **Cosa:** verificare che `agent_copy`, `agent_publish_pack` e `poster_prompt` leggano `knowledge/testi/*` e le regole del `CLAUDE.md`; collegare dove mancano.
- **Dove:** `reel_studio.py`, `main.py`, `reel_kit.py`.
- **Fatto quando:** i prompt contengono le regole del canale (Instagram, WhatsApp, Google Business, sito) e il tono; un test lo controlla.

### T7 — Test di copertura per prodotto
- **Cosa:** un test senza rete né chiavi che per ogni tipo di prodotto costruisce i prompt finali (foto sito, scene video, post con testo) e controlla che contengano ricetta, scheletro, regole del tipo e divieti del brand.
- **Budget di lunghezza:** controllare anche che nessun prompt superi il limite quando si aggiungono knowledge (già successo: `seedance.md` tagliato da 1327 a 919 parole).
- **Fatto quando:** il test passa per tutti i tipi e fallisce se si aggiunge un tipo senza scheda.
- **Verifica:** `python -m pytest tests` completo verde.

### T8 — Pacchetto di prova per Matteo
- **Cosa:** elenco di 5-6 test pronti (anello, orecchini, borsa, sciarpa o foulard, capo, un post con testo) con il pezzo, il modello e cosa guardare; ogni scheda di knowledge ha il campo "verificato / da verificare / voto" da aggiornare dopo i test.
- **Fatto quando:** Matteo lancia i test senza preparare nulla e sa dove annotare l'esito.

## Dopo questo PRD

Test reali con voti e correzione in corsa; seconda testimonial dopo 6 settimane; test instabili (non riprodotti il 20/11); aggiornare titolo e descrizione della PR #14.

## Rischi

- Il testo italiano nelle immagini AI può avere errori: per questo c'è l'approvazione prima e la rilettura dopo.
- Le foto con la modella restano AI: `aiGenerated` e "Info sull'AI" su Instagram.
- Aggiungere tipi di prodotto tocca più file: T7 è la rete di sicurezza.
