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

## Ricette ("comandi" alla Monili)

Come i comandi `/poster` di ChatGPT, ma tarati sul negozio. Si scelgono nel modulo e il regista segue la struttura fissa:

| Ricetta | Cosa fa |
|---|---|
| `/libera` | il regista sceglie la struttura migliore |
| `/modella-monili` | la Modella Monili indossa il prodotto: hook, dettaglio, look, chiusura |
| `/mani-bancone` | mani che prendono e provano il gioiello al bancone (anelli, bracciali), niente volto |
| `/pietra-settimana` | una pietra: significato e abbinamento |
| `/tre-modi` | lo stesso pezzo in 3 look: giorno, ufficio, sera |
| `/colori-ravenna` | il gioiello accostato ai colori dei mosaici di Ravenna |

Le ricette sono in `reel_kit.py` (`RECIPES`): per aggiungerne una basta un nuovo blocco.

## Modella Monili

Un solo volto AI ricorrente, sempre la stessa donna. Si imposta una volta: descrizione (in inglese rende meglio) +
foto di riferimento. Il modo più semplice: fai un primo Reel con `/modella-monili`, poi nel risultato tocca
**"Usa come Modella Monili"** sul fotogramma che ti piace. Da lì ogni scena con la modella usa quella foto come
riferimento. Dati in `memory/modella_monili.json`, foto in `output/brand/modella_monili.jpg`.

Su Instagram, per contenuti AI realistici, attiva l'etichetta **"Info sull'AI"** quando pubblichi.

## Controllo qualità

Ogni fotogramma AI viene confrontato con la foto reale del prodotto (forma, pietre, colori, metallo, difetti
come rettangoli neri o dita deformate). Se il voto è sotto 6/10 viene rigenerato una volta; se è ancora diverso
il risultato mostra **"Controlla prima di pubblicare"**. Anche la copertina poster viene controllata (testo
scritto giusto + prodotto).

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
   - **su Render**: servizio `monili-backend` → Environment → aggiungi `HF_API_KEY_ID` e `HF_API_KEY_SECRET`.
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
- **Render free** (512 MB, file temporanei) va bene per provare. Per l'uso quotidiano usa la **modalità locale**
  (`scripts/start-local.ps1`): video e archivio restano sul portatile.

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
| GET/POST | `/reel/persona` | leggi / salva la Modella Monili (descrizione + foto) |
| POST | `/reel/persona/from-keyframe` | usa un fotogramma (`reel_id`, `shot_id`) come Modella Monili |
