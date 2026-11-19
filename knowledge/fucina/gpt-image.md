## Conoscenza: GPT Image (gpt-image 2 / 2.5 / 2.6, Higgsfield `gpt_image_2_6`)
Etichette: [verificato] = visto nei test; [fonte] = ricerca, non ancora provato; [ipotesi].
- Sul gioiello è meno fedele di Seedream: ridisegna colori e texture e rimpicciolisce il pezzo nel quadro. [verificato: 10/11, stesso anello: voti 3,5-4 contro 4,5] Le tre ricerche del 19/11 lo indicano come il più fedele per gioielli e colore: non confermato, vince il nostro test.
- Sul ritocco di una camera ha ricomposto gli arredi (letto, finestra, specchio spostati): non usabile dove serve fedeltà. [verificato: 10/11]
- Bene su soggetti nuovi e schede personaggio: scheda personaggio e location sono venute credibili a 0,5 crediti. [verificato: 10/11, UGC asset]
- Il parametro `input_fidelity` non c'è più dalla versione 2: le immagini entrano già ad alta fedeltà. [fonte: report 13/11, OpenAI]
- Lati multipli di 16, rapporto massimo 3:1; sopra 2560x1440 è sperimentale. [fonte: report 13/11]
- Varianti 2.6 "sunburst" (più dettaglio, più lenta) e "flare" (più veloce). [fonte: report 13/11, catalogo Higgsfield]
- Struttura del prompt: fedeltà al pezzo per prima, poi scena, inquadratura, luce, divieti. [fonte: guida Higgsfield 31/10]
- Fino a 16 riferimenti, fondo trasparente (PNG), modifica locale; utile per testo leggibile sull'immagine. [fonte: ricerca 19/11] Logo grande e frontale nel primo fotogramma di un video (i video rendono male i loghi piccoli). [ipotesi]
**Da verificare [dubbio]**: costi dati dalle ricerche (1-2 crediti, 2,75 a 2K High) contro i nostri 0,5 crediti a immagine (verificato 10/11).
Per approfondire: `Learn Higgsfield/docs/Prompting Avanzato Gioielleria e Moda.md` (sezione 3), `costi_test.csv` (prove 1, 1b, 2, 2b).
