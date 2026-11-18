## Riferimento: la modella fissa Monili-Aurora e lo slot @MODELLA
**Deciso il 18/11/2026:** nei prompt delle foto indossate e delle scene video la donna si scrive sempre come `@MODELLA`. Chi è (Aurora o un'altra modella) lo sceglie Matteo a mano quando genera su Higgsfield, sostituendo `@MODELLA` con il tag giusto. La Fucina non descrive il volto. Per far descrivere una donna all'AI c'è l'opzione "Descrizione inventata" nella schermata.
Dal 18/11/2026 (sera) Aurora è la testimonial fissa del negozio: anche il flusso automatico (Scheda pezzo, Reel) usa la sua descrizione fissa (`skills/_base/donne.md`, sezione Testimonial) invece di inventare una donna per pezzo.

**Cos'è Aurora**
- Soul ID `Monili-Aurora`, addestrato su 40 immagini (dataset in `MoniliStorage\Dataset_Modella_Monili`). Volto: sopracciglia scure marcate, occhi verde-nocciola, lentiggini chiare, mezzo sorriso leggermente asimmetrico, capelli castani mossi alle spalle con riga di lato, senza frangia. [verificato: STATUS e HANDOFF, 14-16/11]
- Nel campo prompt di Higgsfield la modella si richiama scrivendo `@` e scegliendola dal menu. [verificato: PROVE_REEL_SEEDANCE, 15/11]
- Requisiti ufficiali Higgsfield per un Soul ID: 20-80 foto, almeno un corpo intero, luce morbida e coerente, niente pose ripetute. [fonte: pagina Higgsfield, 11/11]

**Quando sostituisci @MODELLA con una modella addestrata**
- Il tag può richiamare una foto vestita del dataset (t-shirt nera e jeans) e ricopiarla: la frase "use only her face and hair, ignore her clothes" è già nel prompt. [verificato: 16/11]
- Soul 2.0 con una foto allegata fa sparire il campo prompt: non si possono unire foto, prompt e personaggio. Per foto più prompt usare Seedream o Nano Banana. [verificato: 16/11]
- Il retro del capo e gambe e scarpe senza riferimento vengono inventati: allegare le foto vere. [verificato: 16/11]
- Contenuti con la modella AI: da dichiarare AI se pubblicati. [regola del progetto]

**Come si fa vestire un capo vero (ricetta v0, non ancora validata)**
1. Foto vere del capo (davanti, dietro, intera) e un dettaglio.
2. Foto intera con Seedream 5.0: riferimenti = capo vero e volto e capelli della modella; capo descritto a parole; pantaloni e stivali inclusi.
3. Controllo a 100% contro la foto vera, poi Seedance o Genjutsu con quella foto come primo fotogramma.
[fonte: GENJUTSU_PROVE_E_RICETTA.md; Test 1 e 2 ancora in corso al 16/11]

Per approfondire: `Learn Higgsfield/STATUS.md`, `HANDOFF.md`, `PIANO_DATASET_MODELLA.md`, `GENJUTSU_PROVE_E_RICETTA.md`.
