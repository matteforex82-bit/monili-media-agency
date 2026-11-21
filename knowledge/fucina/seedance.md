## Conoscenza: Seedance 2.5 (video da una foto; Higgsfield `seedance_2_5`)
Etichette: [verificato] = visto nei test di Matteo; [fonte] = ricerca (report 13/11 rivisto; ricerca B 19/11), non ancora provato; [ipotesi].

**Impostazioni, costi, varianti**
- Formato 9:16. Provare a 480p, definitivo a 1080p: l'uscita normale è 854x480 ed è morbida sul sito desktop. [verificato: 17/11, hero; 10/11]
- Costi con Plus: 3 crediti al secondo a 480p, 7 a 720p; 8 s con voce a 480p = 24. Controllare il costo mostrato prima di lanciare. [verificato: 10/11] 1080p = 16 al secondo (10 s = 160). [fonte: listino Higgsfield 30/10]
- **Seedance 2.5 Flash**: bozze a 480p o 720p, 2-3 volte più veloce e circa un terzo in meno; regge i movimenti lenti, salta la fisica veloce. **2.5 Edit** / "Draw to Edit": corregge una sola zona (maglia, orecchino, cartellino) senza rigenerare la clip. Prima la bozza, poi il finale solo del take scelto. 4K solo sul sito. [fonte: ricerca B 19/11]
- Due modalità separate: **primo fotogramma** (una foto) per anelli, orecchini, collane, bracciali, capi, borse; **Omni Reference** (@Image1, @Image2, fino a 50 riferimenti, ma meglio 2-4) per Aurora + pezzo e per più viste del pezzo. Con più file il volto si diluisce (visto su Seedream, 16/11). [fonte: ricerca B 19/11]
- "Unlimited" vale solo sul sito, non via CLI o MCP. [verificato: 10/11, 16/11] Con la CLI `--draft true` 5 s a 1080p passano da 80 a 15 crediti. [fonte: report 13/11] Durata 4-30 s.

**Quanto dura un pezzo fedele**
- Nei gioielli la forma comincia a cambiare dopo 7-8 secondi: clip da 5-6 s, 9 s solo per il multi-shot. [verificato: 10/11]
- 4 s a 480p su un anello: stabile, scintilla visibile nel primo fotogramma. [verificato: 10/11, prova 3b]
- Ogni inquadratura di un Reel lungo richiama il capo dai riferimenti. [ipotesi: esito di T7 non registrato]

**Come scrivere**
- Fedeltà per prima, poi una sola azione, un solo movimento di camera lento, luce, divieti. "One continuous shot, no cuts." [fonte: guida Higgsfield 31/10; report 13/11]
- Con riferimenti: ogni immagine ha un ruolo e cosa ignorare ("@Image1 defines Aurora's face and hair only; ignore its outfit"), mai "@Images 1 through 4". Con una sola foto di partenza niente @Image: dichiarare cosa resta uguale ("exact band shape, stone cut, stone count"), senza ridescriverla. [fonte: ricerca B 19/11]
- Blocchi: GLOBAL STYLE, ACTIVE REFERENCES, SCENE, FIRST FRAME AND BLOCKING, TIMED BEATS (secondi interi: 0-2 s, 2-5 s), CAMERA, CONTINUITY, AUDIO, CONSTRAINTS. Scheletro unico in `struttura-prompt.md`. [fonte: ricerca B 19/11]
- Camera: evento, movimento, arrivo ("as the light reaches the stone, one slow push-in of 6 cm, settling in a macro hold"); "slow physical dolly-in, not optical zoom"; orbita max 30°. Mai "fast" (sfoca e deforma), mai "cinematic" o "music" con l'audio acceso. [fonte: ricerca 19/11]
- Più viste del pezzo: file separati, mai collage, più "All three images define one single ring. There is only ever one ring in the finished video." Niente testo scritto sulle immagini. Ultimo fotogramma nello stesso formato del primo, altrimenti si stira. 360° da una sola foto: no (il retro è inventato); con una foto, arco max 45°. [fonte: ricerca B 19/11]
- I verbi "edit, replace, change to, remove" attivano la modalità di modifica e bloccano formato e durata: solo in Seedance 2.5 Edit. [fonte: ricerca B 19/11]
- 3-5 vincoli concreti in coda con un partner positivo ("plain unlabelled stone, no logos, no extra hands"); liste vaghe sono ignorate. L'audio si spegne dal toggle. Deriva di volto o ricamo tra il quinto e l'ottavo secondo: 5-8 s e 2-3 ancore ripetute in CONTINUITY. [fonte: ricerca B 19/11]
- Se parti da una foto di un ambiente il video la tiene come sfondo fermo "appiccicato": chiedere persone, luce e piccoli movimenti vivi. [verificato: 17/11]
- Lato libero per il titolo del sito: dirlo; in montaggio si può specchiare con ffmpeg. [verificato: 17/11]
- Mani e oggetti sono il punto debole: gesti semplici; mai allacciare una chiusura o infilare un anello, ma partire dal pezzo già indossato; stato iniziale e finale della mano. [fonte: guida Higgsfield 31/10; ricerca 19/11]
- Il testo a schermo esce morbido: scritte e prezzi in montaggio. Video muto, audio dopo: l'italiano parlato ha pronuncia imperfetta ("soffici" diventava "soffidi"). [verificato: 10/11, prova 5]

**Persone e filtri**
- Il filtro biometrico di ByteDance può rifiutare un ritratto fotorealistico come riferimento (in un test esterno 4 volte su 5): dopo tre rifiuti è il filtro. Alternative: @Aurora come Element, foto di Aurora già vestita da animare, o la scena su Kling 4.0. [fonte: ricerca B 19/11]
- Con la modella addestrata la coerenza di volto e location è buona (voto 4). [verificato: 10/11, prove 5 e 8]
- Un prompt da 15 s con cinque inquadrature ("torso", "zips ... under the jacket", primi piani sul corpo) è stato bloccato dal filtro del sito; causa non confermata. [verificato: blocco 16/11] Scrivere "at the neckline", "turns slightly". [ipotesi]
- Nella foto del capo togliere cartellini e gruccia e scrivere "no hanger". [verificato: 10/11; 15/11]
- Con primo e ultimo fotogramma, l'ultimo si ricava dal primo modificandolo. [fonte: report 13/11] Un video di riferimento dà uno sconto di circa il 40%. [fonte: report 13/11]

**Da verificare [dubbio]**: errore E005 con volto troppo stretto; "High Bitrate" gratis; 4K nel nostro account; Draw to Edit a 66 crediti per 10 s. Ricerca dice 4-8 s per l'aggancio: restano 5-6 s. Esempi per ogni pezzo: `prompt-video-esempi.md`.
Per approfondire: `Learn Higgsfield/PROVE_REEL_SEEDANCE.md` (prompt T1-T7), `costi_test.csv`, `knowledge/higgsfield_video_guida.md`.
