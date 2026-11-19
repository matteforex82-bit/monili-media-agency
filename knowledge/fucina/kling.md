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

**Kling 4.0: come si usa** [fonte: guida ufficiale Kling 04/11, test ChatCut 15/11, ricerca B 19/11; non provato da noi]
- Versioni su Higgsfield: Kling 4.0 (720p e 1080p, 3-30 s), Kling 4.0 Flash (solo bozze 720p, solo Start Frame), Kling 3.0 e Turbo. Tre modi: References (fino a 15 riferimenti, @Image1, Elements), Frames (fino a 10 keyframe) e Edit. References e Frames non si uniscono nella stessa richiesta.
- Apertura obbligata: "One continuous 5-second shot with no cuts." Senza, lo storyboard automatico inserisce tagli (basta scrivere "medium shot, then close-up"). Il cambio di distanza si scrive "slow push-in".
- Divieti: la guida ufficiale dice che le negazioni sul visivo aumentano gli errori; ammette solo "No subtitles. No background music." Il resto in positivo: "plain unlabelled plaster wall", "five natural relaxed fingers", "three-quarter profile". "No text" non toglie le scritte dipinte sugli oggetti di sfondo.
- Start Frame: dichiarare cosa resta uguale ("@Image1 is the first frame ... keep the exact band width, bezel and stone colour unchanged") e descrivere solo il movimento, senza ridescrivere la foto. Tempi a finestre (0-3s:, 3-6s:) e "at a steady natural pace": clip lunghe con un'azione breve vanno al rallentatore.
- Aurora + pezzo in References: aprire con "EXACT 1 HUMAN CHARACTER — NO DUPLICATES", assegnare un compito a ogni @ImageN e fissare gli sfondi con "frame-left / frame-right". È anche il piano B quando Seedance rifiuta il volto.
- Giro attorno a un pezzo (borsa): Frames con 4 keyframe veri (fronte 0 s, fianco 3 s, retro 5 s, fronte 8 s); non 10 keyframe a griglia fissa, non cambiare più di 1-2 variabili tra due keyframe. Da una sola foto, arco di 40 gradi al massimo.
- Audio stereo sempre acceso, senza interruttore: toglierlo in montaggio o sfumare 4-6 fotogrammi tra due clip. Niente aggettivi astratti ("premium look"): luce, grana, materiale.

**Limiti**
- Negative prompt e `cfg_scale` esistono solo su Kling 3.0 Pro via fal; non sulla CLI di Higgsfield né su Kling 4.0. Con la CLI i divieti vanno scritti nel prompt. [fonte: report 13/11, verificato sulla CLI]
- Kling 4.0 costa più di Kling 3.0 (listino 30/10: 10 s a 720p = 27,5 crediti, a 1080p = 40; il nostro Kling 3.0 Turbo 720p era 1,5 al secondo): si usa se 3.0 deforma o per Aurora. Kling 4.0 è escluso dall'Unlimited del sito, Kling 3.0 no. [fonte: ricerca B 19/11]
- Lo slug CLI di Kling 4.0 non è documentato: controllare con `higgsfield model list --video`.

**Da verificare [dubbio], non usare come fatti**
- Il rapporto di costo: le ricerche danno da 1,5x a 3,3x. Vale il costo mostrato prima di lanciare.
- Motion Control a 7-12 crediti per 5 s. Gli esempi pronti per ogni pezzo sono in `prompt-video-esempi.md`.

Per approfondire: `Learn Higgsfield/docs/Prompting Avanzato Gioielleria e Moda.md` (sezione 4), `costi_test.csv` (prove 3 e 3c), `PROMPT_PLAYBOOK.md` (J3, A3).
