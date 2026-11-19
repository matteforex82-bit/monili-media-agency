## Conoscenza: Seedance 2.5 (video da una foto; Higgsfield `seedance_2_5`)
Etichette: [verificato] = visto nei test di Matteo; [fonte] = ricerca (report 13/11 rivisto), non ancora provato; [ipotesi].

**Impostazioni e costi**
- Formato 9:16 per i Reel. Provare a 480p, definitivo a 1080p: l'uscita normale è 854x480 ed è morbida sul sito desktop. [verificato: 17/11, clip della hero; 10/11, 480x854]
- Costi a crediti, con Plus: 3 al secondo a 480p, 7 al secondo a 720p; un video con voce di 8 s a 480p = 24 crediti. Controllare sempre il costo mostrato prima di lanciare. [verificato: 10/11] 1080p = 16 al secondo. [fonte: ricerca 19/11, coerente con 80 crediti per 5 s]
- Fino a 50 riferimenti, ma meglio pochi e distinti: con troppi il volto si diluisce (visto su Seedream, 16/11). [fonte: ricerca 19/11]
- Seedance 2.5 Edit / "Draw to Edit": corregge una sola zona (maglia rotta, orecchino, cartellino) senza rigenerare la clip. [fonte: ricerca 19/11]
- Le generazioni "Unlimited" valgono solo sul sito higgsfield.ai, non via CLI o MCP. [verificato: 10/11 e 16/11]
- Con la CLI `--draft true` una clip da 5 s a 1080p passa da 80 a 15 crediti. [fonte: report 13/11, provato in locale con `generate cost`]
- Durata 4-30 s in un solo passaggio. [fonte: catalogo Higgsfield]

**Quanto dura un pezzo fedele**
- Nei gioielli la forma comincia a cambiare dopo 7-8 secondi: clip da 5-6 s, 9 s solo per il multi-shot. [verificato: 10/11, prove Kling e Seedance]
- 4 s a 480p su un anello: stabile, scintilla visibile nel primo fotogramma. [verificato: 10/11, prova 3b]
- Ogni inquadratura di un Reel lungo richiama il capo dai riferimenti, perché la forma tende a cambiare. [ipotesi: impostazione del test 15/11, esito di T7 non ancora registrato]

**Come scrivere**
- Fedeltà per prima, poi una sola azione, un solo movimento di camera lento ("push-in", "static locked-off camera"), poi la luce, poi i divieti. "One continuous shot, no cuts." [fonte: guida Higgsfield 31/10; report 13/11]
- Due modi. Con riferimenti (`omni_reference`) ogni immagine ha un ruolo scritto e un nome ("@Image1 defines only the ring silhouette"), mai "@Images 1 through 4". Con una sola foto di partenza (image-to-video) niente @Image: descrivi il soggetto in chiaro. [fonte: report 13/11, guide di terzi]
- Nei Reel a più inquadrature scandire il tempo con finestre (0-3 s, 3-7 s); al massimo 2-4 micro-espressioni sul volto. [fonte: report 13/11]
- Se parti da una foto di un ambiente il video la tiene come sfondo fermo "appiccicato": chiedere esplicitamente persone, luce e piccoli movimenti vivi. [verificato: 17/11, clip videochiamata]
- Se un lato deve restare libero per il titolo del sito, dirlo: la prima versione metteva il soggetto sotto il titolo. In montaggio si può specchiare una ripresa con ffmpeg. [verificato: 17/11, hero]
- Con riferimenti, un solo blocco di testo a sezioni: "SCENE: ... REFERENCES: @Image1 [face and hair only], @Image2 [exact product, 100% unchanged] TIMING: [0-3 s: subtle micro-motion] [3-6 s: settle] MATERIAL PHYSICS: ... CAMERA: ... LIGHT: ... AUDIO: No music, no dialogue. LOCKS: ..." [fonte: ricerca 19/11]
- "Slow physical dolly-in, not optical zoom"; orbita max 30°. [fonte: ricerca 19/11] Gradi espliciti: "the wrist rotates slowly by about 15 degrees". [ipotesi]
- Mani e oggetti sono il punto debole: gesti semplici (la mano entra, si posa, si gira piano). [fonte: guida Higgsfield 31/10, §5b] Mai allacciare una chiusura o infilare un anello: partire dal pezzo già indossato. [fonte: ricerca 19/11]
- Il testo a schermo esce morbido: scritte e prezzi in montaggio. [fonte: ricerca 19/11]
- Video muto: l'audio si mette dopo. In un UGC con voce l'italiano ha pronuncia imperfetta ("soffici" diventava "soffidi"). [verificato: 10/11, prova 5]

**Persone e filtri**
- Con la modella addestrata la coerenza di volto e location è buona (voto 4), come nei test del 10/11 con volti Soul 2.0. [verificato: 10/11, prove 5 e 8]
- Un prompt da 15 s con cinque inquadrature (giacca, "torso", "zips ... under the jacket", primi piani sul corpo) è stato bloccato dal filtro del sito. La causa non è confermata: usare parole neutre e riprovare. [verificato: blocco il 16/11; causa: ipotesi] Evitare "torso", "chest", "bare"; scrivere "at the neckline", "turns slightly". [ipotesi]
- Nella foto del capo togliere cartellini e gruccia, e scrivere "no hanger": a volte compare un cartellino sul bavero. [verificato: 10/11, prova 8; 15/11, T3]
- Con primo e ultimo fotogramma, l'ultimo si ricava dal primo modificandolo, altrimenti gioielli e capelli cambiano a metà clip. [fonte: report 13/11]
- Un video di riferimento porta uno sconto di circa il 40% perché vincola il movimento. [fonte: report 13/11, fal]

**Da verificare [dubbio]**: errore E005 con riferimento del volto troppo stretto; "High Bitrate" gratis; nomi "Seedance 2.5 Flash/4K"; Draw to Edit a 66 crediti per 10 s. Ricerca dice 4-8 s per l'aggancio, non confermato: restano 5-6 s.
Per approfondire: `Learn Higgsfield/PROVE_REEL_SEEDANCE.md` (prompt T1-T7), `costi_test.csv`, `docs/Prompting Avanzato Gioielleria e Moda.md` (sezione 6), `knowledge/higgsfield_video_guida.md`.
