# Skill dei contenuti Monili

Ogni file `.md` in questa cartella è una **skill**: una ricetta che l'app usa per creare un contenuto
(Reel o Story video). Per aggiustare il risultato basta cambiare il testo, il codice non si tocca.

## Come è fatto un file

```
---
label: Nome mostrato nell'app
description: una riga che spiega a cosa serve
formats: reel, story          # formati in cui si può usare
uses_model: true              # true = compare una donna (una per pezzo, vedi _base/donne.md)
default_seconds: 12           # durata suggerita
---
## Struttura        → la scaletta che il regista AI deve seguire (inquadratura per inquadratura)
## Fotogramma       → note extra per le immagini di partenza di ogni scena
## Movimento        → note extra per l'animazione video
## Testi            → note extra per caption, hashtag e testi a schermo
## Copertina        → note extra per la copertina poster
```

Le sezioni sono tutte facoltative tranne **Struttura**. Il nome del file diventa il comando
(es. `pietra-settimana.md` → `/pietra-settimana`).

## Le basi comuni (`_base/`)

- `fotogramma.md` — il modello di prompt per ogni immagine di partenza (vale per tutte le skill)
- `movimento.md` — il modello di prompt per l'animazione Higgsfield
- `copertina.md` — il modello della copertina poster
- `testi.md` — le regole per caption, hashtag e chiusure
- `donne.md` — la linea guida per la donna che indossa i pezzi: la inventa l'AI, una per pezzo, reale ed elegante.
  Vale per i Reel e per la foto indossata della Scheda pezzo
- `divieti.md` — "Mai nei contenuti": le cose da non mostrare mai, in foto e Reel. È l'unico posto dove si mettono
  limiti; luoghi, donne e pose restano liberi, per non diventare monotoni

Nei modelli le parole tra graffe (es. `{scene}`) vengono riempite dall'app: non cancellarle.

## Dove si modificano

- **Dall'app**: pagina **Skill** (link in alto nel Reel Studio). Le modifiche vengono salvate nello storage
  (`MoniliStorage/skills/`) e hanno la precedenza su questi file; "Ripristina originale" le annulla.
- **Da GitHub / da Claude o Hermes**: modificando direttamente questi file.

Le tecniche usate vengono dalla ricerca in `knowledge/ricerca_marketing_ai_2026.md`.
