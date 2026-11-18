## Conoscenza: FLUX (FLUX.2 Pro/Flex/Max/Dev/Klein, FLUX.1 Kontext)
Etichette: [verificato] = visto nei test; [fonte] = ricerca, non ancora provato; [ipotesi].
Stato: sulla CLI di Higgsfield c'è come "Flux 2" e "Flux Kontext Max", ma solo su richiesta; la chiave `FAL_KEY` non è impostata. Non è un modello di lavoro per ora.
- Provato sul ritocco di una camera: ricompone e inventa oggetti (un lampadario) e costa 2 crediti contro 0,5 di Seedream. [verificato: 10/11]
- Non ha negative prompt; le parentesi di peso stile SD sono ignorate. [fonte: report 13/11]
- L'ordine conta: i primi token pesano di più. Soggetto e materiale, azione, ambiente, luce, camera, in 30-80 parole. [fonte: report 13/11]
- Capisce prompt JSON e codici colore HEX esatti: utile per colori di brand o smalti. [fonte: report 13/11]
- In modifica non descrivere tutta la scena: scrivere comandi come "Change the blazer colour to #1D3557, remove reflections on the sapphire, maintain face and posture". [fonte: report 13/11]
- Tende a scaldare i bianchi e l'argento: aggiungere "cool neutral daylight white balance". Su Flex e Kontext tenere la guidance tra 2.5 e 3.5. [fonte: report 13/11, nodi e community]
- Mantiene i volti meno bene di altri modelli. [fonte: report 13/11]
Per approfondire: `Learn Higgsfield/docs/Prompting Avanzato Gioielleria e Moda.md` (sezione 2), `costi_test.csv` (prova 1b).
