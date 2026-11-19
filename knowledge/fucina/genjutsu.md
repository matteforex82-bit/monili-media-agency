## Conoscenza: Genjutsu (Higgsfield, video da un altro video)
Etichette: [verificato] = visto nei test di Matteo; [fonte] = ricerca, non ancora provato; [ipotesi].
Cos'è: non crea video da zero, rifà un video esistente (4-30 s). Tre usi: Motion Transfer (prende solo movimento, tempi e camera e ricostruisce persona, abiti e scena dalle immagini), Object Swap (cambia un solo elemento), Restyle. [fonte: report 13/11]

**Cosa funziona**
- Motion Transfer, clip da 14 s a 480p, tre riferimenti (due frame con la giacca e il volto della modella): volto molto buono e coerente, giacca fedele, movimento fluido. [verificato: 16/11, esito parziale]
- Il Lite sostituisce il capo e il soggetto ma tiene lo sfondo del video, non quello dell'immagine. Sul video di strada: giacca fedele, cammino credibile, voti 4 e 3,5. [verificato: 10/11, prove 9 e 10]

**Cosa NON rifare**
- Object Swap per cambiare l'identità di una persona: due prove, il volto resta quello originale. [verificato: 15/11 e 16/11] Ricerca 19/11 lo propone per correggere il volto: non confermato, vince il nostro test.
- Style: ridisegna tutto il video in uno stile. [verificato: 14-15/11]
- Motion Transfer senza riferimenti di gambe e scarpe: inventa una gamba bianca e una scarpa in più; senza foto del retro inventa il retro del capo. Serve una foto intera già vestita, con pantaloni e stivali. [verificato: 16/11]
- Clip con il telefono davanti al viso o con più persone: il volto non si legge. Clip di 4-5 s, un solo taglio, volto frontale nel primo fotogramma. [verificato: 16/11; scelta del clip: ricetta v0 da validare]
- Prove lunghe: 14 s costano molto; provare a 480p e 4-5 s (Lite 4 crediti; Objects swap Standard 4 s = 12 crediti). [verificato: 10/11 e 16/11]
- `replace_object` costava 63 crediti: fuori budget. [verificato: 10/11]

**Prompt di movimento (ricetta v0, da validare)**: "The person in the video is replaced by the character in image 1, wearing exactly the outfit shown in image 1. Keep the motion, pacing and camera of the video. One person only, both legs wear the same trousers and boots, no white clothing, no sneakers." [fonte: GENJUTSU_PROVE_E_RICETTA.md, non ancora validata]
- Occlusioni rapide, piccoli loghi, bracciali e fibbie danno artefatti. [fonte: report 13/11] Per i pezzi sottili: "crisp fast shutter, minimal motion blur". [fonte: ricerca 19/11]
- Video di terzi: solo prova privata; serve il consenso scritto prima di pubblicare e il contenuto va dichiarato AI. [regola del progetto]
- Parole del corpo: il filtro di Higgsfield ha bloccato un prompt con "torso" (16/11, vedi seedance.md): scrivere parole neutre. [verificato: blocco 16/11; causa: ipotesi]

**Quando sì e quando no, per tipo di pezzo** [fonte: ricerca B 19/11; nessun test pubblico su gioielli sostituiti in movimento]
- Anelli, orecchini, collane, bracciali: no, né da foto né come sostituzione di un gioiello piccolo (occlusioni, scala, catenine). Si usa Seedance o Kling dalla foto; oppure si filma il gioiello vero addosso e Genjutsu cambia solo il resto.
- Giacche, gilet, borse: Object Swap solo se nel video la persona porta un oggetto di sagoma e misura simili (un capo "controfigura") e la foto del pezzo è dallo stesso angolo su grigio neutro 18%. Sul ricamo fitto e sulle fibbie non ci sono test: provare a 480p.
- Giro di camera o foto ferma: no, Genjutsu rifà un video già girato.
- **Aurora su una ripresa vera del pezzo**: la ricerca propone Object Swap per cambiare solo il volto. **Il nostro test dice il contrario** (il volto resta quello originale, 15 e 16/11): vale il test. Per cambiare la persona, Motion Transfer con foto intera già vestita. [verificato: 15-16/11]
- Lite: solo clip sotto 15 s, senza tagli e senza oggetti toccati dalle mani (può allungare 10,1 s a 11 s e sfasare audio e gesto); per le mani, Standard. Soggetto fermo nel video = effetto manichino: movimento continuo e morbido. Tessuto: in un piegamento profondo Standard ha irrigidito una gonna a pieghe.
- Massimo 2 tentativi sulla stessa impostazione, poi cambiare modalità o rigirare il video. Sorgente tra 5 e 29 s, mai 30,0 s. Prompt: dire voce per voce cosa resta uguale da @Video1 (capelli, orecchini, sfondo) e chiudere con "Avoid: halos, double edges, extra fingers, camera cuts, added text" (nessun campo negativo).

**Limiti e costi** [fonte: ricerca 19/11]
- Video sorgente di almeno 409.600 pixel per fotogramma: un'uscita Seedance 854x480 (409.920) è al limite esatto. Meglio 1080x1920, 30 fps.
- Fino a 30 immagini di riferimento (Lite 10); uscita fino a 1080p.
- Object Swap 15 s a 480p = 48 crediti (circa 3,2 al secondo, coerente con i nostri 12 per 4 s), 720p = 112, 1080p = 320; Motion Transfer 480p = 45, 720p = 105, 1080p = 300; Lite 720p = 96, 1080p = 192 [fonte: tabella Higgsfield 02/11]. Prima 480p, mai subito 1080p. Su Lite il tetto reale è 15 s.

**Object Swap di un oggetto su una ripresa col telefono** [fonte: ricerca 19/11; sugli oggetti non ancora provato da noi]
- Girare 4-15 s in 9:16 col telefono a 1x o 2x (mai 0,5x), esposizione e fuoco bloccati, luce morbida costante, camera semplice. La donna porta un oggetto segnaposto di forma e misura simili; capelli, maniche e dita non lo coprono. 3-10 foto nitide del pezzo vero (fronte, tre quarti, macro) con luce simile al video.
- Prompt: "Replace only the black handbag held in her right hand with the structured cognac pebbled-leather handbag from the references. Keep the woman's face, fingers, outfit, movement, camera motion, lighting and the original background 100% unchanged."
- Controllare: contatto mano-manico, ombre, riflessi della minuteria, punto in cui il pezzo tocca il corpo.

**Da verificare [dubbio]**: la ricerca Perplexity dà Genjutsu Standard a 35-100 crediti per 5 s, contro i nostri 12 per 4 s (verificato): non usare.

Per approfondire: `Learn Higgsfield/GENJUTSU_PROVE_E_RICETTA.md` (registro prove e "da non rifare"), `costi_test.csv` (prove 9 e 10).
