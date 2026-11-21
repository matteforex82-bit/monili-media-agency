# Pacchetto di prova: prompt completi per tutti i prodotti

Creato il 20/11/2026 con il PRD `docs/prd-prompt-completi.md`. Serve a provare con contenuti veri quello che lo Studio ora scrive, senza preparare niente: si sceglie il pezzo, si lancia, si guarda e si annota l'esito.

## Prima di cominciare (una volta sola)
1. **Foto di Aurora**: copia 1 o 2 foto "master" di Aurora (volto neutro, senza gioielli, luce morbida) in `C:\Users\matte\MoniliStorage\aurora-riferimenti\`. Le candidate sono in `MoniliStorage\Dataset_Modella_Monili` (es. `A01_...`, `B01_frontale-...`): la scelta è tua. Se la cartella è vuota, lo Studio usa solo la descrizione scritta, come prima.
2. Riavvia il backend (porta 8000), così legge il codice nuovo.

## I 6 test
| # | Cosa | Dove nello Studio | Modello | Cosa guardare |
|---|------|-------------------|---------|---------------|
| 1 | Anello | Nuovo pezzo, Tipo di pezzo = Anello | Nano Banana (default) | Foto base: stessa scala di un altro anello. Indossata: solo dito e nocche, pietra giusta |
| 2 | Orecchini | Nuovo pezzo, Tipo = Orecchini | Nano Banana | Indossata: profilo, capelli dietro l'orecchio, lunghezza giusta del pendente; volto di Aurora coerente |
| 3 | Borsa | Nuovo pezzo, Tipo = Borsa | GPT Image | Scala sul corpo (fondo della borsa al fianco), due manici, cuciture continue |
| 4 | Sciarpa o foulard | Nuovo pezzo, Tipo = Sciarpa / Foulard | GPT Image | Il disegno non cambia scala nelle pieghe, frange integre |
| 5 | Capo (gonna o giacca) | Fucina: Tipo = Capo, "Che capo è" = Sopra o Sotto; poi scene video con Kling o Genjutsu | Seedream + Kling | Inquadratura giusta per il taglio; scene video che rispettano durata e movimento sicuri |
| 6 | Post con testo | Pezzo → Pubblica → Instagram Post → Crea un post con testo: Titolo editoriale, poi Carosello | GPT Image, poi Nano Banana | Titolo identico lettera per lettera (accenti!), logo vero, prezzo della scheda, nessuna cifra inventata; 3 slide coerenti |

Bonus senza AI: **Outfit con prezzi** (foto vera del flat-lay + nomi e prezzi): controlla posizione e leggibilità delle etichette.

## Dove annotare l'esito
- **Foto e video**: nella Fucina, con il voto da 1 a 5 e la nota (finiscono nella libreria e insegnano le regole).
- **Schede di valutazione**: in fondo a ogni `knowledge/valutazione/valutazione-<tipo>.md` c'è "## Esito prove": scrivi stato (verificato / da verificare), voto, data e una nota.
- **Ricette e modelli** (`knowledge/fucina/*.md`): entrano interi nei prompt, quindi l'esito si scrive qui sotto, non nel file.

| File della fucina | Stato | Voto | Data | Note |
|-------------------|-------|------|------|------|
| inquadratura-tipi.md | da verificare | - | - | - |
| ricetta-bijoux.md | da verificare | - | - | - |
| ricetta-accessori.md | da verificare | - | - | - |
| ricetta-abbigliamento.md | da verificare | - | - | - |
| gpt-image.md | da verificare | - | - | - |
| nano-banana.md | da verificare | - | - | - |
| seedream.md | da verificare | - | - | - |
| seedance.md / kling.md / genjutsu.md | da verificare | - | - | - |
| regia-reel.md | da verificare | - | - | - |
| valutazione-video.md | da verificare | - | - | - |

## Costi indicativi
Ogni post con titolo: 1-3 immagini (rigenera se il titolo esce sbagliato) + una lettura del testo. Carosello: 3 immagini + un testo.
