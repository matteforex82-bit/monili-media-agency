# Reel Studio — video-first per I Monili

Pagina: `/reel` (link "Reel Studio" in alto nella pagina principale).

## Flusso

1. **Carichi** 1-3 foto del prodotto + (facoltativo) fino a 3 clip vere girate col telefono (MP4/MOV) + brief.
2. **Analista + Regista AI** (OpenRouter, `gpt-5.5`) creano lo **storyboard**: hook dei primi 1,5 s,
   3-5 inquadrature con fonte (scena AI o clip reale), camera, angolazione, luce, transizione, testo a schermo,
   mood musicale e copertina.
3. **Approvi o modifichi** lo storyboard: ordine, durata, fonte, testi, prompt. Vedi il **costo stimato in €**
   per ogni inquadratura. Sopra il budget (`REEL_BUDGET_EUR`, default 2 €) l'app chiede conferma.
4. **Produzione** (fino a 3 inquadrature in parallelo):
   - fotogramma chiave 9:16 generato **dalla foto reale** (oppure la foto reale stessa per la massima fedeltà);
   - video AI con Higgsfield (Kling 3.0 Std/Pro o Seedance 2.5);
   - le clip reali vengono tagliate e portate a 1080×1920;
   - montaggio finale MP4 9:16 30 fps con transizioni (ffmpeg incluso via `imageio-ffmpeg`).
5. **Testi**: caption, hashtag (sempre `#imoniliravenna #ravenna #romagnastyle`), primo commento, copertina,
   sticker per le stories, audio consigliato, orario. Anche in `testi.md`.

Il video è **senza audio**: l'audio lo scegli tra quelli di tendenza nell'editor di Instagram, che premia
gli audio trending.

## Skill (ricette modificabili)

Le ricette sono file di testo in `skills/` (guida completa in `skills/README.md`). L'app le rilegge a ogni
video: per aggiustare un risultato si cambia il testo, non il codice. Si modificano anche dall'app, nella
pagina **Skill** (link in alto nel Reel Studio): le modifiche vanno nello storage e "Ripristina originale" le annulla.

| Skill | Cosa fa |
|---|---|
| `/libera` | il regista sceglie la struttura migliore |
| `/indossato` | una donna vera, una per pezzo, indossa il prodotto: hook, dettaglio, look, chiusura (ex `/modella-monili`) |
| `/mani-bancone` | mani che prendono e provano il gioiello al bancone (anelli, bracciali), niente volto |
| `/pietra-settimana` | una pietra: significato e abbinamento |
| `/tre-modi` | lo stesso pezzo in 3 look: giorno, ufficio, sera |
| `/colori-ravenna` | il gioiello accostato ai colori dei mosaici di Ravenna |
| `/prima-dopo` | look semplice → con un solo accessorio Monili |
| `/nuovo-arrivo` | presentazione veloce di un pezzo appena arrivato (Storie) |
| `/idea-regalo` | il gioiello come regalo per una persona precisa (Natale e ricorrenze) |
| `/countdown-natale` | Story "mancano X giorni a Natale" con un pezzo al giorno (dal 1° dicembre) |

Il calendario fino a Natale con skill, date verificate e brief pronti è in `docs/piano-natale-2026.md`.

Basi comuni in `skills/_base/`: `fotogramma.md`, `movimento.md`, `copertina.md`, `testi.md`, `donne.md`.

## Coerenza prodotto e scena

1. **Scena unica**: lo storyboard contiene una `scene_bible` (luogo, luce, palette, abiti della donna) che
   entra in ogni fotogramma ed è modificabile nello storyboard.
2. **Fotogramma guida**: i fotogrammi si creano in sequenza; il primo riuscito (di preferenza con la donna)
   diventa il riferimento di scena per tutti gli altri.
3. **Controllo severo** (soglia `REEL_QA_MIN_SCORE`, default 8/10): prodotto identico + scena coerente + nessun
   difetto. Fino a `REEL_KEYFRAME_ATTEMPTS` tentativi (default 3), ognuno con il motivo dello scarto precedente.
4. **Se nessun tentativo passa, l'app usa la foto reale** del prodotto: un gioiello sbagliato non entra mai
   nel video. Il risultato lo segnala ("Prodotto protetto").
5. **Chiusura sulla foto vera**: con "Finisci la scena sulla foto vera" la foto reale diventa il fotogramma
   finale del video Higgsfield (`last_image_url` / `end_image_url`).

## Motore immagini

| Motore | Quando |
|---|---|
| GPT-Image-2 via OpenRouter | default oggi (usa `OPENROUTER_API_KEY`) |
| **GPT-Image-2.5 Flare** (OpenAI diretto) | default automatico se c'è `OPENAI_API_KEY`: qualità superiore, metà latenza |
| **GPT-Image-2.5 Sunburst** (OpenAI diretto) | usato per le copertine poster quando c'è `OPENAI_API_KEY` |
| Gemini Flash / Pro Image | alternativa più economica / veloce |

La chiamata OpenAI usa `/v1/images/edits` con le immagini di riferimento numerate, formato 1152×2048 (9:16,
multipli di 16) e qualità `OPENAI_IMAGE_QUALITY` (default `high`). Si sceglie nel modulo ("Motore immagini").

## Risultati (pagina `/risultati`)

2-3 giorni dopo la pubblicazione si inseriscono i numeri dagli Insights di Instagram (visualizzazioni, invii,
DM, visite in negozio...). La pagina mostra cosa funziona per skill, formato, giorno e fascia oraria; con almeno
2 contenuti per gruppo questi dati entrano nei prompt di regista e copywriter. File:
`<storage>/memory/risultati_contenuti.json`.

## Chi indossa i pezzi

Niente modella fissa, ma **una donna per pezzo** (scelta del 29-30/10/2026): bella ed elegante ma reale, con età,
corpo e viso da persona normale, come se per quel pezzo avessimo ingaggiato una modella. Mai lo stesso pezzo con
due donne diverse; da un pezzo all'altro cambia.

- La inventa la **Scheda pezzo** per la foto indossata (campo `woman` del piano, linea guida in
  `skills/_base/donne.md`) e la salva nei risultati (`woman`).
- **"Fai il Reel di questo pezzo"** apre `/reel?pezzo=<run_id>`: il Reel prende la stessa descrizione e copia la
  foto indossata in `input/donna.jpg`, usata come riferimento del viso nelle scene con la donna. Anche il pezzo
  del sito viene già scelto quando si pubblica il Reel.
- Un Reel creato senza scheda: la inventa il regista nello storyboard e resta salvata in `woman` di `reel.json`.
- Dentro il Reel resta la stessa in tutte le scene (fotogramma guida).

## Libertà creativa e divieti

Scelta del 30/10/2026: per non diventare monotoni l'AI inventa luoghi, donne, pose e abiti adatti al pezzo e allo
stile del negozio. Due cose aiutano la varietà: regista e piano della scheda ricevono le **donne e le scene usate
di recente** da non ripetere (`casting.recent_women` / `recent_scenes`, lette da schede e Reel salvati). L'unico
limite fisso è l'elenco **"Mai nei contenuti"** (`skills/_base/divieti.md`, modificabile dalla pagina Skill), che
entra nel piano della scheda, nelle sue foto, nello storyboard e in ogni fotogramma.

Su Instagram, per contenuti AI realistici, attiva l'etichetta **"Info sull'AI"** quando pubblichi.

## Controllo qualità

Vedi "Coerenza prodotto e scena" sopra. Anche la copertina poster viene controllata (testo scritto giusto +
prodotto); se non passa resta disponibile la copertina foto.

## Copertina poster

Opzione attiva di default: copertina 9:16 in stile editoriale Monili (serif su fondo crema, come
"Non sono semplici orecchini."). C'è sempre anche la copertina foto semplice come alternativa.

## Modalità anteprima (senza Higgsfield)

Senza API key Higgsfield tutto il flusso funziona lo stesso: le scene AI diventano un lento zoom sul fotogramma
chiave. Costano solo i testi e i fotogrammi su OpenRouter (pochi centesimi). È utile per provare storyboard e
testi prima di attivare i video veri.

## Come creare la API key Higgsfield

1. Vai su <https://console.higgsfield.ai> e crea un account (o entra con quello di higgsfield.ai).
2. Ricarica crediti API dalla console. I crediti scadono dopo 12 mesi: all'inizio compra poco.
3. Sezione **API keys** → crea una nuova chiave → copia **Key ID** e **Secret**. Il secret si vede una volta sola.
4. Inseriscile **solo nel backend**, mai nel frontend:
   - **in locale**: nel file `.env` nella cartella del progetto
     ```
     HF_API_KEY_ID=...
     HF_API_KEY_SECRET=...
     ```
5. Riavvia il backend: in alto nella pagina Reel compare **"Higgsfield attivo"** e le stime diventano quelle
   ufficiali (endpoint `/estimate` di Higgsfield).

## Costi (indicativi)

| Voce | Stima |
|---|---|
| Fotogramma chiave AI (gpt-5.4-image-2) | ~0,10 € |
| Video Kling 3.0 Standard | ~0,09 €/secondo (stima prudente finché non c'è la key) |
| Controllo qualità per fotogramma | ~0,02 € |
| Copertina poster | ~0,12 € |
| Testi e regia | ~0,09 € |
| **Reel 12-14 s, 4 inquadrature** | **~1,2-1,9 €** |

I lavori falliti o bloccati dalla moderazione non vengono addebitati da Higgsfield.

## Limiti da conoscere

- **I gioielli piccoli sono il punto debole dei video AI**: pietre e montature possono deformarsi col movimento.
  Per questo: movimenti lenti, prompt di fedeltà e la possibilità di usare la **foto reale** come fotogramma
  (opzione "Foto reale (massima fedeltà)"). Controlla sempre il risultato prima di pubblicare.
- I video su Higgsfield restano disponibili 7 giorni: l'app li scarica subito nello storage.
- Lo Studio gira sul PC (`scripts/start-local.ps1`): video e archivio restano lì. Render è stato dismesso il 30/10/2026.

## Dove finiscono i file

```text
<storage>/output/reels/<id>/
  reel.json        stato completo (storyboard, stima, log, risultati)
  input/           foto e clip caricate
  shots/           fotogrammi chiave e clip per inquadratura
  monili_reel_<id>.mp4
  cover.jpg
  testi.md
```

## API backend

| Metodo | Percorso | Cosa fa |
|---|---|---|
| GET | `/reel/config` | stato Higgsfield, modelli, budget |
| POST | `/reel/create` | multipart `photos[]`, `clips[]`, `brief`, `format` (reel/story), `target_seconds`, `video_model` |
| GET | `/reel/{id}` | stato, storyboard, stima, log, risultati |
| PUT | `/reel/{id}/storyboard` | salva le modifiche e ricalcola la stima |
| POST | `/reel/{id}/render` | avvia la produzione (`confirm_over_budget` se sopra budget) |
| GET | `/reels` | archivio |
| GET | `/results` | numeri registrati, riepilogo e video da completare |
| PUT/DELETE | `/results/{id}` | salva / elimina i numeri di un contenuto (`id` del reel o `manuale-...`) |
| GET | `/skills` | elenco skill e basi |
| GET/PUT/DELETE | `/skills/{id}` (`?base=true` per le basi) | leggi / salva / ripristina originale |

## Test

```
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests
```
I test girano senza chiavi e senza internet (AI simulata, storage temporaneo).
