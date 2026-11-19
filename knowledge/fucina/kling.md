## Conoscenza: Kling 3.0 e Kling 4.0 (video da una foto)
Etichette: [verificato] = visto nei test; [fonte] = ricerca, non ancora provato; [ipotesi].

**Cosa abbiamo visto**
- Anello bijoux, Kling 3.0 Turbo 720p, 5 s, partendo dalla foto studio: stabile, 6 petali e colori invariati, push-in fluido. 1,5 crediti al secondo. [verificato: 10/11, prova 3]
- Stessa prova a 15 s: i primi 7 secondi frontali sono fedeli; dall'ottavo l'orbita laterale ridisegna la fascia (quella vera è larga e a segmenti elastici) e non torna al frontale. Si tiene il taglio da 7 s. [verificato: 10/11, prova 3c]
- Quindi: clip corte e frontali per i gioielli. [verificato: 10/11]

**Come scrivere**
- Quattro strati: soggetto con blocco identità, azione fisica con velocità, camera, scena/luce/stile. [fonte: report 13/11]
- La camera si scrive a parole: dolly in/out, pan, orbit, crane, push-in, "static locked-off camera", nella seconda o terza frase dopo l'azione. Non c'è un campo camera. [fonte: report 13/11]
- Livello di energia: "Subtle" per macro e gioielli, "Moderate" per capelli e stoffe, "Dynamic" solo per azione. Camera e soggetto allo stesso livello. Separare con "static background" o "static figure". [fonte: report 13/11]
- Gioiello: "turns slowly", "the background and the light stay still", foto di partenza su velluto scuro o bianco uniforme, senza luci bruciate sulle gemme. [fonte: report 13/11]
- Multi-inquadratura con `multi_prompt` (3.0 e 4.0). [fonte: report 13/11]
- Parole neutre: il filtro di Higgsfield ha bloccato un prompt con "torso" (16/11, vedi seedance.md); evitare elenchi di parti del corpo. [verificato: blocco 16/11; causa: ipotesi]

**Motion Control e keyframe** [fonte: ricerca 19/11]
- Kling 3.0 Motion Control copia movimento di mani e dita da un video guida vero (girato col telefono) su una foto ferma già approvata, purché tutte le dita e il braccio siano visibili e non coperti nel primo fotogramma. Utile per un gesto del polso con bracciali e anelli; alternativa a Genjutsu che parte dalla foto. Kling 3.0 ha anche le varianti Omni e Omni Edit.
- Kling 4.0: modalità "Frames" (fino a 10 keyframe) e "References" (fino a 15 riferimenti) non si possono unire. Frames per una rotazione complessa della mano o una borsa in cammino. [ipotesi]

**Limiti**
- Negative prompt e `cfg_scale` esistono solo su Kling 3.0 Pro via fal; non sulla CLI di Higgsfield né su Kling 4.0. Con la CLI i divieti vanno scritti nel prompt. [fonte: report 13/11, verificato sulla CLI]
- Kling 4.0 costa circa 2,6 volte Kling 3.0 in image-to-video: si usa se 3.0 deforma. Ha fino a 15 riferimenti e clip fino a 30 s. [fonte: guida Higgsfield 31/10; report 13/11]
- Non ha l'audio come Seedance. [fonte: guida Higgsfield 31/10]

**Da verificare [dubbio], non usare come fatti**
- Kling 4.0 con audio stereo nativo e editing video: lo dicono due ricerche del 19/11, contro la guida del 31/10. Controllare nell'interfaccia.
- Rapporto di costo Kling 4.0 / 3.0: le ricerche danno 1,5x, 2,7x o 3,3x (Kling 4.0 a 25 crediti per 5 s a 720p). Vale il costo mostrato prima di lanciare.
- Motion Control a 7-12 crediti per 5 s; nome "Kling 4.0 Flash".

Per approfondire: `Learn Higgsfield/docs/Prompting Avanzato Gioielleria e Moda.md` (sezione 4), `costi_test.csv` (prove 3 e 3c), `PROMPT_PLAYBOOK.md` (J3, A3).
