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

**Aurora e il pezzo nelle foto: regole dalla ricerca A del 19/11** [fonte: Higgsfield, ByteDance, test Runware; non ancora provato da noi]
- Da 2 a 4 riferimenti in tutto, mai di più (con 10-16 il colore dello smalto o del ricamo "cola" su trucco, occhi e abiti). Ordine fisso: Image 1 = volto neutro di Aurora senza gioielli; Image 2 = foto vera del pezzo su fondo neutro; Image 3 solo se serve = macro di ricamo o pietra.
- Con @Aurora come Element la numerazione scala di uno: Image 1 diventa il pezzo.
- Nel prompt: stesso paragrafo di identità riscritto uguale ogni volta, e confini espliciti: "Take ONLY Aurora's face, skin and hair from Image 1; take ONLY the piece from Image 2; zero colour or texture blending". Cambiare una sola cosa per volta tra due foto della stessa serie.
- Ripartire sempre dal file master, mai da una foto AI già generata. Fogli con più viste in un solo file no: il modello le legge come persone diverse.
- Il volto deve occupare almeno il 20-25% del quadro: nei campi larghi e nei profili l'identità cede per prima. Senza identità addestrata il volto cambia entro 3-7 foto.
- Dove funziona @Aurora: Nano Banana Pro e GPT Image 2.6 (solo PNG o GIF, non SVG). Su Seedream il tag non è confermato: ritratti master come Image 1. Soul ID da solo non si usa dentro Seedream e GPT Image [fonte: documentazione Soul ID, non trovato].
- Serie lunghe o campagne: prima posa e luogo con Soul 2.0 + Soul ID, poi la foto approvata va con la foto vera del pezzo in Nano Banana Pro, Seedream 5.5 o GPT Image 2.6 Sunburst.
- Sguardo: GPT Image guarda sempre in camera, per pose spontanee Seedream 5.5. Lentiggini e pelle "illustrata" su GPT: scrivere "real photograph, authentic skin texture".
- Etichetta AI: la norma europea sulle immagini sintetiche realistiche vale dal 2 agosto 2026 [dubbio: fonte un blog, da verificare con il consulente; vedi `docs/impegni-legali.md`].

Per approfondire: `Learn Higgsfield/STATUS.md`, `docs/archivio/handoff/handoff-2026-11-20.md`, `PIANO_DATASET_MODELLA.md`, `GENJUTSU_PROVE_E_RICETTA.md`.
